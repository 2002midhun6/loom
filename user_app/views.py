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
from django.contrib.auth.decorators import login_required
from datetime import datetime
import pytz





def men_product(request):
    kolkata_tz = pytz.timezone('Asia/Kolkata')
        
    now = datetime.now(kolkata_tz)
    
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    
    products = Product.objects.filter(category_id=2)
    for i in products:
        if i.offer and i.offer.end_date < now:
            i.offer = None
            i.save()
        elif i.sub_category.offer and i.sub_category.offer.end_date < now:
            i.offer = None
            i.sub_category.offer = None
            i.sub_category.save()
             
    sub_category = Sub_Category.objects.filter(category_id=2)
    
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
        for i in products:
            if i.offer and i.offer.end_date < now:
                i.offer = None
                i.save()
            elif i.sub_category.offer and i.sub_category.offer.end_date < now:
                i.offer = None
                i.sub_category.offer = None
                i.sub_category.save()
    
    
    selected_subcategory = request.GET.get('subcategory')
    if selected_subcategory and selected_subcategory !="None":
        products = products.filter(sub_category_id=selected_subcategory)
        for i in products:
            if i.offer and i.offer.end_date < now:
                i.offer = None
                i.save()
            elif i.sub_category.offer and i.sub_category.offer.end_date < now:
                i.offer = None
                i.sub_category.offer = None
                i.sub_category.save()
    
    
    sort_by = request.GET.get('sort', 'newest')  
    if sort_by == 'newest':
        products = products.order_by('-created_at')
         
         
    elif sort_by == 'name_asc':
        products = products.order_by('product_name')
    elif sort_by == 'name_desc':
        products = products.order_by('-product_name')
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            price_min = ''
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
             price_max = ''
    
    page = request.GET.get('page', 1)
    product_paginator = Paginator(products, 8)
    products = product_paginator.get_page(page)
    
    context = {
        'products': products,
        'sub_category': sub_category,
        'search_query': search_query,
        'selected_subcategory': selected_subcategory,
        'sort_by': sort_by,
        'price_min': price_min,   
        'price_max': price_max,
    }
    return render(request, 'user/men.html', context)
def men_category(request,id):
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        
        now = datetime.now(kolkata_tz)
    
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        products = Product.objects.filter(Q(category_id=2) & Q(sub_category=id) )
        for i in products:
            if i.offer and i.offer.end_date < now:
                i.offer = None
                i.save()
            elif i.sub_category.offer and i.sub_category.offer.end_date < now:
                i.offer = None
                i.sub_category.offer = None
                i.save()
       
        context= {
                'products':products
        }

        return render(request,'user/casual.html',context)

def women_category(request,id):
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        
        now = datetime.now(kolkata_tz)
        if request.user.is_authenticated and request.user.is_staff:
                return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        products = Product.objects.filter(Q(category_id=1) & Q(sub_category=id) )
        for i in products:
            if i.offer and i.offer.end_date < now:
                i.offer = None
                i.save()
            elif i.sub_category.offer and i.sub_category.offer.end_date < now:
                i.offer = None
                i.sub_category.offer = None
                i.sub_category.save()
        context= {
                'products':products
        }
        
        return render(request,'user/casual.html',context)
def women_product(request):
    kolkata_tz = pytz.timezone('Asia/Kolkata')
        
    now = datetime.now(kolkata_tz)
                
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    
    products = Product.objects.filter(category_id=1)
    for i in products:
            if i.offer and i.offer.end_date < now:
                i.offer = None
                i.save()
            elif i.sub_category.offer and i.sub_category.offer.end_date < now:
                i.offer = None
                i.sub_category.offer = None
                i.sub_category.save()
    sub_category = Sub_Category.objects.filter(category_id=1)
    
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    
    selected_subcategory = request.GET.get('subcategory')
    if selected_subcategory:
        products = products.filter(sub_category_id=selected_subcategory)
        for i in products:
            if i.offer and i.offer.end_date < now:
                i.offer = None
                i.save()
            elif i.sub_category.offer and i.sub_category.offer.end_date < now:
                i.offer = None
                i.sub_category.offer = None
                i.sub_category.save()
        
    
    sort_by = request.GET.get('sort', 'newest')  
    if sort_by == 'newest':
        products = products.order_by('-created_at') 
    elif sort_by == 'name_asc':
        products = products.order_by('product_name')
    elif sort_by == 'name_desc':
        products = products.order_by('-product_name')
    
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            price_min = ''
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            price_max = ''
    page = request.GET.get('page', 1)
    product_paginator = Paginator(products, 8)
    products = product_paginator.get_page(page)
    
    context = {
        'products': products,
        'sub_category': sub_category,
        'search_query': search_query,
        'selected_subcategory': selected_subcategory,
        'sort_by': sort_by,
        'price_min': price_min,   
        'price_max': price_max,
    }
    return render(request, 'user/women.html', context)
def view_product(request,id):
          kolkata_tz = pytz.timezone('Asia/Kolkata')
       
          now = datetime.now(kolkata_tz)
          if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
          if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
          products = Product.objects.get(id=id)
          
          offer_ended=False
          if products.offer and products.offer.end_date < now:
                products.offer = None
                products.save()
                offer_ended = True
          elif products.sub_category.offer and products.sub_category.offer.end_date < now:
                products.offer = None
                products.sub_category.offer = None
                products.sub_category.save()
                offer_ended = True
          review_data = Product.objects.filter(id=id).aggregate(
          total_reviews=Count('productreview'),
          total_stars=Sum('productreview__rating')
    )

    
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
                  'offer_ended':offer_ended,
                
          }
          return render(request,'user/view_product.html',context)
@login_required
def account(request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        if not request.user.is_authenticated:
                return redirect('user_app:user_login')
        from user.models import UserReferral
        referral = UserReferral.objects.filter(user=request.user).first()
        referral_code = referral.referral_code if referral else "Not available"
         
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
                'referral_code': referral_code,

        }
        
        return render(request,'user/account.html',context)
@login_required       
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
               next_url = request.session.pop('next', None)
               if next_url:
                    return redirect(next_url)
               return redirect('customer_app:account')
             
                
               
        
        return render(request,'user/add_address.html')
@login_required
def edit_address(request,id):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
        address_obj=Address.objects.get(id=id)
        if request.user.id != address_obj.user.id:
             return redirect('user_app:user_logout')
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
               next_url = request.session.pop('next', None)
               if next_url:
                    return redirect(next_url)
            
               return redirect('customer_app:account')
        return render(request,'user/edit_address.html',context)
@login_required
def remove_address(request,address_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    address_item = Address.objects.get(id =address_id)
    address_item.delete()
    
    return redirect('customer_app:account')
@login_required
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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from django.http import HttpResponse
from io import BytesIO
from decimal import Decimal
from datetime import datetime


def generate_invoice_pdf(request, order, order_items, order_details):
    """
    Generate a PDF invoice for an order - excludes canceled/returned items,
    shows original price, discounts, and final amount paid.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=60,
        leftMargin=60,
        topMargin=60,
        bottomMargin=60
    )

    elements = []
    styles = getSampleStyleSheet()

    # ── Custom styles ──────────────────────────────────────────────
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1a1a2e'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
        spaceBefore=10,
    ))
    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#444444'),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        name='BoldRight',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
    ))

    # ── HEADER: Title + Order Meta ─────────────────────────────────
    header_data = [[
        Paragraph("INVOICE", styles['InvoiceTitle']),
        Paragraph(
            f"<b>Order #</b>{order.id}<br/>"
            f"<b>Date:</b> {order.order_date.strftime('%B %d, %Y')}<br/>"
            f"<b>Status:</b> {order.order_status.upper()}",
            styles['SmallText']
        )
    ]]
    header_table = Table(header_data, colWidths=[4 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a1a2e'), spaceAfter=12))

    # ── BILL TO + SHIPPING ADDRESS ─────────────────────────────────
    bill_data = [[
        [
            Paragraph("BILL TO", styles['SectionHeader']),
            Paragraph(f"{order.user.first_name} {order.user.last_name}", styles['SmallText']),
            Paragraph(f"Email: {order.user.email}", styles['SmallText']),
            Paragraph(f"Phone: {order_details.phone}", styles['SmallText']),
        ],
        [
            Paragraph("SHIP TO", styles['SectionHeader']),
            Paragraph(f"{order_details.street_address}", styles['SmallText']),
            Paragraph(f"Pincode: {order_details.postal_code}", styles['SmallText']),
            Paragraph(f"Phone: {order_details.phone}", styles['SmallText']),
        ]
    ]]
    bill_table = Table(bill_data, colWidths=[3.75 * inch, 3.75 * inch])
    bill_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 16))

    # ── ORDER ITEMS TABLE (exclude canceled and returned) ──────────
    elements.append(Paragraph("ORDER ITEMS", styles['SectionHeader']))

    col_widths = [3.2 * inch, 0.7 * inch, 1.1 * inch, 1.1 * inch, 1.4 * inch]
    table_data = [[
        Paragraph('<b>Product</b>', styles['SmallText']),
        Paragraph('<b>Qty</b>', styles['SmallText']),
        Paragraph('<b>Unit Price</b>', styles['SmallText']),
        Paragraph('<b>Original</b>', styles['SmallText']),
        Paragraph('<b>Amount (₹)</b>', styles['SmallText']),
    ]]

    # Convert order_items queryset - filter out canceled and returned
    if hasattr(order_items, 'filter'):
        # It's a queryset
        active_items = order_items.exclude(cancel_status='canceled').exclude(return_status='returned')
    else:
        # It's already evaluated (list/zip etc) - re-fetch from order
        active_items = order.items.exclude(cancel_status='canceled').exclude(return_status='returned')

    original_subtotal = Decimal('0')
    paid_subtotal = Decimal('0')

    for item in active_items:
        item_price = item.item_price or item.product.discount_price
        original_price = item.product.price  # full original price before any discount
        item_original = Decimal(str(item.quantity)) * Decimal(str(original_price))
        item_paid = Decimal(str(item.quantity)) * Decimal(str(item_price))

        original_subtotal += item_original
        paid_subtotal += item_paid

        table_data.append([
            Paragraph(item.product.product_name, styles['SmallText']),
            Paragraph(str(item.quantity), styles['SmallText']),
            Paragraph(f"rs:{item_price}", styles['SmallText']),
            Paragraph(f"rs:{item_original}", styles['SmallText']),
            Paragraph(f"rs:{item_paid}", styles['SmallText']),
        ])

    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dddddd')),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 14))

    # ── PRICING SUMMARY ───────────────────────────────────────────
    SHIPPING = Decimal('50')
    product_discount = original_subtotal - paid_subtotal  # offer/product-level discount

    # Coupon discount
    coupon_discount = Decimal('0')
    if order.coupons:
        coupon_discount = paid_subtotal + SHIPPING - (order.discount or Decimal('0'))
        coupon_discount = max(coupon_discount, Decimal('0'))

    final_total = order.discount or paid_subtotal

    summary_data = [
        ['Original Price (MRP):', f"rs:{original_subtotal:.2f}"],
    ]

    if product_discount > 0:
        summary_data.append(['Product / Offer Discount:', f"- rs:{product_discount:.2f}"])

    summary_data.append(['Subtotal after offers:', f"rs:{paid_subtotal:.2f}"])
    summary_data.append(['Shipping:', f"rs:{SHIPPING:.2f}"])

    if coupon_discount > 0:
        summary_data.append([f"Coupon ({order.coupons.code}):", f"- rs:{coupon_discount:.2f}"])

    summary_data.append(['TOTAL PAID:', f"rs:{final_total:.2f}"])

    summary_table = Table(summary_data, colWidths=[5.5 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        # Last row (TOTAL PAID) bold with top border
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1a1a2e')),
        # Highlight product discount in green
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#2e7d32')) if product_discount > 0 else ('NOSPLIT', (0, 0), (-1, -1)),
    ]))
    elements.append(summary_table)

    # ── FOOTER ────────────────────────────────────────────────────
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'), spaceAfter=8))
    elements.append(Paragraph(
        "Thank you for shopping with us! For any queries, please contact our support.",
        styles['SmallText']
    ))
    elements.append(Paragraph(
        f"Invoice generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles['SmallText']
    ))

    # ── BUILD ─────────────────────────────────────────────────────
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.pdf"'
    response.write(pdf)

    return response
# @login_required
# def item_order(request,id):
#     if request.user.is_authenticated and request.user.is_staff:
#         return redirect('admin_app:admin_home')
#     if request.user.is_authenticated and request.user.is_block:
#         return redirect('user_app:user_logout')
    
    
#     order = Order.objects.get(id = id)
#     order_details=OrderAddress.objects.get(order=order)


#     if request.user.id != order.user.id:
#         return redirect('user_app:user_logout')
    
#     order_items = order.items.all().order_by('-id')
#     print(order_items )
#     if request.GET.get('download_pdf'):
#         return generate_invoice_pdf(request, order, order_items, order_details)
            
       
#     total_price = 0
#     item_total_prices = []
#     cart_total_with_discount = request.session.get('cart_total_with_discount', None)

#     if cart_total_with_discount is None:
#         print("hello")
    
#         discount_price =  total_price
#     else:
#         print("hyy")
    
#         discount_price =  cart_total_with_discount 

        
#     for item in order_items:
            
            
#             item_total = item.quantity * item.product.discount_price
            
                
            
#             total_price += item_total
#             item_total_prices.append(item_total)
#     coupon_savings = (float(total_price)+50) - float(order.discount) if order.discount else 0
#     print(coupon_savings)

#     context = {
#             'order': order,
#             'order_items': zip(order_items, item_total_prices),  
#             'total_price': total_price,
#             'discount_price':discount_price,
#             'items':order_items,
#             'order_details': order_details,
#             'coupon_savings': coupon_savings,
#         }
#     return render(request,'user/item_details.html',context)
from decimal import Decimal

@login_required
def item_order(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')

    order = Order.objects.get(id=id)
    order_details = OrderAddress.objects.get(order=order)

    if request.user.id != order.user.id:
        return redirect('user_app:user_logout')

    if request.GET.get('download_pdf'):
        order_items = order.items.all().order_by('-id')
        return generate_invoice_pdf(request, order, order_items, order_details)

    order_items = order.items.all().order_by('-id')

    original_total = Decimal('0')
    active_total = Decimal('0')      # total excluding canceled items
    canceled_total = Decimal('0')    # total of only canceled items
    item_total_prices = []

    for item in order_items:
        # Use Decimal for everything
        item_total = Decimal(item.quantity) * item.product.discount_price   # assuming discount_price is Decimal
        item_total_prices.append(item_total)
        
        original_total += item_total
        
        if item.cancel_status == 'canceled':
            canceled_total += item_total
        else:
            active_total += item_total

    SHIPPING = Decimal('50')

    # Coupon savings
    coupon_savings = (original_total + SHIPPING) - (order.discount or Decimal('0'))

    # Amount paid for products only (excluding shipping)
    amount_paid_for_products = (order.discount or Decimal('0')) - SHIPPING

    # Calculate active proportion safely using Decimal
    if original_total > 0:
        active_proportion = active_total / original_total
    else:
        active_proportion = Decimal('1')

    # If no active items remain, effective total is 0
    if active_total == 0:
        effective_total = Decimal('0')
    else:
        # Active items' share of product cost + full shipping
        effective_total = round(
            (active_proportion * amount_paid_for_products) + SHIPPING, 
            2
        )

    canceled_savings = (order.discount or Decimal('0')) - effective_total

    context = {
        'order': order,
        'order_items': zip(order_items, item_total_prices),
        'items': order_items,
        'total_price': original_total,
        'active_total': active_total.quantize(Decimal('0.01')),
        'canceled_total': canceled_total.quantize(Decimal('0.01')),
        'effective_total': effective_total.quantize(Decimal('0.01')),
        'canceled_savings': canceled_savings.quantize(Decimal('0.01')),
        'order_details': order_details,
        'coupon_savings': coupon_savings.quantize(Decimal('0.01')) if coupon_savings > 0 else Decimal('0'),
    }
    
    return render(request, 'user/item_details.html', context)
@login_required
def view_wallet(request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet_transaction = wallet.transactions.all()
        context={
                 'wallet':wallet,
                 'wallet_transaction':wallet_transaction
            }
        return render(request,'user/wallet.html',context)
      
    
    
        
    

               
    