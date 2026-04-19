from django.shortcuts import render, redirect, get_object_or_404
from cart.models import *
from address.models import Address
from decimal import Decimal
from datetime import timedelta
from order.models import *
from django.contrib import messages
from django.db.models import F
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.conf import settings
import razorpay
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
def _staff_or_blocked_redirect(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and getattr(request.user, 'is_block', False):
        return redirect('user_app:user_logout')
    return None
def cancel_failed_payment_order(order):
    order.order_status = 'canceled'
    order.cancellation_reason = 'Maximum payment attempts exceeded'
    order.save()
    for item in order.items.all():
        item.varient.stock = F('stock') + item.quantity
        item.varient.save()
        item.product.sold_count = F('sold_count') - item.quantity
        item.product.save()
@login_required
@never_cache
def order_complete(request):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard

    if request.method != 'POST':
        return redirect('user_app:index')

    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart could not be found.')
        return redirect('cart_app:view_cart')
    cart_id = cart.id
    cart_items = cart.items.select_related('product', 'varient').all()
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_app:view_cart')
    address_id = request.session.get('checkout_address_id')
    if address_id:
        address = get_object_or_404(Address, id=address_id, user=user)
    else:
        try:
            address = Address.objects.get(user=user, default=True)
        except Address.DoesNotExist:
            messages.error(request, 'No delivery address found. Please add an address.')
            return redirect('cart_app:checkout', cart_id=cart_id)
        except Address.MultipleObjectsReturned:
            address = Address.objects.filter(user=user, default=True).first()
    coupon_code = request.session.get('coupon')
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupen.objects.get(code=coupon_code)
        except Coupen.DoesNotExist:
            request.session['cart_total_with_discount'] = request.session.get('total_without_coupon')
            request.session.pop('total_without_coupon', None)
            messages.error(request, 'The coupon you applied is no longer valid.')
            return redirect('cart_app:view_cart')
    discount = request.session.get('cart_total_with_discount')
    if discount is None:
        messages.error(request, 'Session expired. Please go through checkout again.')
        return redirect('cart_app:view_cart')
    payment_method = request.POST.get('payment_method')
    if payment_method not in ('cod', 'wallet', 'razorpay'):
        messages.error(request, 'Invalid payment method selected.')
        return redirect('cart_app:checkout', cart_id=cart_id)
    if payment_method == 'cod' and float(discount) > 1000:
        messages.error(request, 'Cash on Delivery is not available for orders above ₹1000.')
        return redirect('cart_app:checkout', cart_id=cart_id)
    try:
        with transaction.atomic():
            delivery_date = timezone.now() + timedelta(days=7)
            order = Order.objects.create(
                user=user,
                order_status='confirmed',
                delivery_date=delivery_date,
                address=address,
                discount=discount,
                coupons=coupon_obj,
            )
            OrderAddress.objects.create(
                order=order,
                landmark=getattr(address, 'landmark', ''),
                postal_code=address.postal_code,
                phone=address.phone,
                street_address=address.street_address,
                alternative_phone=getattr(address, 'alternative_phone', ''),
            )
            for item in cart_items:
                if item.varient.stock < item.quantity:
                    raise ValueError(
                        f'Insufficient stock for "{item.product.product_name}" '
                        f'({item.varient.stock} available).'
                    )
                OrderItems.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    item_price=item.product.discount_price,
                    price=item.quantity * Decimal(str(item.product.discount_price)),
                    varient=item.varient,
                )
                item.varient.stock = F('stock') - item.quantity
                item.varient.save()
                item.product.sold_count = F('sold_count') + item.quantity
                item.product.save()
            cart_items.delete()
            for key in ('checkout_address_id', 'coupon', 'cart_total_with_discount', 'total_without_coupon'):
                request.session.pop(key, None)
            if payment_method == 'cod':
                Payment.objects.create(
                    order=order,
                    total_price=discount,
                    payment_method='cod',
                    payment_status='success',
                )
                return redirect('order_app:complete')
            elif payment_method == 'wallet':
                wallet, _ = Wallet.objects.get_or_create(user=user)
                if wallet.balance < Decimal(str(discount)):
                    raise ValueError('Insufficient wallet balance.')
                wallet.balance = F('balance') - Decimal(str(discount))
                wallet.save()
                WalletTransation.objects.create(
                    wallet=wallet,
                    transaction_type='debited',
                    amount=discount,
                )
                Payment.objects.create(
                    order=order,
                    total_price=discount,
                    payment_method='wallet',
                    payment_status='success',
                )
                return redirect('order_app:complete')
            elif payment_method == 'razorpay':
                razorpay_amount = int(float(discount) * 100)
                razorpay_order = razorpay_client.order.create({
                    'amount': razorpay_amount,
                    'currency': 'INR',
                    'payment_capture': '1',
                })
                Payment.objects.create(
                    order=order,
                    total_price=discount,
                    payment_method='razorpay',
                    payment_status='pending',
                    razorpay_order_id=razorpay_order['id'],
                    payment_attempts=1,
                )
                order.order_status = 'payment_pending'
                order.save()
                return render(request, 'user/razorpay_payment.html', {
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                    'razorpay_amount': razorpay_amount,
                    'order_id': order.id,
                    'attempts_remaining': 1,
                })
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart_app:checkout', cart_id=cart_id)
    except razorpay.errors.BadRequestError as e:
        messages.error(request, f'Payment gateway error: {str(e)}')
        return redirect('cart_app:checkout', cart_id=cart_id)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        messages.error(request, f'DEBUG ERROR: {str(e)}')
        # Also print to terminal
        print("=== ORDER ERROR ===")
        print(error_details)
        print("==================")
        return redirect('cart_app:checkout', cart_id=cart_id)
        
def retry_payment(request, order_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        try:
            payment = Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found for this order.')
            return redirect('customer_app:item_order', id=order_id)
        if payment.payment_attempts >= 2:
            cancel_failed_payment_order(order)
            messages.error(request, 'Maximum payment attempts reached. Order has been cancelled.')
            return redirect('customer_app:item_order', id=order_id)
        if payment.payment_status not in ('pending', 'failed'):
            messages.error(request, 'This order cannot be retried for payment.')
            return redirect('customer_app:item_order', id=order_id)
        razorpay_amount = int(float(order.discount) * 100)
        razorpay_order = razorpay_client.order.create({
            'amount': razorpay_amount,
            'currency': 'INR',
            'payment_capture': '1',
        })
        payment.payment_attempts += 1
        payment.razorpay_order_id = razorpay_order['id']
        payment.payment_status = 'pending'
        payment.save()
        return render(request, 'user/razorpay_payment.html', {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': razorpay_amount,
            'order_id': order.id,
            'attempts_remaining': 2 - payment.payment_attempts,
        })
    except razorpay.errors.BadRequestError as e:
        messages.error(request, f'Payment gateway error: {str(e)}')
        return redirect('customer_app:item_order', id=order_id)
    except Exception as e:
        messages.error(request, f'Error processing payment retry. Please try again.')
        return redirect('customer_app:item_order', id=order_id)
@csrf_exempt
def verify_payment(request):
    if request.method != 'POST':
        return HttpResponse('Invalid Request', status=400)
    payment_id = request.POST.get('razorpay_payment_id')
    order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')
    if not all([payment_id, order_id, signature]):
        messages.error(request, 'Incomplete payment data received.')
        return redirect('cart_app:checkout')
    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found.')
        return redirect('cart_app:checkout')
    order = payment.order
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        })
        payment.payment_status = 'success'
        payment.razorpay_payment_id = payment_id
        payment.save()
        order.order_status = 'confirmed'
        order.save()
        return redirect('order_app:complete')
    except razorpay.errors.SignatureVerificationError:
        payment.payment_status = 'failed'
        payment.save()
        if payment.payment_attempts >= 2:
            cancel_failed_payment_order(order)
            messages.error(request, 'Maximum payment attempts reached. Order has been cancelled.')
        else:
            order.order_status = 'payment_pending'
            order.save()
            remaining = 2 - payment.payment_attempts
            messages.error(request, f'Payment verification failed. You have {remaining} attempt(s) remaining.')
        return redirect('customer_app:item_order', id=order.id)
    except Exception as e:
        messages.error(request, 'An unexpected error occurred during payment verification.')
        return redirect('customer_app:item_order', id=order.id)
def payment_failed(request):
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('customer_app:account')
def complete(request):
    return render(request, 'user/order-complete.html')
@login_required
def cancel_order(request, id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    if request.method != 'POST':
        return redirect('customer_app:item_order', id=id)
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('customer_app:account')
    if order.user != request.user:
        messages.error(request, 'Unauthorised action.')
        return redirect('user_app:user_logout')
    if order.order_status in ('delivered', 'canceled'):
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('customer_app:item_order', id=id)
    cancel_reason = request.POST.get('cancel_reason', '').strip()
    if not cancel_reason:
        messages.error(request, 'Cancellation reason is required.')
        return redirect('customer_app:item_order', id=id)
    try:
        payment = Payment.objects.get(order=order)
        payment_method = payment.payment_method
    except Payment.DoesNotExist:
        payment_method = 'cod'
    try:
        with transaction.atomic():
            order.order_status = 'canceled'
            order.cancellation_reason = cancel_reason
            order.save()
            active_items = order.items.exclude(cancel_status='canceled')
            for item in active_items:
                item.varient.stock = F('stock') + item.quantity
                item.varient.save()
            if payment_method != 'cod':
                SHIPPING = Decimal('50')
                all_items = order.items.all()
                total_items_subtotal = sum(
                    Decimal(str(i.price)) for i in all_items
                )
                canceled_items_subtotal = sum(
                    Decimal(str(i.price)) 
                    for i in all_items 
                    if i.cancel_status == 'canceled'
                )
                active_items_subtotal = total_items_subtotal - canceled_items_subtotal
                if total_items_subtotal > 0 and active_items_subtotal > 0:
                    active_proportion = active_items_subtotal / total_items_subtotal
                    amount_paid_for_products = (
                        Decimal(str(order.discount)) - SHIPPING
                    )
                    refund_amount = (
                        active_proportion * amount_paid_for_products
                    ) + SHIPPING
                else:
                    refund_amount = Decimal('0')
                refund_amount = max(refund_amount, Decimal('0')).quantize(Decimal('0.01'))
                if refund_amount > 0:
                    wallet, _ = Wallet.objects.get_or_create(user=request.user)
                    wallet.balance = F('balance') + refund_amount
                    wallet.save()
                    WalletTransation.objects.create(
                        wallet=wallet,
                        transaction_type='cancellation',
                        amount=refund_amount,
                    )
        messages.success(request, 'Order cancelled successfully.')
    except Exception as e:
        messages.error(request, 'Something went wrong while cancelling the order. Please try again.')
    return redirect('customer_app:item_order', id=id)
@login_required
def return_order(request, id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    if request.method != 'POST':
        return redirect('customer_app:account')
    try:
        order_item = OrderItems.objects.get(id=id)
    except OrderItems.DoesNotExist:
        messages.error(request, 'Order item not found.')
        return redirect('customer_app:account')
    order = order_item.order
    order_id = order.id
    if order.user != request.user:
        messages.error(request, 'Unauthorised action.')
        return redirect('user_app:user_logout')
    if order.order_status != 'delivered':
        messages.error(request, 'Only delivered orders can be returned.')
        return redirect('customer_app:item_order', id=order_id)
    if order_item.return_status in ('pending', 'returned'):
        messages.error(request, 'A return has already been requested for this item.')
        return redirect('customer_app:item_order', id=order_id)
    return_reason = request.POST.get('return_reason', '').strip()
    if not return_reason:
        messages.error(request, 'Return reason is required.')
        return redirect('customer_app:item_order', id=order_id)
    order_item.return_reason = return_reason
    order_item.return_status = 'pending'
    order_item.return_date = timezone.now()
    order_item.save()
    messages.success(request, 'Return request submitted successfully.')
    return redirect('customer_app:item_order', id=order_id)
def return_confirm(request, item_id, order_id):
    if getattr(request.user, 'is_block', False):
        return redirect('authentication_app:logout')
    if request.method != 'POST':
        return redirect('admin_app:show_order', id=order_id)
    try:
        item = OrderItems.objects.get(id=item_id)
    except OrderItems.DoesNotExist:
        messages.error(request, 'Order item not found.')
        return redirect('admin_app:show_order', id=order_id)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('admin_app:admin_home')
    if item.return_status == 'returned':
        messages.error(request, 'This item has already been returned.')
        return redirect('admin_app:show_order', id=order_id)
    try:
        with transaction.atomic():
            item_subtotal = item.price
            coupon_deduction = Decimal('0')
            if order.coupons:
                order_subtotal = sum(i.price for i in order.items.all())
                if order_subtotal > 0:
                    total_discount = order_subtotal - Decimal(str(order.discount))
                    item_proportion = item_subtotal / order_subtotal
                    coupon_deduction = total_discount * item_proportion
            refund_amount = max(item_subtotal - coupon_deduction, Decimal('0'))
            wallet, _ = Wallet.objects.get_or_create(user=order.user)
            wallet.balance = F('balance') + refund_amount
            wallet.save()
            WalletTransation.objects.create(
                wallet=wallet,
                transaction_type='refund',
                amount=refund_amount,
            )
            item.return_status = 'returned'
            item.save()
            item.varient.stock = F('stock') + item.quantity
            item.varient.save()
            item.product.sold_count = F('sold_count') - item.quantity
            item.product.save()
            all_items = order.items.all()
            if all_items.count() == all_items.filter(return_status='returned').count():
                order.order_status = 'canceled'
                order.cancellation_reason = 'All items returned'
                order.save()
        messages.success(request, f'Item returned. ₹{refund_amount:.2f} credited to wallet.')
    except Exception as e:
        messages.error(request, 'Something went wrong while processing the return.')
    return redirect('admin_app:show_order', id=order_id)
@login_required
def submit_review(request, product_id, order_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    product = get_object_or_404(Product, id=product_id)
    has_ordered = OrderItems.objects.filter(
        product=product,
        order__user=request.user,
        order__order_status='delivered',
    ).exists()
    if not has_ordered:
        messages.error(request, 'You can only review products you have purchased.')
        return redirect('customer_app:item_order', id=order_id)
    if ProductReview.objects.filter(user=request.user, product=product).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('customer_app:item_order', id=order_id)
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
            comment = request.POST.get('review', '').strip()
            if not (1 <= rating <= 5):
                messages.error(request, 'Rating must be between 1 and 5.')
                return redirect('customer_app:item_order', id=order_id)
            if not comment:
                messages.error(request, 'Review comment cannot be empty.')
                return redirect('customer_app:item_order', id=order_id)
            ProductReview.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment,
            )
            messages.success(request, 'Thank you for your review!')
            return redirect('customer_app:item_order', id=order_id)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value.')
            return redirect('customer_app:item_order', id=order_id)
        except Exception as e:
            messages.error(request, 'Something went wrong while submitting your review.')
            return redirect('customer_app:item_order', id=order_id)
    order_items = OrderItems.objects.filter(product=product, order__user=request.user)[:1]
    return render(request, 'user/review.html', {'order_items': order_items, 'order_id': order_id})
@login_required
def cancel_order_item(request, item_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    if request.method != 'POST':
        return redirect('customer_app:account')
    order_item = get_object_or_404(OrderItems, id=item_id)
    order = order_item.order
    order_id = order.id
    if order.user != request.user:
        messages.error(request, 'Unauthorised action.')
        return redirect('user_app:user_logout')
    if order.order_status in ('delivered', 'canceled'):
        messages.error(request, 'This order cannot be modified.')
        return redirect('customer_app:item_order', id=order_id)
    if order_item.cancel_status == 'canceled':
        messages.error(request, 'This item is already cancelled.')
        return redirect('customer_app:item_order', id=order_id)
    cancel_reason = request.POST.get('cancel_reason', '').strip()
    if not cancel_reason:
        messages.error(request, 'Cancellation reason is required.')
        return redirect('customer_app:item_order', id=order_id)
    try:
        payment = Payment.objects.get(order=order)
        payment_method = payment.payment_method
    except Payment.DoesNotExist:
        payment_method = 'cod'
    try:
        with transaction.atomic():
            item_subtotal = order_item.price
            coupon_deduction = Decimal('0')
            if order.coupons:
                order_subtotal = sum(i.price for i in order.items.all())
                if order_subtotal > 0:
                    total_discount = order_subtotal - Decimal(str(order.discount))
                    item_proportion = item_subtotal / order_subtotal
                    coupon_deduction = total_discount * item_proportion
            refund_amount = max(item_subtotal - coupon_deduction, Decimal('0'))
            active_items = order.items.exclude(cancel_status='canceled')
            if active_items.count() == 1 and active_items.first() == order_item:
                refund_amount += Decimal('50.00')
            order_item.cancel_reason = cancel_reason
            order_item.cancel_status = 'canceled'
            order_item.save()
            order_item.varient.stock = F('stock') + order_item.quantity
            order_item.varient.save()
            order_item.product.sold_count = F('sold_count') - order_item.quantity
            order_item.product.save()
            if payment_method != 'cod':
                wallet, _ = Wallet.objects.get_or_create(user=request.user)
                wallet.balance = F('balance') + refund_amount
                wallet.save()
                WalletTransation.objects.create(
                    wallet=wallet,
                    transaction_type='cancellation',
                    amount=refund_amount,
                )
            all_items = order.items.all()
            if all_items.count() == all_items.filter(cancel_status='canceled').count():
                order.order_status = 'canceled'
                order.cancellation_reason = 'All items canceled by user'
                order.save()
        if payment_method != 'cod':
            messages.success(
                request,
                f'"{order_item.product.product_name}" cancelled. ₹{refund_amount:.2f} refunded to wallet.'
            )
        else:
            messages.success(request, f'"{order_item.product.product_name}" has been cancelled.')
    except Exception as e:
        messages.error(request, 'Something went wrong while cancelling the item. Please try again.')
    return redirect('customer_app:item_order', id=order_id)