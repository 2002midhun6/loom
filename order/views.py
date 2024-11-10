from django.shortcuts import render,redirect
from  cart.models import *
from address.models import Address
from decimal import Decimal
from datetime import timedelta
from order.models import *
from cart.models import *
from django.db.models import F
# Create your views here.
def order_complete(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
   
           
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_item = cart.items.all()
    delivery_date = timezone.now() + timedelta(days=7)
    address=Address.objects.get(default=True,user=user)
    order = Order(
            user = user,
            order_status = 'confirmed',
            delivery_date = delivery_date,
            address = address
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
                price = item.quantity * Decimal(item_price)
            )
            # Reducing the available stock

            item.product.varient.stock = F('stock') - item.quantity
            item.product.sold_count = F('sold_count') + item.quantity
            item.product.save()
    cart_item.delete()
    payment_method=request.POST.get('payment_method')
    if payment_method=='cod':
         payment_obj = Payment.objects.create(
                order = order,
                total_price = request.session['cart_total'] ,
                payment_method = 'cod',        
            )
    return render(request,'user/order-complete.html')
