from django.shortcuts import render,redirect
from product.models import *
from category.models import *
from django.core.paginator import Paginator
from django.db.models import Q
import re
from address.models import Address
from user.models import CustomUser
from cart.models import *



# Create your views here.
def men_product(request):
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
          varients=products.varient.all()
          if  not products.is_listed or not products.category.is_listed or not products.category.is_listed:
                 context ={
                        
                 }
           
          
          context= {
                  'varients':varients,
                  'product':products,
                
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
               if not re.match(r'^[0-9]{2,9}$', postal_code):
                    context['error'] = "Invalid postal code. Please enter a valid number between 2-9 digits."
                    return render(request, 'user/add_address.html', context)

               if not re.match(r'^[0-9]{10,13}$', phone):
                    context['error'] = "Invalid phone number. Please enter a valid 10 digit number."
                    return render(request, 'user/add_address.html', context)

               if alternative_phone and not re.match(r'^[0-9]{10,13}$', alternative_phone):
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
                'address':address_obj
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
           'user_details':user_details,
    }
    if request.method=="POST":
               
               
               username = request.POST.get('username')
               
               first_name = request.POST.get('first_name')
               
               last_name = request.POST.get('last_name')
               
               user_details.username=username
               user_details.first_name= first_name
               user_details.last_name=last_name
               user_details.save()

               
               return redirect('customer_app:account')
    return render(request,'user/edit_user_details.html',context)

        
    
               
               
    