from django.shortcuts import render,redirect
from user.models import CustomUser
from django.db.models import Q
from django.contrib.auth import login,authenticate,logout
from django.views.decorators.cache import never_cache
from product.models import *
from django.contrib import messages


# Create your views here.
@never_cache
def admin_home(request):
    if request.user.is_authenticated and request.user.is_staff:
         
      return render(request,'admin/admin_index.html')
    else:
          return redirect('user_app:index')
@never_cache
def user_details(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search')
        if query:
            user = CustomUser.objects.all().exclude(is_staff = True).filter(Q(first_name__icontains = query) | Q(email__icontains = query))
            return render(request,'admin/admin_user_management.html',{'user':user,'query':query})
        else:
            user=CustomUser.objects.all().exclude(is_staff = True)
            return render(request,'admin/admin_user_management.html',{'user':user})
    return redirect('user_app:index')
@never_cache
def user_block(request,id):
  if request.user.is_authenticated and request.user.is_staff:
    if request.method == 'POST':
        user = CustomUser.objects.get(id = id)
        print(user)
        if user.is_block:
            print(user.is_block)
            user.is_block = False
            user.save()
        elif not user.is_block:
            user.is_block = True
            user.save()
    return redirect('admin_app:user_details')
  return redirect('user_app:index')
@never_cache
def admin_logout(request):
 if request.user.is_authenticated and request.user.is_staff:
    if request.method=='POST':
        logout(request)
        return redirect('user_app:user_login')
 else:
          return redirect('user_app:index')
@never_cache
def admin_offer(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            offers = Offer.objects.all().filter(offer_title__icontains = query)
        else:
            offers = Offer.objects.all()
            
        return render(request,'admin/offer.html',{'offers':offers,'query':query})
    
    else:
        return redirect('user_app:index')
@never_cache
def add_offer(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            offer_title = request.POST.get('offer_title')
            offer_description = request.POST.get('offer_description')
            offer_percentage = request.POST.get('offer_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            offer = Offer(
                offer_title = offer_title,
                offer_description = offer_description,
                offer_percentage = offer_percentage,
                start_date = start_date,
                end_date = end_date
            )
            
            offer.save()
            messages.success(request,f'New offer {offer_title} added.')
            return redirect('admin_app:admin_offer')
            
        return render(request,'admin/add_offer.html')
    else:
        return redirect('user_app:index')
def edit_offer(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        offer = Offer.objects.get(id = id)    # Retrive data of the offer
        if request.method == 'POST':
            offer_title = request.POST.get('offer_title')
            offer_description = request.POST.get('offer_description')
            offer_percentage = request.POST.get('offer_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            offer.offer_title = offer_title
            offer.offer_description = offer_description
            offer.offer_percentage = offer_percentage
            offer.start_date = start_date
            offer.end_date = end_date
            
            
            offer.save()
            
            messages.success(request,f'Offer {offer_title} edited.')
            return redirect('admin_app:admin_offer')
        return render(request,'admin/edit_offer.html',{'offer':offer})
    else:
        return redirect('user_app:index')
def delete_offer(request,id):
   
    if request.user.is_authenticated and request.user.is_staff:
        offer = Offer.objects.get(id = id)
         # Retrive data of the offer
        if request.method == 'POST':
            offer_title = offer.offer_title
            offer.delete()
            
            messages.success(request,f'Offer {offer_title} removed.')
            return redirect('admin_app:admin_offer')
        return redirect('admin_app:admin_offer')
    else:
        return redirect('user_app:index')
def admin_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            coupons = Coupen.objects.all().filter(code__icontains = query)
        else:
            coupons = Coupen.objects.all()
            
        return render(request,'admin/coupon.html',{'coupons':coupons,'query':query})
    
    else:
        return redirect('user_app:index')
    
def add_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        
        if request.method == 'POST':
            code = request.POST.get('code')
            minimum_order_amount = request.POST.get('minimum_order_amount')
            maximum_order_amount = request.POST.get('maximum_order_amount')
            used_limit = request.POST.get('used_limit')
            expiry_date_str = request.POST.get('expiry_date')
            discount_amount = request.POST.get('discount_amount')
            
            # Converting string expiry date to datetime object.
            expiry_date_naive = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            expiry_date = timezone.make_aware(expiry_date_naive, timezone.get_current_timezone())
            
            coupon = Coupen(
                code = code,
                minimum_order_amount = minimum_order_amount,
                maximum_order_amount = maximum_order_amount,
                used_limit = used_limit,
                expiry_date = expiry_date,
                discount_amount = discount_amount,
            )
            coupon.save()
            
            messages.success(request,f'New coupon {code} has added.')
            return redirect('admin_app:admin_coupon')
         
        return render(request,'admin/add_coupon.html')
    
    else:
        return redirect('user_app:index')
    
    
def edit_coupon(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        coupon = Coupen.objects.get(id = id)
        
        if request.method == 'POST':
            code = request.POST.get('code')
            minimum_order_amount = request.POST.get('minimum_order_amount')
            maximum_order_amount = request.POST.get('maximum_order_amount')
            used_limit = request.POST.get('used_limit')
            expiry_date_str = request.POST.get('expiry_date')
            discount_amount = request.POST.get('discount_amount')
            
            # Converting string expiry date to datetime object.
            expiry_date_naive = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            expiry_date = timezone.make_aware(expiry_date_naive, timezone.get_current_timezone())
            
            coupon.code = code
            coupon.minimum_order_amount = minimum_order_amount
            coupon.maximum_order_amount = maximum_order_amount
            coupon.used_limit = used_limit
            coupon.expiry_date = expiry_date
            coupon.discount_amount = discount_amount
            
            coupon.save()
            
            messages.success(request,f'Coupon {code} edited.')
            return redirect('admin_app:admin_coupon')
        
        context = {
            'coupon':coupon
        }
        return render(request,'admin/edit_coupon.html',context)
    
    else:
        return redirect('user_app:index')
    
    
def remove_coupon(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        coupon = Coupen.objects.get(id = id)
        if request.method == 'POST':
            coupon.delete()
            messages.success(request,f'Coupon {coupon.code} removed.')
            return redirect('admin_app:admin_coupon')
    
    else:
        return redirect('user_app:index')
def admin_banner(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            banners = Banner.objects.all().filter(banner_name__icontains = query)
        else:
            banners = Banner.objects.all()
            
        return render(request,'admin/banner.html',{'banners':banners,'query':query})
    
    else:
        return redirect('user_app:home')
def add_banner(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            banner_name = request.POST.get('banner_name')
            description = request.POST.get('description')
            product_id = request.POST.get('product_id')
            price = request.POST.get('price')
            deal_price = request.POST.get('deal_price')
            banner_image = request.FILES.get('banner_image')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            print(product_id)
            product = Product.objects.get(id = product_id)
            
            new_banner = Banner(
                banner_name = banner_name,
                banner_description = description,
                product = product,
                price = price,
                deal_price = deal_price,
                banner_image = banner_image,
                start_date = start_date,
                end_date = end_date,
            )
            
            new_banner.save()
            messages.success(request,f'New banner {banner_name} added.')
            return redirect('admin_app:admin_banner')
        
        products = Product.objects.all()
        
        context = {
            'products':products,
        }
        
        return render(request,'admin/add_banner.html',context)
    else:
        return redirect('user_app:index')


def edit_banner(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        banner = Banner.objects.get(id = id)
        if request.method == 'POST':
            banner_name = request.POST.get('banner_name')
            description = request.POST.get('description')
            product_id = request.POST.get('product_id')
            price = request.POST.get('price')
            deal_price = request.POST.get('deal_price')
            banner_image = request.FILES.get('banner_image')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            product = Product.objects.get(id = product_id)
            
            banner.banner_name = banner_name
            banner.banner_description = description
            banner.product = product
            banner.price = price
            banner.deal_price = deal_price
            banner.start_date = start_date
            banner.end_date = end_date
            
            if banner_image:
                banner.banner_image = banner_image
                
            banner.save()
            
            messages.success(request,f' banner {banner_name} edited.')
            return redirect('admin_app:admin_banner')
        
        products = Product.objects.exclude(id = banner.product.id)
        
        context = {
            'banner':banner,
            'products':products,
        }
        
        return render(request,'admin/edit_banner.html',context)
    else:
        return redirect('user_app:index')
    
def remove_banner(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        banner = Banner.objects.get(id = id)    # Retrive Banner
        if request.method == 'POST':
            banner_name = banner.banner_name
            banner.delete()
            
            messages.success(request,f'Banner {banner_name} removed.')
            return redirect('admin_app:admin_banner')
        return redirect('admin_app:admin_banner')
    else:
        return redirect('user_app:index')
    

