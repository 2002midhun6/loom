from django.shortcuts import render,redirect
from  . models import *
from category.models import *
from django.db.models import F
import re
from django.views.decorators.cache import never_cache
from datetime import datetime
import pytz


# Create your views here.
@never_cache
def admin_product_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        product = Product.objects.all()
        category=Category.objects.all()
        return render(request,'admin/product.html',{'product':product,'categories':category})
    else:
        return redirect('user_app:index')
@never_cache
def product_list(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            product = Product.objects.get(id = id)
            if product.is_listed:
                product.is_listed = False
                product.save()
            elif not product.is_listed:
                product.is_listed = True
                product.save()
        return redirect('product_app:admin_product_view')
    else:
        return redirect('user_app:index')
@never_cache
def add_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        
        now = datetime.now(kolkata_tz)
        if request.method=="POST":
                
                product_name = request.POST.get('product_name')
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')
                image3 = request.FILES.get('image3')
                is_listed = request.POST.get('available')
                price = request.POST.get('price')
                description=request.POST.get('description')
                sub_category_id=request.POST.get('sub_category')
                offer_id = request.POST.get('offer')
                sub_category=Sub_Category.objects.get(id=sub_category_id)
                category_id=sub_category.category.id
                category=Category.objects.get(id=category_id)
                category=Category.objects.get(id=id)
                sub_categories=category.sub_category.all()
                offers = Offer.objects.filter(end_date__gt=now)
                
                
                context ={
                        'product_name':product_name,
                        'image1':image1,
                        'image2' :image2,
                        'image3' :image3,
                       'is_listed':is_listed,
                        'price' :price,
                        'description':description,
                        'sub_category_id':sub_category,
                        'sub_categories':sub_categories,
                        'offers':offers
                

                }
                
                if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$', product_name):
                    context['error'] = "Product name is not readable"
                    return render(request, 'admin/add_product.html', context)
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                if not image1.name.lower().endswith(tuple(valid_extensions)):
                        context['error'] = "Uploaded file must be an image (jpg, jpeg, png, gif)."
                        return render(request, 'admin/add_product.html', context)
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                if not image2.name.lower().endswith(tuple(valid_extensions)):
                        context['error'] = "Uploaded file must be an image (jpg, jpeg, png, gif)."
                        return render(request, 'admin/add_product.html', context)

                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                if not image3.name.lower().endswith(tuple(valid_extensions)):
                        context['error'] = "Uploaded file must be an image (jpg, jpeg, png, gif)."
                        return render(request, 'admin/add_product.html', context)
                if not re.match(r'^(0|[1-9]\d*)(\.\d{1,2})?$',price):
                    context['error'] = "price cannot be character"
                    return render(request, 'admin/add_product.html', context)

                if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$',description):
                    context['error'] = "discription should contain letters"
                    return render(request, 'admin/add_product.html', context)
 

                
                
                new_product = Product(
                    product_name = product_name,
                    description = description,
                    price = price,
                    image1=image1,
                    image2=image2,
                    image3=image3,
                    category=category,
                    sub_category=sub_category,
                    

                    
                    
                    is_listed = is_listed,
                )
                if offer_id:
                    offer = Offer.objects.get(id = offer_id)
                    new_product.offer = offer
                new_product.save()
                
                return redirect('product_app:admin_product_view')
        category=Category.objects.get(id=id)
        sub_categories=category.sub_category.all()
        offers = Offer.objects.filter(end_date__gt=now)
        context={
            
                'sub_categories':sub_categories,
                'offers':offers


            }
        return render(request,'admin/add_product.html',context)
    else:
        return redirect('user_app:index')
@never_cache
def product_varients(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        product =  Product.objects.get(id = id)
        request.session['product_id']=id
        
        varients=product.varient.all()
        context={
            'varients':varients,
        }

        return render(request,'admin/product_varients.html',context)
       

    else:
        return redirect('user_app:index')
@never_cache
def edit_varient(request,id):
    if request.user.is_authenticated and request.user.is_staff:
         varient= Varient.objects.get(id=id)
         
         context={
             'varient':varient
         }
         if request.method == 'POST':
        
            stock = request.POST.get('stock')
            
            varient.stock=F('stock')+stock
            varient.save()
            product_id=request.session['product_id']
           
            return redirect('product_app:product_varients',id=product_id)
         else:
            return render(request,'admin/edit_varient.html',context)
    else:
        return redirect('user_app:index')
@never_cache
def add_varient(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method=='POST':
            id=request.session['product_id']
            product=Product.objects.get(id=id)
            size = request.POST.get('size')
            stock = request.POST.get('stock')
            print(size)
            print(stock)
            new_varient = Varient(
               size=size,
               stock=stock,
               
               
            )
            new_varient.save()
            new_varient.product.add(product)
            return redirect('product_app:product_varients',id=id)
            


            
        return render(request,'admin/add_varients.html')
    

    else:
        return redirect('user_app:index')
@never_cache
def edit_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        
        now = datetime.now(kolkata_tz)
        product=Product.objects.get(id=id)
        offers = Offer.objects.filter(end_date__gt=now)
        context={
            'product':product,
            'offers':offers,
         }
        if request.method == 'POST':
            product_name = request.POST.get('product_name')

            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')
            price = request.POST.get('price')
            description=request.POST.get('description')
            offer_id=request.POST.get('offer')
            if description:
                product.description=description
            product.product_name =  product_name
            if image1:
                product.image1=image1
            if image2:
                product.image2=image2
            if image3:
                product.image3=image3
            if offer_id:
                    offer = Offer.objects.get(id = offer_id)
                    product.offer = offer
            product.price=price
            product.save()
            return redirect('product_app:product_list',id=id)

           
        return render(request,'admin/edit_product.html',context)
    else:
        return redirect('user_app:index')


         
         






       
             
        


