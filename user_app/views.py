from django.shortcuts import render,redirect
from product.models import *
from category.models import *
from django.core.paginator import Paginator
from django.db.models import Q


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
          products = Product.objects.get(id=id)
          varients=products.varient.all()
          context= {
                  'varients':varients,
                  'product':products,
          }
          return render(request,'user/view_product.html',context)
        
        
        
   
    