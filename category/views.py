from django.shortcuts import render,redirect
from  . models import *
from django.views.decorators.cache import never_cache
from django.contrib import messages
from offer.models import *
from datetime import datetime
import pytz


# Create your views here.
@never_cache
def category(request):
    if request.user.is_authenticated and request.user.is_staff:
        category = Category.objects.all()
        return render(request,'admin/admin_category.html',{'category':category})
    else:
        return redirect('user_app:index')
def category_list(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            category_obj = Category.objects.get(id = id)
            if category_obj.is_listed:
                category_obj.is_listed = False
                category_obj.save()
            elif not category_obj.is_listed:
                category_obj.is_listed = True
                category_obj.save()
        return redirect('category_app:category')
    else:
        return redirect('user_app:index')
@never_cache
def category_edit(request,id):

    if request.user.is_authenticated and request.user.is_staff:
        category = Category.objects.get(id = id)    # Retrive data of the catgory
        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            category_image = request.FILES.get('category_image')
            is_listed = request.POST.get('available')
            
            category.category_name = category_name
            category.is_listed = is_listed
            
            if category_image:
                category.category_image = category_image
            
            category.save()
            
            
            return redirect('category_app:category')
        return render(request,'admin/edit_category.html',{'category':category})
    else:
        return redirect('user_app:index')
@never_cache
def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            category_image = request.FILES.get('category_image')
            is_listed = request.POST.get('available')
            
            new_category = Category(
                category_name = category_name,
                category_image = category_image,
                is_listed = is_listed
            )
            new_category.save()
            messages.success(request,f'New category {category_name} added.')
            return redirect('category_app:category')
        return render(request,'admin/add_category.html')
    else:
        return redirect('user_app:index')
@never_cache
def sub_category(request,id):
    if request.user.is_authenticated and request.user.is_staff:
             category_obj = Category.objects.get(id = id)
             request.session['category_obj_id']=id
             sub_category_obj=category_obj.sub_category.all()
             return render(request,'admin/sub_category.html',{'sub_category_obj':sub_category_obj})
           
    else:
        return redirect('user_app:index')
def sub_category_list(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
          
            category_obj = Sub_Category.objects.get(id = id)
            if category_obj.is_listed:
                category_obj.is_listed = False
                category_obj.save()
            elif not category_obj.is_listed:
                category_obj.is_listed = True
                category_obj.save()
            id=request.session['category_obj_id']
        return redirect('category_app:sub_category',id=id)
    else:
        return redirect('user_app:index')  
@never_cache 
def sub_category_edit(request,id):

    if request.user.is_authenticated and request.user.is_staff:
        kolkata_tz = pytz.timezone('Asia/Kolkata')
        # Get the current time in Asia/Kolkata timezone
        now = datetime.now(kolkata_tz)
        sub_category = Sub_Category.objects.get(id = id) 
        offer = Offer.objects.filter(end_date__gt=now) # Retrive data of the catgory
        if request.method == 'POST':
            sub_category_name = request.POST.get('sub_category_name')
            sub_category_image = request.FILES.get('sub_category_image')
            is_listed = request.POST.get('available')
            offer=request.POST.get('offer')
            sub_category.sub_category_name = sub_category_name
            sub_category.is_listed = is_listed
           
            if sub_category_image:
                sub_category.sub_category_image = sub_category_image
            
            
            if offer:
                   sub_category.offer = Offer.objects.get(id = offer)
            sub_category.save()
            id=request.session['category_obj_id']
            return redirect('category_app:sub_category',id=id)
        return render(request,'admin/sub_category_edit.html',{'category':sub_category,'offer':offer})
    else:
        return redirect('user_app:index')
@never_cache
def add_sub_category(request):
        
        if request.user.is_authenticated and request.user.is_staff:
            if request.method == 'POST':
                id=request.session.get('category_obj_id')
                cat_obj=Category.objects.get(id=id)
                print(cat_obj.category_name)
                sub_category_name = request.POST.get('sub_category_name')
                sub_category_image = request.FILES.get('sub_category_image')
                is_listed = request.POST.get('available')
                
                new_category =  Sub_Category(
                    sub_category_name = sub_category_name,
                    sub_category_image = sub_category_image,
                    is_listed = is_listed,
                    category=cat_obj

                )
                new_category.save()
                messages.success(request,f'New category {sub_category_name} added.')
                return redirect('category_app:sub_category',id=id)
            return render(request,'admin/add_sub_category.html')
        else:
            return redirect('user_app:index')




    
    

