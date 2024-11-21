from django.shortcuts import render,redirect
from user.models import CustomUser
from django.db.models import Q
from django.contrib.auth import login,authenticate,logout
from django.views.decorators.cache import never_cache
from product.models import *
from django.contrib import messages
from order.models import *
import re
from offer.models import *


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
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')


            end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            end_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone())
            
            start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            start_date = timezone.make_aware(start_date_naive, timezone.get_current_timezone())
            
            
            
            context={
                'offer_title':offer_title,
                'offer_description':offer_description,
                'offer_percentage':offer_percentage,
                'start_date':start_date,
                'end_date':end_date,
            }
            if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$',offer_title):
                    context['error'] = "offer  is not readable"
                    return render(request, 'admin/add_offer.html',context)
            if not re.match(r'^[a-zA-Z]+(\s+[a-zA-Z]*)*$', offer_description):
                    context['error'] = "discription should is not readable"
                    return render(request, 'admin/add_offer.html',context)
            if not re.match(r'^[0-9]+$', offer_percentage):
                    context['error'] = "percentage should be number"
                    return render(request, 'admin/add_offer.html',context)
            if end_date < timezone.now() or start_date < timezone.now() or end_date < start_date:
                    context['error'] = 'please check start and end date'
                    return render(request,'admin/add_offer.html',context)
          
          
            
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
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            end_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone())
            
            start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            start_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone())
            


            context={
                'offer_title':offer_title,
                'offer_description':offer_description,
                'offer_percentage':offer_percentage,
                'start_date':start_date,
                'end_date':end_date,

           
            }
            if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$',context):
                    context['error'] = "offer  is not readable"
                    return render(request, 'admin/add_offer.html',context)
            if not re.match(r'^[a-zA-Z]+(\s+[a-zA-Z]*)*$', offer_description):
                    context['error'] = "discription should is not readable"
                    return render(request, 'admin/add_offer.html',context)
            if not re.match(r'^[0-9]+$', offer_percentage):
                    context['error'] = "percentage should be number"
                    return render(request, 'admin/add_offer.html',context)
          
            
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
            

            context={
                'code':code,
                'minimum_order_amount':minimum_order_amount,
                'maximum_order_amount':maximum_order_amount,
                'used_limit':used_limit,
                'expiry_date':expiry_date,
                'discount_amount':discount_amount,
                  


           
            }
            min= float(minimum_order_amount)
            max= float(maximum_order_amount)
            discount_am=float(discount_amount)
                
            if not re.match(r'^([a-zA-Z]+[0-9]*)+$', code):
                    context['error'] = "should not contain symbols"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^[0-9]+$',minimum_order_amount ):
                    context['error'] = "minimum amound must be a number"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^[0-9]+$', maximum_order_amount):
                    context['error'] = "maximum amount be a number"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^[1-9]+[0-9]*$',used_limit):
                    context['error'] = "user limit should be one or more than"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^[1-9]+[0-9]*$',discount_amount):
                    context['error'] = "discount should be a number"
                    return render(request, 'admin/add_coupen.html', context)
            if expiry_date < timezone.now():
                    context['error'] = 'Expiry date cannot be a past time!'
                    return render(request,'admin/add_coupen.html',context)
            if max<min:
                   context['error'] = 'minimum amount cannot be graeter than maximum amount'
                   return render(request,'admin/add_coupen.html',context)
                 
            if min<=discount_am:
                  context['error'] = 'minimum amount equal to discount'
                  return render(request,'admin/add_coupen.html',context)
                 
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
         
        return render(request,'admin/add_coupen.html')
    
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
            context={
                'code':code,
                'minimum_order_amount':minimum_order_amount,
                'maximum_order_amount':maximum_order_amount,
                'used_limit':used_limit,
                'discount_amount':discount_amount,
                'expiry_date':expiry_date,
                    }
            min_amount = float(minimum_order_amount)
            max_amount = float(maximum_order_amount)
            discount_am=float(discount_amount)
            limit = int(used_limit)
            if not re.match(r'^([a-zA-Z]+[0-9]*)+$', code):
                    context['error'] = "should not contain symbols"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^\d*\.?\d+$',minimum_order_amount):
                    context['error'] = "minimum amound must be a number"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^\d*\.?\d+$',maximum_order_amount):
                    context['error'] = "maximum amount be a number"
                    return render(request, 'admin/add_coupen.html', context)
            if not re.match(r'^[1-9]+[0-9]*$',used_limit):
                    context['error'] = "user limit should be one or more than"
                    return render(request, 'admin/add_coupen.html', context)
            
            if not re.match(r'^\d*\.?\d+$',discount_amount):
                    context['error'] = "discount should be greter than zero"
                    return render(request, 'admin/add_coupen.html', context)
            if expiry_date < timezone.now():
                    context['error'] = 'Expiry date cannot be a past time!'
                    return render(request,'admin/add_coupen.html',context)
            if  max_amount < min_amount: 
                context['error'] = "minimum order amount cannnot be greater"
                return render(request, 'admin/add_coupen.html', context)
            if min_amount<=discount_am:
                  context['error'] = 'minimum amount equal to discount'
                  return render(request,'admin/add_coupen.html',context)
            
                 
                    
            
            
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
        return render(request,'admin/edit_coupen.html',context)
    
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
            banner_image = request.FILES.get('banner_image')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
           
            end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            end_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone())
            
            start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            start_date = timezone.make_aware(start_date_naive, timezone.get_current_timezone())
            context={
                 'banner_name':banner_name,
                 'description':description,
                'start_date':start_date,
                'end_date':end_date,
                'banner_image':banner_image,
                    }
            if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$',banner_name):
                    context['error'] = "banner  is not readable"
                    return render(request, 'admin/add_banner.html',context)
            if not re.match(r'^[a-zA-Z]+(\s+[a-zA-Z]*)*$', description):
                    context['error'] = "discription should is not readable"
                    return render(request, 'admin/add_banner.html',context)
            
            if end_date < timezone.now() or start_date < timezone.now() or end_date < start_date:
                    context['error'] = 'please check start and end date'
                    return render(request,'admin/add_banner.html',context)

            new_banner = Banner(
                banner_name = banner_name,
                banner_description = description,
                banner_image = banner_image,
                start_date = start_date,
                end_date = end_date,
            )
            
            new_banner.save()
            messages.success(request,f'New banner {banner_name} added.')
            return redirect('admin_app:admin_banner')
        
        banner = Banner.objects.all()
        
        context = {
            'banner':banner,
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
           
            banner_image = request.FILES.get('banner_image')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            end_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone())
            
            start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            
            # Converting naive datetime to timezone-aware datetime
            start_date = timezone.make_aware(end_date_naive, timezone.get_current_timezone())
            
            
            context={
                 'banner_name':banner_name,
                 'description':description,
                'start_date':start_date,
                'end_date':end_date,
                'banner_image':banner_image,
                    }
            if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$',banner_name):
                    context['error'] = "banner  is not readable"
                    return render(request, 'admin/add_banner.html',context)
            if not re.match(r'^[a-zA-Z]+(\s+[a-zA-Z]*)*$', description):
                    context['error'] = "discription should is not readable"
                    return render(request, 'admin/add_banner.html',context)
            
            if end_date < timezone.now() or start_date < timezone.now() or end_date < start_date:
                    context['error'] = 'please check start and end date'
                    return render(request,'admin/add_banner.html',context)
            
            banner.banner_name = banner_name
            banner.banner_description = description
            banner.start_date = start_date
            banner.end_date = end_date
            
            if banner_image:
                banner.banner_image = banner_image
                
            banner.save()
            
            messages.success(request,f' banner {banner_name} edited.')
            return redirect('admin_app:admin_banner')
        
       
        context = {
            'banner':banner,
           
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
def admin_orders(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            orders = Order.objects.filter(id__icontains = query)        
        else:
            orders = Order.objects.all().order_by('-id')
        context = {
            'orders':orders,
            'query':query,
        }
        return render(request,'admin/order.html',context)
    
    else:
        return redirect('user_app:home')

def show_order(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        order = Order.objects.get(id = id)
         
        order_details=OrderAddress.objects.get(order=order)
        order_items = order.items.all()
        print(order_items )
       

        # Handling the form submission to change order status
        if request.method == "POST":
            new_status = request.POST.get('order_status')
            if new_status in dict(STATUS):  # Ensure the status is valid
                order.order_status = new_status
                order.save()
                messages.success(request, "Order status updated successfully.")
            else:
                messages.error(request, "Invalid order status.")
        
        
        # Calculating total price
        total_price = 0
        item_total_prices = []
        
        for item in order_items:
            # Check if product has an offer and calculate the item total
            
            item_total = item.quantity * item.product.discount_price
            
                
            # Add item total to total order price
            total_price += item_total
            item_total_prices.append(item_total)  # Store each item's total price

        context = {
            'order': order,
            'order_items': zip(order_items, item_total_prices),  # Pass both items and their individual total prices
            'total_price': total_price,
            'status_choices': STATUS,
            'items':order_items,
            'order_details':order_details
        }
        return render(request,'admin/show_order.html',context)
    
    else:
        return redirect('user_app:index')
#------admin sale#
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear, Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import logging
import pytz

logger = logging.getLogger(__name__)

class SalesReportView(TemplateView):
    template_name = 'admin/sales_report.html'
    timezone = pytz.timezone('Asia/Kolkata')

    def get(self, request, *args, **kwargs):
        download_format = request.GET.get('download_format')
        if download_format:
            start_date, end_date = self.get_date_range()
            sales_data = self.get_sales_data(start_date, end_date)
            
            if download_format == 'excel':
                return self.download_excel(sales_data)
            elif download_format == 'pdf':
                return self.download_pdf(sales_data)
        
        return super().get(request, *args, **kwargs)

    def get_date_range(self):
        report_type = self.request.GET.get('report_type', 'daily')
        current_time = timezone.localtime(timezone.now(), self.timezone)
        today = current_time.date()
        
        try:
            if report_type == 'custom':
                start_date = self.request.GET.get('start_date')
                end_date = self.request.GET.get('end_date')
                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
                    return start, end

            date_ranges = {
                'daily': (today - timedelta(days=1), today + timedelta(days=1)),
                'weekly': (today - timedelta(days=7), today + timedelta(days=1)),
                'monthly': (today.replace(day=1), (today + timedelta(days=1))),
                'yearly': (today.replace(month=1, day=1), today + timedelta(days=1))
            }
            
            return date_ranges.get(report_type, (today, today + timedelta(days=1)))
        except Exception as e:
            logger.error(f"Error in get_date_range: {str(e)}")
            return today, today + timedelta(days=1)

    def get_sales_data(self, start_date, end_date):
        try:
            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time()),
                self.timezone
            )
            end_datetime = timezone.make_aware(
                datetime.combine(end_date, datetime.min.time()),
                self.timezone
            )

            # Get the appropriate truncation function
            trunc_func = self.get_trunc_function()
            
            # Base queryset for orders
            base_queryset = OrderItems.objects.filter(
                order__order_date__gte=start_datetime,
                order__order_date__lt=end_datetime
            )

            # Aggregate sales data
            sales_data = base_queryset.annotate(
                period=trunc_func('order__order_date', tzinfo=self.timezone)
            ).values('period').annotate(
                total_orders=Count('order', distinct=True),
                delivered_orders=Count('order', distinct=True, 
                    filter=Q(order__order_status='delivered')),
                pending_orders=Count('order', distinct=True, 
                    filter=Q(order__order_status='pending')),
                cancelled_orders=Count('order', distinct=True, 
                    filter=Q(order__order_status='cancelled')),
                total_amount=Coalesce(
                    Sum(F('price') * F('quantity')),
                    Decimal('0.00')
                ),
                total_discount=Coalesce(
                    Sum('order__discount'),
                    Decimal('0.00')
                )
            ).order_by('period')

            processed_data = []
            for item in sales_data:
                processed_item = {
                    'period': item['period'],
                    'total_orders': item['total_orders'],
                    'delivered_orders': item['delivered_orders'],
                    'pending_orders': item['pending_orders'],
                    'cancelled_orders': item['cancelled_orders'],
                    'total_amount': item['total_amount'],
                    'discount': item['total_discount'],
                    'net_amount': item['total_amount'] - item['total_discount']
                }
                processed_data.append(processed_item)

            return processed_data

        except Exception as e:
            logger.error(f"Error in get_sales_data: {str(e)}", exc_info=True)
            return []

    def get_trunc_function(self):
        report_type = self.request.GET.get('report_type', 'daily')
        trunc_functions = {
            'daily': TruncDate,
            'weekly': TruncWeek,
            'monthly': TruncMonth,
            'yearly': TruncYear
        }
        return trunc_functions.get(report_type, TruncDate)

    def prepare_data_for_excel(self, sales_data):
        excel_data = []
        for item in sales_data:
            row = {
                'Period': item['period'].strftime('%Y-%m-%d'),
                'Total Orders': item['total_orders'],
                'Delivered Orders': item['delivered_orders'],
                'Pending Orders': item['pending_orders'],
                'Cancelled Orders': item['cancelled_orders'],
                'Total Amount': float(item['total_amount']),
                'Discount': float(item['discount']),
                'Net Amount': float(item['net_amount'])
            }
            excel_data.append(row)
        return excel_data

    def download_excel(self, sales_data):
        try:
            df = pd.DataFrame(self.prepare_data_for_excel(sales_data))
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sales Report')
            
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
            return response
        except Exception as e:
            logger.error(f"Error generating Excel file: {str(e)}", exc_info=True)
            return HttpResponse("Error generating Excel file", status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            start_date, end_date = self.get_date_range()
            sales_data = self.get_sales_data(start_date, end_date)
            
            # Calculate overall statistics
            overall_stats = {
                'total_orders': sum(item['total_orders'] for item in sales_data),
                'delivered_orders': sum(item['delivered_orders'] for item in sales_data),
                'pending_orders': sum(item['pending_orders'] for item in sales_data),
                'cancelled_orders': sum(item['cancelled_orders'] for item in sales_data),
                'total_amount': sum(Decimal(str(item['total_amount'])) for item in sales_data),
                'total_discount': sum(Decimal(str(item['discount'])) for item in sales_data),
                'net_amount': sum(Decimal(str(item['net_amount'])) for item in sales_data),
            }

            context.update({
                'sales_data': sales_data,
                'report_type': self.request.GET.get('report_type', 'daily'),
                'start_date': start_date,
                'end_date': end_date - timedelta(days=1),
                'overall_stats': overall_stats
            })
            
        except Exception as e:
            logger.error(f"Error in get_context_data: {str(e)}", exc_info=True)
            context.update({
                'error_message': 'An error occurred while generating the report.',
                'sales_data': [],
                'overall_stats': {}
            })
        
        return context