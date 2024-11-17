from django.shortcuts import render,redirect
from product.models import *
from category.models import *
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count,Sum
import re
from address.models import Address
from user.models import CustomUser
from cart.models import *
from order.models import *
from django.contrib import messages
import math


# Create your views here.
def men_product(request):
                if request.user.is_authenticated and request.user.is_staff:
                    return redirect('admin_app:admin_home')
                if request.user.is_authenticated and request.user.is_block:
                    return redirect('user_app:user_logout')
                
                
                page = 1
                page = request.GET.get('page',1)
                products = Product.objects.filter(category_id=1)
                sub_category=Sub_Category.objects.filter(category_id=1)
                product_paginator = Paginator(products,8)
                


                products = product_paginator.get_page(page)
                context = {
                        'products':products,
                        'sub_category':sub_category,
                       
                    }
                return render(request,'user/men.html', context)
def men_category(request,id):
        products = Product.objects.filter(Q(category_id=1) & Q(sub_category=id) )
        
        context= {
                'products':products
        }

        return render(request,'user/casual.html',context)

def women_category(request,id):
        if request.user.is_authenticated and request.user.is_staff:
                return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        products = Product.objects.filter(Q(category_id=2) & Q(sub_category=id) )
        context= {
                'products':products
        }
        
        return render(request,'user/casual.html',context)
def women_product(request):
                if request.user.is_authenticated and request.user.is_staff:
                    return redirect('admin_app:admin_home')
                if request.user.is_authenticated and request.user.is_block:
                    return redirect('user_app:user_logout')
                page = 1
                page = request.GET.get('page',1)
                products = Product.objects.filter(category_id=2)
                sub_category=Sub_Category.objects.filter(category_id=2)
                product_paginator = Paginator(products,8)
                


                products = product_paginator.get_page(page)
                context = {
                        'products':products,
                        'sub_category':sub_category,
                       
                    }
                return render(request,'user/women.html', context)
def view_product(request,id):
          if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
          if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
          products = Product.objects.get(id=id)
          review_data = Product.objects.filter(id=id).aggregate(
          total_reviews=Count('productreview'),
          total_stars=Sum('productreview__rating')
    )

    #  total reviews and total stars from the aggregated data
          total_reviews = review_data['total_reviews'] or 0
          total_stars = review_data['total_stars'] or 0
    
          print(total_reviews)
          review=products.productreview_set.all()
        
          
          if total_reviews > 0:
                average_rating = math.floor(total_stars / total_reviews)
                
          else:
                average_rating = 0
          varients=products.varient.all()
          if  not products.is_listed or not products.category.is_listed or not products.category.is_listed:
                 context ={
                        
                 }
           
          
          context= {
                  'varients':varients,
                  'product':products,
                  'average_rating':average_rating,
                  'total_review':total_reviews,
                  'reviews': review,
                
          }
          return render(request,'user/view_product.html',context)
def account(request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        if not request.user.is_authenticated:
                return redirect('user_app:user_login')
         
        orders = request.user.orders.all().order_by('-id')
        user_email=request.user
        user_details=CustomUser.objects.get(email=user_email)
        address_obj=Address.objects.filter(user=user_details,default=True)
        address_obj1=Address.objects.filter(user=user_details,default=False)
        context={
                'user_details':user_details,
                'address':address_obj,
                'address1':address_obj1,
                'orders':orders,
        }
        
        return render(request,'user/account.html',context)
        
def add_address(request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        if request.method == 'POST':
               address_type = request.POST.get('address_type')
               country = request.POST.get('country')
               state = request.POST.get('state')
               street_address = request.POST.get('street_address')
               if request.POST.get('landmark'):
                    landmark = request.POST.get('landmark')
               else:
                       landmark = None
               postal_code = request.POST.get('postal_code')
               phone= request.POST.get('phone')
               alternative_phone=request.POST.get('alternative_phone')
               if request.POST.get('is_default') == "on":
                       is_default = True
               else:
                       is_default =False
               print(is_default)
               context={
                        
                        'address_type' : address_type,
                        'country' : country,
                        'state' : state,
                        'street_address' : street_address,
                        'landmark':landmark,
                        'postal_code' : postal_code,
                        'phone' : phone,
                        'alternative_phone' : alternative_phone,
                        
                        

               }
               if not re.match(r'^[1-9]+[0-9]{2,9}$', postal_code):
                    context['error'] = "Invalid postal code. Please enter a valid number between 2-9 digits."
                    return render(request, 'user/add_address.html', context)

               if not re.match(r'^[1-9]+[0-9]{9,12}$', phone):
                    context['error'] = "Invalid phone number. Please enter a valid 10 digit number."
                    return render(request, 'user/add_address.html', context)

               if alternative_phone and not re.match(r'^[1-9]+[0-9]{9,12}$', alternative_phone):
                    context['error'] = "Invalid alternative phone number. Please enter a valid 10 digit number."
                    return render(request, 'user/add_address.html', context)
               if is_default:
                         Address.objects.filter(user=request.user, default=True).update(default=False)


            # Redirect to account page upon success
               address_obj=Address(
                        user=request.user,
                        address_type = address_type,
                        country = country,
                        state = state,
                        street_address = street_address,
                        landmark=landmark,
                        postal_code = postal_code,
                        phone = phone,
                        alternative_phone = alternative_phone,
                        default=is_default
                )
               address_obj.save()
             
                
               return redirect('customer_app:account')
        
        return render(request,'user/add_address.html')
def edit_address(request,id):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        address_obj=Address.objects.get(id=id)
        print(address_obj.default)
        context={
                'landmark':address_obj.landmark,
                'postal_code':address_obj.postal_code,
               'phone':address_obj.phone,
               'street_address':address_obj.street_address,
               'alternative_phone':address_obj.alternative_phone,
               'default':address_obj.default,
               }
        if request.method=="POST":
               address_type = request.POST.get('address_type')
               country = request.POST.get('country')

               state = request.POST.get('state')
               street_address = request.POST.get('street_address')
               if request.POST.get('landmark'):
                    landmark = request.POST.get('landmark')
               else:
                       landmark = None
               postal_code = request.POST.get('postal_code')
               phone= request.POST.get('phone')
               alternative_phone=request.POST.get('alternative_phone')

               if request.POST.get('is_default') == "on":
                       
                       Address.objects.filter(user=request.user, default=True).update(default=False)
                       is_default = True
               else:
                       is_default =False
               context={
                'landmark':landmark,
                'postal_code':postal_code,
                'phone':phone,
                'street_address':street_address,

               'alternative_phone':alternative_phone,
               'default': is_default,
               }
               if not re.match(r'^[1-9]\d[0-9]{2,9}$', postal_code):
                    context['error'] = "Invalid postal code. Please enter a valid number between 2-9 digits."
                    return render(request, 'user/edit_address.html', context)

               if not re.match(r'^[1-9]\d{9,11}$', phone):
                    context['error'] = "Invalid phone number. Please enter a valid 10 digit number."
                    return render(request, 'user/edit_address.html', context)

               if alternative_phone and not re.match(r'^[1-9]\d[0-9]{9,11}$', alternative_phone):
                    context['error'] = "Invalid alternative phone number. Please enter a valid 10 digit number."
                    return render(request, 'user/edit_address.html', context)
              


               address_obj.address_type=address_type
               address_obj.country=country
               address_obj.state=state
               address_obj.street_address=street_address
               address_obj.landmark=landmark
               address_obj.postal_code=postal_code
               address_obj.phone=phone
               address_obj.alternative_phone=alternative_phone
               address_obj.default= is_default
               address_obj.save()
               return redirect('customer_app:account')
        return render(request,'user/edit_address.html',context)
def remove_address(request,address_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    address_item = Address.objects.get(id =address_id)
    address_item.delete()
    
    return redirect('customer_app:account')
def edit_user(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    user_details=CustomUser.objects.get(id=id)
    context={
           'username':user_details.username,
           'first_name':user_details.first_name,
           'last_name':user_details.last_name,
    }
    if request.method=="POST":
             
               
               username = request.POST.get('username')
               
               first_name = request.POST.get('first_name')
               
               last_name = request.POST.get('last_name')
               context={
                      'username':username,
                      'first_name':first_name,
                      'last_name':last_name
                      
                }
               
               if not re.match(r'^[A-Za-z]+$', username):
                    context['error'] = "user name should not contain numbers"
                    return render(request, 'user/edit_user_details.html', context)
               if not re.match(r'^[A-Za-z]+$', first_name):
                    context['error'] = "first name should not contain numbers"
                    return render(request, 'user/edit_user_details.html', context)
               if not re.match(r'^[A-Za-z]+$', last_name):
                    context['error'] = "lastname name should not contain numbers"
                    return render(request, 'user/edit_user_details.html', context)
               user_details.username=username
               user_details.first_name= first_name
               user_details.last_name=last_name
               user_details.save()

               
               return redirect('customer_app:account')
    return render(request,'user/edit_user_details.html',context)
def item_order(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    order = Order.objects.get(id = id)
    
    order_items = order.items.all().order_by('-id')
    print(order_items )
            
        # Handling the form submission to change order status
  
        
        # Calculating total price
    total_price = 0
    item_total_prices = []
    cart_total_with_discount = request.session.get('cart_total_with_discount', None)

    if cart_total_with_discount is None:
        print("hello")
    # Handle the case where no discount is applied
    # You could, for example, use the original cart total if available
        discount_price =  total_price# assuming `cart_total` is defined here
    else:
        print("hyy")
    # Proceed with the discounted total

    # Use cart_total_with_discount as needed
        discount_price =  cart_total_with_discount # 

        
    for item in order_items:
            # Check if product has an offer and calculate the item total
            if item.product.offer:
                item_total = item.quantity * item.product.discount_price
            else:
                item_total = item.quantity * item.product.price
                
            # Add item total to total order price
            total_price += item_total
            item_total_prices.append(item_total) # Store each item's total price

    context = {
            'order': order,
            'order_items': zip(order_items, item_total_prices),  # Pass both items and their individual total prices
            'total_price': total_price,
            'discount_price':discount_price,
            'items':order_items,
        }
    return render(request,'user/item_details.html',context)
def view_wallet(request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet_transaction = wallet.transactions.all()
        context={
                 'wallet':wallet,
                 'wallet_transaction':wallet_transaction
            }
        return render(request,'user/wallet.html',context)
      
    
    
        
    
               
               
    