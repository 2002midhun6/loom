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
from django.http import JsonResponse


# Create your views here.
@never_cache
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
    if coupon_code:
        coupon_obj=Coupen.objects.get(code=coupon_code)
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
    cart_item.delete()
    
    payment_method=request.POST.get('payment_method')
    if payment_method=='cod':
         payment_obj = Payment.objects.create(
                order = order,
                total_price = discount,
                payment_method = 'cod', 
                payment_status = 'success',        
            )
    if payment_method=='wallet':

        
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
    if payment_method=='razer_pay':
        razorpay_order = razorpay_client.order.create({
        'amount': int(discount * 100),  # Razorpay requires amount in paise
        'currency': 'INR',
        'receipt': f'order_{order.id}',
        'payment_capture': 1,
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    # Render Razorpay checkout page
    context = {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'amount': discount * 100,  # Razorpay expects paise
        'currency': 'INR',
    }
    return render(request, 'user/payment.html', context)
    return redirect('order_app:complete')
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
    
    if request.method == 'POST':
        order_item = OrderItems.objects.get(id=id)
        order=order_item.order
        order_id=order.id
        return_reason = request.POST.get('return_reason')
        if return_reason:
            order_item.return_reason = return_reason
            order_item.return_date = timezone.now()
            order_item.save()
            

            messages.success(request, "Return request sent.")
        else:
            messages.error(request, "Return reason is required.")
    
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
            comment=comment
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



@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        try:
            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update payment status in the database
            payment = Payment.objects.create(
                order=Order.objects.get(razorpay_order_id=razorpay_order_id),
                payment_method='razorpay',
                payment_status='success',
                total_price=request.session['cart_total_with_discount'],
            )
            return JsonResponse({'status': 'success'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failed'})

    
    
    

        

    