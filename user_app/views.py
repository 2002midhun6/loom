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
    
    
    page = request.GET.get('page', 1)
    product_paginator = Paginator(products, 8)
    products = product_paginator.get_page(page)
    
    context = {
        'products': products,
        'sub_category': sub_category,
        'search_query': search_query,
        'selected_subcategory': selected_subcategory,
        'sort_by': sort_by,
    }
    return render(request, 'user/men.html', context)
def men_category(request,id):
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
        products = Product.objects.filter(Q(category_id=2) & Q(sub_category=id) )
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
    
    
    page = request.GET.get('page', 1)
    product_paginator = Paginator(products, 8)
    products = product_paginator.get_page(page)
    
    context = {
        'products': products,
        'sub_category': sub_category,
        'search_query': search_query,
        'selected_subcategory': selected_subcategory,
        'sort_by': sort_by,
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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.http import HttpResponse
from io import BytesIO




def generate_invoice_pdf(request, order, order_items, order_details):
    """
    Generate a PDF invoice for an order
    """
    
    buffer = BytesIO()
    
   
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    
    elements = []
    
 
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    ))
    
   
    elements.append(Paragraph("INVOICE", styles['CustomTitle']))
    elements.append(Paragraph(f"Order #{order.id}", styles['Heading2']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    
    elements.append(Paragraph("Bill To:", styles['Heading3']))
    elements.append(Paragraph(f"{order.user.first_name} {order.user.last_name}", styles['Normal']))
    elements.append(Paragraph(f"Email: {order.user.email}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {order_details.phone}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    
    elements.append(Paragraph("Shipping Address:", styles['Heading3']))
    elements.append(Paragraph(f"{order_details.street_address}", styles['Normal']))
    elements.append(Paragraph(f" {order_details.postal_code}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    
    table_data = [
        ['Product', 'Quantity', 'Price ($)', 'Total ($)'] 
    ]
    
    
    total_amount = 0
    for item in order_items:
       
        item_price = getattr(item, 'item_price', item.product.discount_price)
        item_total = item.quantity * item_price
        total_amount += item_total
        table_data.append([
            item.product.product_name,
            str(item.quantity),
            str(item_price),
            str(item_total)
        ])
    
    
    table_data.append(['', '', 'Subtotal:', str(total_amount)])
    if hasattr(order, 'discount') and order.discount:
        table_data.append(['', '', 'Final Total:', str(order.discount)])
    else:
        table_data.append(['', '', 'Final Total:', str(total_amount)])
    
   
    table = Table(table_data, colWidths=[4*inch, 1*inch, 1.25*inch, 1.25*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f"Order Status: {order.order_status.upper()}", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for your business!", styles['Heading3']))
    
    
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_order_{order.id}.pdf"'
    response.write(pdf)
    
    return response
@login_required
def item_order(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    
    order = Order.objects.get(id = id)
    order_details=OrderAddress.objects.get(order=order)


    if request.user.id != order.user.id:
        return redirect('user_app:user_logout')
    
    order_items = order.items.all().order_by('-id')
    print(order_items )
    if request.GET.get('download_pdf'):
        return generate_invoice_pdf(request, order, order_items, order_details)
            
       
    total_price = 0
    item_total_prices = []
    cart_total_with_discount = request.session.get('cart_total_with_discount', None)

    if cart_total_with_discount is None:
        print("hello")
    
        discount_price =  total_price
    else:
        print("hyy")
    
        discount_price =  cart_total_with_discount 

        
    for item in order_items:
            
            
            item_total = item.quantity * item.product.discount_price
            
                
            
            total_price += item_total
            item_total_prices.append(item_total)

    context = {
            'order': order,
            'order_items': zip(order_items, item_total_prices),  
            'total_price': total_price,
            'discount_price':discount_price,
            'items':order_items,
            'order_details': order_details,
        }
    return render(request,'user/item_details.html',context)
@login_required
def view_wallet(request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        wallet_transaction = wallet.transactions.all()
        context={
                 'wallet':wallet,
                 'wallet_transaction':wallet_transaction
            }
        return render(request,'user/wallet.html',context)
      
    
    
        
    

               
    