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
    coupon_obj=Coupen.objects.get(code=coupon_code)
    discount=request.session['cart_total_with_discount']
    order = Order(
            user = user,
            order_status = 'confirmed',
            delivery_date = delivery_date,
            address = address,
            coupons = coupon_obj,
            discount = discount,
        )
    order.save() 
    for item in cart_item:
            # product price if it has offer or not.
            item_price = 0
            if item.product.offer:
                item_price = item.product.discount_price
            else:
                item_price = item.product.price
            OrderItems.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
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
       
        item.varient.stock = F('stock') + item.quantity
        item.varient.save()
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



    
    
    

        

    