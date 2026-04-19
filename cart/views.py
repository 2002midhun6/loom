from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from product.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from address.models import Address
from order.models import Order
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from datetime import datetime
from django.urls import reverse
from django.db import transaction
import pytz
import json
def _get_kolkata_now():
    return datetime.now(pytz.timezone('Asia/Kolkata'))
def _expire_offers(product, now):
    expired = False
    if product.offer and product.offer.end_date < now:
        product.offer = None
        product.save()
        expired = True
    elif (
        product.sub_category
        and product.sub_category.offer
        and product.sub_category.offer.end_date < now
    ):
        product.sub_category.offer = None
        product.sub_category.save()
        expired = True
    return expired
def _staff_or_blocked_redirect(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and getattr(request.user, 'is_block', False):
        return redirect('user_app:user_logout')
    return None
def add_to_cart(request, id):
    now = _get_kolkata_now()
    if not request.user.is_authenticated:
        return redirect("user_app:user_login")

    if request.user.is_staff:
        return redirect('admin_app:admin_home')

    if getattr(request.user, 'is_block', False):
        return redirect('user_app:user_logout')

    if request.method != 'POST':
        messages.error(request, 'Please select a size.')
        return redirect('customer_app:view_product', id=id)
    try:
        user = request.user
        product = get_object_or_404(Product, id=id)
        _expire_offers(product, now)
        varient_id = request.POST.get('var_id')
        if not varient_id:
            messages.error(request, 'Please select a size.')
            return redirect('customer_app:view_product', id=id)
        varient = get_object_or_404(Varient, id=varient_id)
        if varient.stock < 1:
            messages.error(request, f'Sorry, "{product.product_name}" in the selected size is out of stock.')
            return redirect('customer_app:view_product', id=id)
        with transaction.atomic():
            cart, _ = Cart.objects.get_or_create(user=user)
            unit_price = getattr(varient, 'price', None) or product.price   
            cart_item, created = Cart_item.objects.get_or_create(
                cart=cart,
                product=product,
                varient=varient,
                defaults={
                    'quantity': 1,
                    'total_price': unit_price,
                }
            )
            item_exists = not created
            if created:
                cart_item.quantity = 1
                cart_item.total_price = unit_price
                cart_item.save()
            else:
                pass
            if request.POST.get('wishlist') == 'wishlist':
                request.session['just_added_to_cart'] = json.dumps({ 
                        'product_name': product.product_name,
                        'was_already_in_cart': item_exists  
                    })
                return redirect('wishlist_app:wishlist_view')
            varients = product.varient.all() 
            return render(request, 'user/view_product.html', {
                'product': product,
                'id': id,
                'alert': True,
                'item_exists': item_exists,
                'varients': varients,   
            })
    except Exception as e:
        messages.error(request, 'Something went wrong while adding to cart. Please try again.')
        return redirect('customer_app:view_product', id=id)
@login_required
@never_cache
def view_cart(request):
    now = _get_kolkata_now()
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    except Exception:
        messages.error(request, 'Could not load your cart. Please try again.')
        return redirect('user_app:index')
    request.session.pop('cart_total_with_discount', None)
    request.session.pop('coupon', None)
    offer_ended = False
    filtered_cart_items = []
    for item in cart.items.select_related('product', 'product__category', 'product__sub_category', 'varient').all():
        if (
            not item.product.is_listed
            or not item.product.category.is_listed
            or not item.product.sub_category.is_listed
        ):
            item.delete()
            continue

        if _expire_offers(item.product, now):
            offer_ended = True
        if item.quantity > item.varient.stock:
            item.quantity = item.varient.stock
            item.save()
            messages.warning(
                request,
                f'Quantity for "{item.product.product_name}" adjusted to available stock ({item.varient.stock}).'
            )
        item.total_price = item.product.discount_price * item.quantity
        filtered_cart_items.append(item)
    cart_total = sum(item.total_price for item in filtered_cart_items)
    cart_delivery = float(cart_total) + 50
    request.session['cart_total'] = float(cart_total)
    return render(request, 'user/cart.html', {
        'cart': cart,
        'cart_items': filtered_cart_items,
        'cart_total': cart_total,
        'cart_delivery': cart_delivery,
        'offer_ended': offer_ended,
    })
@login_required
def update_cart_item_quantity(request, product_id, varient_id, action):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    product = get_object_or_404(Product, id=product_id)
    varient = get_object_or_404(Varient, id=varient_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item = get_object_or_404(Cart_item, cart=cart, product=product, varient=varient)
    if action == 'increment':
        if cart_item.quantity >= varient.stock:
            messages.error(
                request,
                f'Cannot add more "{product.product_name}". Maximum stock ({varient.stock}) reached.'
            )
        else:
            cart_item.quantity += 1
            cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    else:
        messages.error(request, 'Invalid action.')
    return redirect('cart_app:view_cart')
def remove_cart_item(request, cart_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        cart_item = Cart_item.objects.get(id=cart_id)
        if cart_item.cart.user != request.user:
            messages.error(request, 'You are not authorised to remove this item.')
            return redirect('cart_app:view_cart')
        cart_item.delete()
    except Cart_item.DoesNotExist:
        messages.error(request, 'Cart item not found.')
    return redirect('cart_app:view_cart')
@never_cache
def checkout(request, cart_id):
    now = _get_kolkata_now()
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    if not request.user.is_authenticated:
        return redirect('user_app:user_login')
    try:
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        messages.error(request, 'Cart not found.')
        return redirect('cart_app:view_cart')
    if request.user.id != cart.user.id:
        messages.error(request, 'Unauthorised access.')
        return redirect('user_app:user_logout')
    cart_items = cart.items.select_related('product', 'product__sub_category', 'varient').all()
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_app:view_cart')
    offer_ended = False
    cart_items_with_prices = []
    for item in cart_items:
        if _expire_offers(item.product, now):
            offer_ended = True
        item.total_price = item.product.discount_price * item.quantity
        cart_items_with_prices.append(item)
    cart_subtotal = sum(item.total_price for item in cart_items_with_prices)
    cart_total = float(cart_subtotal) + 50  
    cart_total_with_discount = float(
        request.session.get('cart_total_with_discount', cart_total)
    )
    request.session['cart_total_with_discount'] = cart_total_with_discount
    coupon_savings = cart_total - cart_total_with_discount
    try:
        address = Address.objects.get(user=request.user, default=True)
    except Address.DoesNotExist:
        address = None
    except Address.MultipleObjectsReturned:
        address = Address.objects.filter(user=request.user, default=True).first()
    all_addresses = Address.objects.filter(user=request.user)
    return render(request, 'user/checkout.html', {
        'cart': cart,
        'user': request.user,
        'cart_items': cart_items_with_prices,
        'cart_id': cart_id,
        'cart_total': cart_total,
        'address': address,
        'all_addresses': all_addresses,
        'cart_total_with_discount': cart_total_with_discount,
        'offer_ended': offer_ended,
        'coupon_savings': coupon_savings,
        'coupon': request.session.get('coupon', ''),
    })
def set_checkout_address(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)
    try:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        if not address_id:
            return JsonResponse({'success': False, 'error': 'address_id is required.'}, status=400)
        address = get_object_or_404(Address, id=address_id, user=request.user)
        request.session['checkout_address_id'] = address_id
        return JsonResponse({
            'success': True,
            'address': {
                'street_address': address.street_address,
                'postal_code': address.postal_code,
                'phone': address.phone,
                'state': address.state,
                'country': address.country,
                'landmark': getattr(address, 'landmark', ''),
                'alternative_phone': getattr(address, 'alternative_phone', ''),
                'address_type': address.address_type,
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
def coupon(request):
    if not request.user.is_authenticated:
        return redirect('user_app:user_login')
    if request.user.is_staff:
        return redirect('admin_app:admin_home')
    if getattr(request.user, 'is_block', False):
        return redirect('user_app:user_logout')
    if request.method != 'POST':
        return redirect('user_app:index')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    def ajax_or_redirect(status, message, cart_id, extra=None):
        if is_ajax:
            payload = {'status': status, 'message': message}
            if extra:
                payload.update(extra)
            return JsonResponse(payload)
        if status == 'error':
            messages.error(request, message)
        else:
            messages.success(request, message)
        return redirect('cart_app:checkout', cart_id=cart_id)

    cart_id = request.POST.get('cart_id')
    customer_coupon = request.POST.get('coupon', '').strip()
    try:
        cart_total = float(request.POST.get('cart_total', 0))
    except (ValueError, TypeError):
        return ajax_or_redirect('error', 'Invalid cart total.', cart_id)
    if not cart_id:
        return ajax_or_redirect('error', 'Cart ID missing.', cart_id)
    if not customer_coupon:
        return ajax_or_redirect('error', 'Please enter a coupon code.', cart_id)
    try:
        coupon_obj = Coupen.objects.filter(code=customer_coupon).first()
        if not coupon_obj:
            return ajax_or_redirect('error', 'Invalid coupon code. Please try again.', cart_id)
        usage_count = Order.objects.filter(
            user=request.user, coupons=coupon_obj
        ).count()
        if usage_count >= int(coupon_obj.used_limit):
            return ajax_or_redirect('error', 'You have exceeded the usage limit for this coupon.', cart_id)
        if not (coupon_obj.minimum_order_amount < cart_total < coupon_obj.maximum_order_amount):
            return ajax_or_redirect(
                'error',
                f'This coupon is valid only for orders between '
                f'₹{coupon_obj.minimum_order_amount} and ₹{coupon_obj.maximum_order_amount}.',
                cart_id
            )
        discounted_total = cart_total - float(coupon_obj.discount_amount)
        request.session['coupon'] = coupon_obj.code
        request.session['total_without_coupon'] = cart_total
        request.session['cart_total_with_discount'] = discounted_total
        return ajax_or_redirect(
            'success',
            'Coupon applied successfully.',
            cart_id,
            extra={
                'coupon_code': coupon_obj.code,
                'discount_amount': float(coupon_obj.discount_amount),
                'cart_total_with_discount': discounted_total,
            }
        )
    except Exception as e:
        return ajax_or_redirect('error', f'Error applying coupon: {str(e)}', cart_id)
def checkout_add_address(request, cart_id):
    request.session['next'] = reverse('cart_app:checkout', kwargs={'cart_id': cart_id})
    return redirect('customer_app:add_address')
def checkout_edit_address(request, cart_id, addr_id):
    request.session['next'] = reverse('cart_app:checkout', kwargs={'cart_id': cart_id})
    return redirect('customer_app:edit_address', id=addr_id)
def update_cart_item_quantity_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)
    try:
        product_id = data.get('product_id')
        varient_id = data.get('varient_id')
        action = data.get('action')
        if not all([product_id, varient_id, action]):
            return JsonResponse({'success': False, 'error': 'product_id, varient_id, and action are required.'}, status=400)
        try:
            varient_obj = Varient.objects.get(id=varient_id)
        except Varient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Variant not found.'}, status=404)
        cart_item = get_object_or_404(Cart_item, product_id=product_id, varient_id=varient_id, cart__user=request.user)
        if action == 'increment':
            if cart_item.quantity >= varient_obj.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Maximum available stock ({varient_obj.stock}) reached.'
                })
            cart_item.quantity += 1
        elif action == 'decrement':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                return JsonResponse({'success': False, 'error': 'Quantity cannot be less than 1. Remove the item instead.'})
        else:
            return JsonResponse({'success': False, 'error': f'Unknown action: {action}.'}, status=400)
        cart_item.total_price = cart_item.quantity * cart_item.product.discount_price
        cart_item.save()
        cart_total = Cart_item.objects.filter(cart=cart_item.cart).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        return JsonResponse({
            'success': True,
            'new_quantity': cart_item.quantity,
            'item_total_price': float(cart_item.total_price),
            'cart_subtotal': float(cart_total),
            'cart_total': float(cart_total) + 50,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)