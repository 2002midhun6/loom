from django.shortcuts import render,redirect,get_object_or_404
from  . models import *
from product.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from address.models import Address


# def add_to_cart(request,id):
#     if request.user.is_authenticated and request.user.is_staff:
#         return redirect('admin_app:admin_home')
#     if request.user.is_authenticated and request.user.is_block:
#         return redirect('authentication_app:logout')
    
#     # Getting the user and the product

#     if request.method == 'POST':
#         user = request.user
#         product = get_object_or_404(Product, id=id)
        
#         varients_id = request.POST.get('var_id')
#         varient = Varient.objects.get(id=varients_id)
        
#         available_stock = varient.stock
#         print('this is varient id ', varients_id, available_stock)

#         # Check the user has already a cart or create new cart
#         cart, created = Cart.objects.get_or_create(user=user)
#         if created:
#             print('cart created')
#         else:
#             print('cart not creating')

#         # Calculate the total price (assuming product has a price field)
#         unit_price = varient.price if hasattr(varient, 'price') else product.price
#         total_price = unit_price  # For quantity 1

#         # Check if the products is already in the cart
#         cart_item, item_created = Cart_item.objects.get_or_create(
#             cart=cart,
#             product=product,
#             varient=varient,
#             defaults={
#                 'quantity': 1,
#                 'total_price': total_price
#             }
#         )

#         if item_created:
#             print(f"Created new item for product {cart_item.product.product_name} with quantity {cart_item.quantity}")
#         else:
#             # Increment the quantity if the item already exists in the cart
#             cart_item.quantity += 1
#             cart_item.total_price = unit_price * cart_item.quantity
#             cart_item.save()
#             print(f"Item already exists. Incrementing quantity to {cart_item.quantity}")

#         # Save the cart item
#         cart_item.save()
#         print(f"Cart item saved: {cart_item.product.product_name} with quantity {cart_item.quantity} and price {cart_item.total_price}")

#     # if product.offer:
#     #     cart_item.total_price = cart_item.quantity * product.discount_price
#     # else: 
#     #     cart_item.total_price = cart_item.quantity * product.price 

#         # cart_item.save()
#     # print(f"Cart item saved: {cart_item.product.product_name} with quantity {cart_item.quantity}")
        
#     # # request.session['coupon_applied'] = False  # Reset coupon status to recalculate discount
#     # # request.session['discount_amount'] = 0 
    
#     return redirect('cart_app:view_cart')
    
from django.db import transaction
from django.http import HttpResponse

def add_to_cart(request, id):
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
            
            # Get user and product
            user = request.user
            print(f"User: {user.username}")
            
            product = get_object_or_404(Product, id=id)
            print(f"Product found: {product.product_name}")
           
            varients_id = request.POST.get('var_id')
            print(f"Variant ID from POST: {varients_id}")
            
            varient = Varient.objects.get(id=varients_id)
            print(f"Variant found: {varient}")
            
            # Create or get cart with transaction
            with transaction.atomic():
                cart, cart_created = Cart.objects.get_or_create(user=user)
                print(f"Cart {'created' if cart_created else 'retrieved'} for user")
                print(f"Cart ID: {cart.id}")
                
                # Calculate price
                unit_price = varient.price if hasattr(varient, 'price') else product.price
                print(f"Unit price: {unit_price}")
                
                # Try to get existing cart item or create new one
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
                    print("Updating existing cart item")
                    cart_item.quantity += 1
                    cart_item.total_price = unit_price * cart_item.quantity
                    cart_item.save()
                else:
                    print("New cart item created")

                print(f"Cart item saved with ID: {cart_item.id}")
                print(f"Final quantity: {cart_item.quantity}")
                print(f"Final total price: {cart_item.total_price}")
                
            return redirect('cart_app:view_cart')
            
        except Product.DoesNotExist:
            print("Product not found")
            return HttpResponse("Product not found")
        except Varient.DoesNotExist:
            print("Variant not found")
            return HttpResponse("Variant not found")
        except Exception as e:
            print(f"Error occurred: {str(e)}")
           
    error_message = "select a size"

           # Add an error message 
    messages.error(request, error_message)
    return redirect('customer_app:view_product', id=id )


@login_required
def view_cart(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    if not request.user.is_authenticated:
        return redirect('user_app:user_login')
    
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    # List to hold the items that should stay in the cart
    filtered_cart_items = []
    
    # Loop through cart items and remove those that are not listed
    for item in cart_items:
        if  not item.product.is_listed or not item.product.category.is_listed or not item.product.category.is_listed:
            item.delete()
        else:
            # Check if quantity exceeds available stock
            if item.quantity > item.varient.stock:
                item.quantity = item.varient.stock
                item.save()
                messages.warning(request, f'Quantity for {item.product.product_name} has been adjusted to match available stock ({item.product.stock}).')
            filtered_cart_items.append(item)
    
    cart_items_with_prices = []
   
    # Calculate the total price for each item
    for item in filtered_cart_items:
        if item.product.offer:
            item.total_price = item.product.discount_price * item.quantity
        else:
           item.total_price = item.product.price * item.quantity
           
        
        cart_items_with_prices.append(item)
    
    # Calculate total cart value
    cart_total = sum(item.total_price for item in cart_items_with_prices)
    
    request.session['cart_total'] = float(cart_total)
    
    return render(request, 'user/cart.html', {
        'cart': cart,
        'cart_items': filtered_cart_items,
        'cart_total': cart_total,
        
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
    
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Get the cart item for the specified product
    cart_item = get_object_or_404(Cart_item, cart=cart, product=product,varient=varient)
    
    # Update quantity based on action
    if action == 'increment':
        # Check if incrementing would exceed available stock
        if cart_item.quantity >= varient.stock:
            messages.error(request, f'Cannot add more {product.product_name}. Maximum available stock ({product.available_stock}) reached.')
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

def checkout(request,cart_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    if not request.user.is_authenticated:
        return redirect('user_app:user_login')
    user_email = request.user.email
    user = CustomUser.objects.get(email = user_email)
    cart = Cart.objects.get(id = cart_id)
    cart_items = cart.items.all()
    # request.session['cart_id'] = cart_id
    
    cart_items_with_prices = []
    # Calculate the total price for each item
    for item in cart_items:
        if item.product.offer:
            item.total_price = item.product.discount_price * item.quantity
        else:
            item.total_price = item.product.price * item.quantity
    
        cart_items_with_prices.append(item)
    cart_total = sum(item.total_price for item in cart_items_with_prices)
    
    # # Apply coupon discount if applicable
    # discount = Decimal(request.session.get('discount_amount', 0))
    # cart_total_with_discount = float(cart_total) - float(discount)

    
    # request.session['cart_total'] = float(cart_total_with_discount)

    # coupon_code = request.session.get('coupon_code', '')
    
    #  # Wallet payment
    # wallet,created = Wallet.objects.get_or_create(user = user)
    # wallet_balance = wallet.balance
        
    address = Address.objects.get(user=request.user,default=True)
    print(address.phone)
    
    context = {
        'user':user,
        'cart_items':cart_items,
        'cart_total':cart_total,
        'address':address,
        # 'cart_total_with_discount':cart_total_with_discount,
        # 'coupon_code':coupon_code,
        # 'wallet_balance':wallet_balance,
    }
    return render(request,'user/checkout.html',context)


