from django.shortcuts import render,redirect,get_object_or_404
from  cart.models import *
from address.models import Address
from decimal import Decimal
from datetime import timedelta
from order.models import *
from cart.models import *
from django.contrib import messages
from django.db.models import F
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.conf import settings
import razorpay
from django.utils import timezone
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.

def order_complete(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
   
           
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_id = cart.id
    cart_item = cart.items.all()
    delivery_date = timezone.now() + timedelta(days=7)
    address=Address.objects.get(default=True,user=user)
   
    coupon_code=request.session.get('coupon')
    print(coupon_code)
    if coupon_code :
        if Coupen.objects.filter(code=coupon_code).exists():
            coupon_obj=Coupen.objects.get(code=coupon_code)
        else:
            request.session['cart_total_with_discount']=request.session.get('total_without_coupon')
            del request.session['total_without_coupon']
            messages.error(request, "The coupon you applied is no longer valid.")
            return redirect('cart_app:view_cart')
            
    discount=request.session['cart_total_with_discount']
    order = Order(
            user = user,
            order_status = 'confirmed',
            delivery_date = delivery_date,
            address = address,
            discount = discount,
        )
   
    if coupon_code:
        order.coupons=coupon_obj
    
    order.save() 
    OrderAddress.objects.create(
        order=order,
        landmark=address.landmark,
        postal_code=address.postal_code,
        phone=address.phone,
        street_address=address.street_address,
        alternative_phone=address.alternative_phone,
    )
   
    for item in cart_item:
            # product price if it has offer or not.
            item_price = 0
           
            item_price = item.product.discount_price
            
            
            
           
            OrderItems.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                item_price=item_price,
                
                price = item.quantity * Decimal(item_price),
                varient = item.varient
                
            )
            # Reducing the available stock
            
            item.varient.stock = F('stock') - item.quantity
            
            item.product.sold_count = F('sold_count') + item.quantity
            item.varient.save()
            item.product.save()
    cart_item.delete()
    
    payment_method=request.POST.get('payment_method')
    try:
        if payment_method=='cod':
            if discount > 1000:
                return 
            payment_obj = Payment.objects.create(
                    order = order,
                    total_price = discount,
                    payment_method = 'cod', 
                    payment_status = 'success',        
                )
            return redirect('order_app:complete')
        elif payment_method=='wallet':

            
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet_balance = wallet.balance 
            wallet_balance=wallet.balance
            if wallet_balance < discount:
                messages.error(request,'insufficent balance in wallet')
                return redirect('cart_app:checkout', cart_id=cart_id)
            else:
                wallet_balance=float(wallet_balance) - discount
                wallet.balance=wallet_balance
                wallet.save()
                wallet_transaction_obj = WalletTransation.objects.create(
                    wallet = wallet,
                    transaction_type = 'debited',
                    amount = discount,
                )
            
                payment_obj = Payment.objects.create(
                    order = order,
                    total_price = discount,
                    payment_method = 'wallet',  
                    payment_status = 'success',     
                )
            return redirect('order_app:complete')
        else :
            
            # Create Razorpay order
            try:
                if payment_method == 'razorpay':
                        razorpay_amount = int(float(discount) * 100)
                        razorpay_order = razorpay_client.order.create(dict(
                            amount=razorpay_amount,
                            currency='INR',
                            payment_capture='1'
                        ))
                        
                        # Create payment record with pending status and initialize attempts
                        payment_obj = Payment.objects.create(
                            order=order,
                            total_price=discount,
                            payment_method='razorpay',
                            payment_status='pending',
                            razorpay_order_id=razorpay_order['id'],
                            payment_attempts=1  # First attempt
                        )
                        
                        # Update order status to payment pending
                        order.order_status = 'payment_pending'
                        order.save()
                        
                        context = {
                            'razorpay_order_id': razorpay_order['id'],
                            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                            'razorpay_amount': razorpay_amount,
                            'order_id': order.id,
                            'attempts_remaining': 1  # Since this is first attempt
                        }
                        return render(request, 'user/razorpay_payment.html', context)
            
            except Exception as e:
                messages.error(request, f"Error processing payment: {e}")
        return redirect('cart_app:checkout')
    except Exception as e:
        messages.error(request, f"Error processing payment: {e}")
        return redirect('cart_app:checkout')
def retry_payment(request, order_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment = Payment.objects.get(order=order)
        
        # Check payment attempts
        if payment.payment_attempts >= 2:
            # Auto cancel the order
            cancel_failed_payment_order(order)
            messages.error(request, 'Maximum payment attempts reached. Order has been cancelled.')
            return redirect('customer_app:item_order', id=order_id)
        
        # Only allow retry if payment is pending or failed
        if payment.payment_status not in ['pending', 'failed']:
            messages.error(request, 'This order cannot be retried for payment')
            return redirect('customer_app:item_order', id=order_id)
        
        # Create new Razorpay order
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_amount = int(float(order.discount) * 100)
        
        razorpay_order = razorpay_client.order.create(dict(
            amount=razorpay_amount,
            currency='INR',
            payment_capture='1'
        ))
        
        # Increment payment attempts
        payment.payment_attempts += 1
        payment.razorpay_order_id = razorpay_order['id']
        payment.payment_status = 'pending'
        payment.save()
        
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'razorpay_amount': razorpay_amount,
            'order_id': order.id,
            'attempts_remaining': 2 - payment.payment_attempts
        }
        
        return render(request, 'user/razorpay_payment.html', context)
        
    except Exception as e:
        messages.error(request, f'Error processing payment retry: {str(e)}')
        return redirect('customer_app:item_order', id=order_id)
def cancel_failed_payment_order(order):
    """Helper function to cancel order after payment failures"""
    order.order_status = 'canceled'
    order.cancellation_reason = 'Maximum payment attempts exceeded'
    order.save()
    
    # Return items to inventory
    order_items = order.items.all()
    for item in order_items:
        item.varient.stock = F('stock') + item.quantity
        item.varient.save()
        
        # Update product sold count
        item.product.sold_count = F('sold_count') - item.quantity
        item.product.save()



@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            }
            
            try:
                razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                razorpay_client.utility.verify_payment_signature(params_dict)
                
                payment = Payment.objects.get(razorpay_order_id=order_id)
                order = payment.order
                
                # Update payment and order status
                payment.payment_status = 'success'
                payment.razorpay_payment_id = payment_id
                payment.save()
                
                order.order_status = 'confirmed'
                order.save()
                
                return redirect('order_app:complete')
                
            except razorpay.errors.SignatureVerificationError:
                payment = Payment.objects.get(razorpay_order_id=order_id)
                order = payment.order
                
                # Update payment status to failed
                payment.payment_status = 'failed'
                payment.save()
                
                # Check if this was the last attempt
                if payment.payment_attempts >= 2:
                    cancel_failed_payment_order(order)
                    messages.error(request, 'Maximum payment attempts reached. Order has been cancelled.')
                else:
                    # Update order status to payment pending
                    order.order_status = 'payment_pending'
                    order.save()
                    messages.error(request, f'Payment verification failed. You have {2 - payment.payment_attempts} attempts remaining.')
                
                return redirect('customer_app:item_order', id=order.id)
                
        except Exception as e:
            messages.error(request, f'Payment processing error: {str(e)}')
            return redirect('cart_app:checkout')
            
    return HttpResponse('Invalid Request', status=400)

def payment_failed(request):
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('customer_app:account')
       
     
def complete(request):
     return render(request,'user/order-complete.html')

def cancel_order(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        
        # If order is done by COD then in cancel order money should not be credited to the wallet.
        try:
            payment = Payment.objects.get(order = order)
            payment_method = payment.payment_method
        except Exception as e:
            payment_method = 'cod'
        
        # Get cancellation reason from form
        cancel_reason = request.POST.get('cancel_reason')
        
        if cancel_reason:
            order.order_status = 'canceled'
            order.cancellation_reason = cancel_reason 
            
            # If order canceled then available stock is recalculated
            order_items = order.items.all()
            total_price = 0
            for item in order_items:
                
                
                item.varient.stock = F('stock') + item.quantity
                item.varient.save()
            order.save()
            
            # Adding money to wallet when cancelling the order.
            if not payment_method=='cod':
                wallet = Wallet.objects.get(user=request.user)
                wallet.balance = F('balance') + order.discount
                wallet.save()
                print(wallet.balance)
                print('its my wallet balance')
                
                wallet_transaction = WalletTransation.objects.create(
                    wallet = wallet,
                    transaction_type = 'cancellation',
                    amount = order.discount,
                )

            messages.success(request, "Order canceled successfully.")
        else:
            messages.error(request, "Cancellation reason is required.")
    
    return redirect('customer_app:item_order', id=id)
def return_order(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    print('hello kutta')
    if request.method == 'POST':
        order_item = OrderItems.objects.get(id=id)
        order=order_item.order
        order_id=order.id
        return_reason = request.POST.get('return_reason')
        if return_reason:
            order_item.return_reason = return_reason
            order_item.return_date = timezone.now()
            
            order_item.save()
            print('hello kutta3',order_item.return_reason)
            

            messages.success(request, "Return request sent.")
        else:
            messages.error(request, "Return reason is required.")
        print("hhhdicke")
    return redirect('customer_app:item_order', id=order_id)
def return_confirm(request,item_id,order_id):
    # if request.user.is_authenticated and request.user.is_staff:
    #     return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    if request.method == 'POST':

        item = OrderItems.objects.get(id=item_id)
        order = Order.objects.get(id=order_id)
        items=order.items.all()
        count=len(items)
        if order.coupons:
            amount=order.coupons.discount_amount
            deducted=amount//count

        else:
            deducted=0
        # Adding money to wallet when returning the item.
        total_price = (item.price * item.quantity)-deducted
        print(item.price,item.quantity)
        print(total_price)
      
        # getting the user of the order.
        order = Order.objects.get(id = order_id)
        user_id = order.user.id
        user = CustomUser.objects.get(id=user_id)
        wallet,created = Wallet.objects.get_or_create(user=user)
        wallet.balance = F('balance') + total_price
        wallet.save()
        print(wallet.balance)
        
        wallet_transaction = WalletTransation.objects.create(
            wallet = wallet,
            transaction_type = 'refund',
            amount = total_price,
        )
        
        item.return_status = 'returned'
        item.save()
        
        return redirect('admin_app:show_order',id=order_id)
    else:
        return redirect('admin_app:show_order',id=order_id)
@login_required
def submit_review(request, product_id,order_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('review')
        print(order_id)
        
        product = get_object_or_404(Product, id=product_id)
        
        # Save the review
        review = ProductReview(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment,
            
        )
        review.save()

        
        messages.success(request, "Thank you for your review!")
        return redirect('customer_app:item_order', id=order_id)

    order_items = OrderItems.objects.filter(product_id=product_id, order__user=request.user)[:1]
    
    if not order_items.exists():
        print('no order')
        messages.error(request, "Order item does not exist.")
        return redirect('customer_app:item_order', id=order_id)
    
    return render(request,'user/review.html',{'order_items':order_items,'order_id':order_id})



