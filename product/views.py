from django.shortcuts import render,redirect
from  . models import *
from category.models import *
from django.db.models import F


# Create your views here.
def admin_product_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        product = Product.objects.all()
        category=Category.objects.all()
        return render(request,'admin/product.html',{'product':product,'categories':category})
    else:
        return redirect('user_app:index')

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

def add_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method=="POST":
                product_name = request.POST.get('product_name')
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')
                image3 = request.FILES.get('image3')
                is_listed = request.POST.get('available')
                price = request.POST.get('price')
                description=request.POST.get('description')
                sub_category_id=request.POST.get('sub_category')
                sub_category=Sub_Category.objects.get(id=sub_category_id)
                category_id=sub_category.category.id
                category=Category.objects.get(id=category_id)
                
                
                
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
                new_product.save()
                
                return redirect('product_app:admin_product_view')
        category=Category.objects.get(id=id)
        sub_categories=category.sub_category.all()
        context={
            
                'sub_categories':sub_categories,

            }
        return render(request,'admin/add_product.html',context)
    else:
        return redirect('user_app:index')
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
def edit_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        product=Product.objects.get(id=id)
        context={
            'product':product
         }
        if request.method == 'POST':
            product_name = request.POST.get('product_name')

            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')
            price = request.POST.get('price')
            description=request.POST.get('description')
            if description:
                product.description=description
            product.product_name =  product_name
            if image1:
                product.image1=image1
            if image2:
                product.image2=image2
            if image3:
                product.image3=image3
           
            product.price=price
            product.save()
            return redirect('product_app:product_list',id=id)

           
        return render(request,'admin/edit_product.html',context)
    else:
        return redirect('user_app:index')


         
         






       
             
        


