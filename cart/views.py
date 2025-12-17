from django.shortcuts import render,redirect,get_object_or_404
from  . models import *
from product.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from address.models import Address
from order.models import Order
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import datetime
import pytz





    
from django.db import transaction
from django.http import HttpResponse

def add_to_cart(request, id):
    kolkata_tz = pytz.timezone('Asia/Kolkata')
       
    now = datetime.now(kolkata_tz)
    print("=== Starting add_to_cart function ===")
    
    if not request.user.is_authenticated:
        print("User not authenticated")
        return redirect("user_app:user_login")

    if request.user.is_staff:
        print("Staff user detected")
        return redirect('admin_app:admin_home')
        
    if request.user.is_block:
        print("Blocked user detected")
        return redirect('user_app:user_logout')

    if request.method == 'POST':
        try:
            print(f"Processing POST request for product ID: {id}")
            
            
            user = request.user
            print(f"User: {user.username}")
            
            product = get_object_or_404(Product, id=id)
            offer_ended=False
            if product.offer and product.offer.end_date < now:
                    product.offer = None
                    product.save()
                    offer_ended = True
            elif product.sub_category.offer and product.sub_category.offer.end_date < now:
                    product.offer = None
                    product.sub_category.offer = None
                    product.sub_category.save()
                    offer_ended = True
            print(f"Product found: {product.product_name}")
           
            varients_id = request.POST.get('var_id')
            print(f"Variant ID from POST: {varients_id}")
            
            varient = Varient.objects.get(id=varients_id)
            print(f"Variant found: {varient}")
            
            
            with transaction.atomic():
                cart, cart_created = Cart.objects.get_or_create(user=user)
                print(f"Cart {'created' if cart_created else 'retrieved'} for user")
                print(f"Cart ID: {cart.id}")
                
               
                unit_price = varient.price if hasattr(varient, 'price') else product.price
                print(f"Unit price: {unit_price}")
                
                
                cart_item, created = Cart_item.objects.get_or_create(
                    cart=cart,
                    product=product,
                    varient=varient,
                    defaults={
                        'quantity': 1,
                        'total_price': unit_price
                    }
                )
                
                
                if not created:
                    print("Item already exists in cart")
                    item_exists = True 
                else:
                    print("New cart item created")
                    cart_item.quantity = 1
                    cart_item.total_price = unit_price * cart_item.quantity
                    cart_item.save()
                    item_exists = False 
                print(f"Cart item saved with ID: {cart_item.id}")
                print(f"Final quantity: {cart_item.quantity}")
                print(f"Final total price: {cart_item.total_price}")
                alert = True
                if request.POST.get('wishlist'):
                    request.session['exist_session']=item_exists
                    return redirect('wishlist_app:wishlist_view')
                return render(request,'user/view_product.html',{'product':product,'id':id,'alert':alert,'item_exists': item_exists,})
            
        except Product.DoesNotExist:
            print("Product not found")
            return HttpResponse("Product not found")
        except Varient.DoesNotExist:
            print("Variant not found")
            return HttpResponse("Variant not found")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
    error_message = "select a size"

          
    messages.error(request, error_message)
    return redirect('customer_app:view_product', id=id )


@login_required
def view_cart(request):
    kolkata_tz = pytz.timezone('Asia/Kolkata')
       
    now = datetime.now(kolkata_tz)
    
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    if not request.user.is_authenticated:
        return redirect('user_app:user_login')
    
    offer_ended = False
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    if 'cart_total_with_discount' in request.session:
        del request.session['cart_total_with_discount']
    if 'coupon' in request.session:
        del request.session['coupon']
    
    
    filtered_cart_items = []
    
    
    for item in cart_items:
        if  not item.product.is_listed or not item.product.category.is_listed or not item.product.category.is_listed:
            item.delete()
        else:
            
            if item.product.offer and item.product.offer.end_date < now:
                    item.product.offer = None
                    item.product.save()
                    offer_ended = True
                    print(1)
            elif item.product.sub_category.offer and item.product.sub_category.offer.end_date < now:
                    item.product.offer = None
                    item.product.sub_category.offer = None
                    item.product.sub_category.save()
                    offer_ended = True
                    print(1,3)
            
            
            if item.quantity > item.varient.stock:
                item.quantity = item.varient.stock
                item.save()
                messages.warning(request, f'Quantity for {item.product.product_name} has been adjusted to match available stock ({item.variant.stock}).')
            filtered_cart_items.append(item)
    
    cart_items_with_prices = []
   
    
    for item in filtered_cart_items:
        
                
        item.total_price = item.product.discount_price * item.quantity
        
           
        
        cart_items_with_prices.append(item)
    
    
    cart_total = sum(item.total_price for item in cart_items_with_prices)
    
    
    request.session['cart_total'] = float(cart_total)
    cart_delivery=float(cart_total)+50
    
    return render(request, 'user/cart.html', {
        'cart': cart,
        'cart_items': filtered_cart_items,
        'cart_total': cart_total,
        'cart_delivery': cart_delivery,
        'offer_ended':offer_ended,
        
    })

@login_required
def update_cart_item_quantity(request, product_id,varient_id, action):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    varient = get_object_or_404(Varient, id=varient_id)
    
    
    
    cart, created = Cart.objects.get_or_create(user=user)
    
    
    cart_item = get_object_or_404(Cart_item, cart=cart, product=product,varient=varient)
    
    
    if action == 'increment':
        
        if cart_item.quantity >= varient.stock:
            messages.error(request, f'Cannot add more {product.product_name}. Maximum available stock {varient.stock} reached.')
            return redirect('cart_app:view_cart')
        cart_item.quantity += 1
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return redirect('cart_app:view_cart')
    
    cart_item.save()
    return redirect('cart_app:view_cart')
def remove_cart_item(request,cart_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    cart_item = Cart_item.objects.get(id = cart_id)
    cart_item.delete()
    
    return redirect('cart_app:view_cart')
@never_cache
def checkout(request,cart_id):
    kolkata_tz = pytz.timezone('Asia/Kolkata')
       
    now = datetime.now(kolkata_tz)
    
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    if not request.user.is_authenticated:
        return redirect('user_app:user_login')
    user_email = request.user.email
    user = CustomUser.objects.get(email = user_email)
    cart = Cart.objects.get(id = cart_id)
    if request.user.id != cart.user.id:
        return redirect('user_app:user_logout')

    cart_items = cart.items.all()
  
    
    cart_items_with_prices = []
    offer_ended =''
    
    for item in cart_items:
        offer_ended = False
        if item.product.offer and item.product.offer.end_date < now:
                    item.product.offer = None
                    item.product.save()
                    offer_ended = True
        elif item.product.sub_category.offer and item.product.sub_category.offer.end_date < now:
                    item.product.offer = None
                    item.product.sub_category.offer = None
                    item.product.sub_category.save()
                    offer_ended = True
       
        item.total_price = item.product.discount_price * item.quantity
        
        cart_items_with_prices.append(item)
    cart_total = sum(item.total_price for item in cart_items_with_prices)+50
    
    
    request.session['cart_total_with_discount'] = float(request.session.get('cart_total_with_discount', cart_total)) 
    cart_total_with_discount=request.session['cart_total_with_discount']

    
    
    
        
    try:
        address = Address.objects.get(user=request.user, default=True)
    except Address.DoesNotExist:
        
        messages.error(request, "Please add a default address to proceed.")
        return redirect('customer_app:account')  

    print(address.phone)
    
    context = {
        'cart':cart,
        'user':user,
        'cart_items':cart_items,
        'cart_id':cart_id,
        'cart_total':cart_total,
        'address':address,
        'cart_total_with_discount':cart_total_with_discount,
        'offer_ended':offer_ended
        
    }
    return render(request,'user/checkout.html',context)



def coupon(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_block:
            return redirect('user_app:user_logout')
    
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        cart_total = float(request.POST.get('cart_total', 0))  
        customer_coupon = request.POST.get('coupon')
        
        if not customer_coupon:
            print('not customer_coupon' )
            return redirect('cart_app:checkout', cart_id=cart_id)
        else:
            
            coupon_obj  = Coupen.objects.filter(code=customer_coupon).first()
            user = request.user

            counter=0
            
            if coupon_obj and coupon_obj.code == customer_coupon:
                    order = Order.objects.filter(user=user,coupons=coupon_obj)
                    print(order)
                    limit=int(coupon_obj.used_limit)
                    for i in order:
                        if i.coupons.code == customer_coupon:
                            counter+=1
                    if counter < limit:
                        if cart_total < coupon_obj.maximum_order_amount and cart_total > coupon_obj.minimum_order_amount:
                       
                            print(coupon_obj.code)
                            
                            request.session['coupon']=coupon_obj.code
                            request.session['total_without_coupon']=cart_total
                            request.session['cart_total_with_discount'] = cart_total - float(coupon_obj.discount_amount)
                            print(request.session['cart_total_with_discount'])
                            messages.success(request, "Coupon applied successfully.")
                            return redirect('cart_app:checkout', cart_id=cart_id)
                        else:
                            messages.error(request, "coupen cannotbe able to applied in this amount")
                            return redirect('cart_app:checkout', cart_id=cart_id)
                    else:
                        messages.error(request, "coupen limit exceed")
                        return redirect('cart_app:checkout', cart_id=cart_id)


            else:
                           
                            messages.error(request, "Invalid coupon code. Please try again.")
                            return redirect('cart_app:checkout', cart_id=cart_id)
    
    
    return redirect('user_app:index')


def update_cart_item_quantity_ajax(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            product_id = data.get('product_id')
            varient_id = data.get('varient_id')
            action = data.get('action')
            varient_obj=Varient.objects.get(id=varient_id)

            cart_item = get_object_or_404(Cart_item, product_id=product_id, varient_id=varient_id)

            if action == 'increment':
                if cart_item.quantity >= varient_obj.stock:
                    return JsonResponse({'success': False, 'error': 'Invalid action or quantity'})
                else:
                    cart_item.quantity += 1
            elif action == 'decrement' and cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action or quantity'})

            cart_item.total_price = cart_item.quantity * cart_item.product.discount_price
            cart_item.save()
            cart_total = Cart_item.objects.filter(cart=cart_item.cart).aggregate(total=Sum('total_price'))['total']
            
            return JsonResponse({'success': True, 'new_quantity': cart_item.quantity, 'item_total_price': cart_item.total_price,'cart_subtotal': cart_total,'cart_total':cart_total+50})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


