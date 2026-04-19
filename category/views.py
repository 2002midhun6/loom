from django.shortcuts import render, redirect
from .models import *
from django.views.decorators.cache import never_cache
from django.contrib import messages
from offer.models import *
from datetime import datetime
import pytz
@never_cache
def category(request):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            category = Category.objects.all()
            return render(request, 'admin/admin_category.html', {'category': category})
        except Exception as e:
            messages.error(request, f'Error loading categories: {str(e)}')
            return render(request, 'admin/admin_category.html', {'category': []})
    else:
        return redirect('user_app:index')
def category_list(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            try:
                category_obj = Category.objects.get(id=id)
                category_obj.is_listed = not category_obj.is_listed
                category_obj.save()
                status = "listed" if category_obj.is_listed else "unlisted"
                messages.success(request, f'Category "{category_obj.category_name}" has been {status}.')
            except Category.DoesNotExist:
                messages.error(request, 'Category not found.')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
        return redirect('category_app:category')
    else:
        return redirect('user_app:index')
@never_cache
def category_edit(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            category = Category.objects.get(id=id)
        except Category.DoesNotExist:
            messages.error(request, 'Category not found.')
            return redirect('category_app:category')
        if request.method == 'POST':
            try:
                category_name = request.POST.get('category_name', '').strip()
                category_image = request.FILES.get('category_image')
                is_listed = request.POST.get('available')
                if not category_name:
                    messages.error(request, 'Category name cannot be empty.')
                    return render(request, 'admin/edit_category.html', {'category': category})
                if Category.objects.filter(category_name__iexact=category_name).exclude(id=id).exists():
                    messages.error(request, f'A category named "{category_name}" already exists.')
                    return render(request, 'admin/edit_category.html', {'category': category})
                category.category_name = category_name
                category.is_listed = bool(is_listed)
                if category_image:
                    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
                    if category_image.content_type not in allowed_types:
                        messages.error(request, 'Invalid image format. Please upload JPEG, PNG, WEBP, or GIF.')
                        return render(request, 'admin/edit_category.html', {'category': category})
                    category.category_image = category_image
                category.save()
                messages.success(request, f'Category "{category_name}" updated successfully.')
                return redirect('category_app:category')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
                return render(request, 'admin/edit_category.html', {'category': category})
        return render(request, 'admin/edit_category.html', {'category': category})
    else:
        return redirect('user_app:index')
@never_cache
def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            try:
                category_name = request.POST.get('category_name', '').strip()
                category_image = request.FILES.get('category_image')
                is_listed = request.POST.get('available')
                if not category_name:
                    messages.error(request, 'Category name cannot be empty.')
                    return render(request, 'admin/add_category.html')
                if not category_image:
                    messages.error(request, 'Category image is required.')
                    return render(request, 'admin/add_category.html')
                if Category.objects.filter(category_name__iexact=category_name).exists():
                    messages.error(request, f'A category named "{category_name}" already exists.')
                    return render(request, 'admin/add_category.html')
                allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
                if category_image.content_type not in allowed_types:
                    messages.error(request, 'Invalid image format. Please upload JPEG, PNG, WEBP, or GIF.')
                    return render(request, 'admin/add_category.html')
                new_category = Category(
                    category_name=category_name,
                    category_image=category_image,
                    is_listed=bool(is_listed)
                )
                new_category.save()
                messages.success(request, f'New category "{category_name}" added successfully.')
                return redirect('category_app:category')
            except Exception as e:
                messages.error(request, f'Error adding category: {str(e)}')
                return render(request, 'admin/add_category.html')
        return render(request, 'admin/add_category.html')
    else:
        return redirect('user_app:index')
@never_cache
def sub_category(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            category_obj = Category.objects.get(id=id)
            request.session['category_obj_id'] = id
            sub_category_obj = category_obj.sub_category.all()
            return render(request, 'admin/sub_category.html', {'sub_category_obj': sub_category_obj})
        except Category.DoesNotExist:
            messages.error(request, 'Category not found.')
            return redirect('category_app:category')
        except Exception as e:
            messages.error(request, f'Error loading subcategories: {str(e)}')
            return redirect('category_app:category')
    else:
        return redirect('user_app:index')
def sub_category_list(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        category_obj_id = request.session.get('category_obj_id')
        if not category_obj_id:
            messages.error(request, 'Session expired. Please navigate from the category page.')
            return redirect('category_app:category')
        if request.method == 'POST':
            try:
                sub_cat_obj = Sub_Category.objects.get(id=id)
                sub_cat_obj.is_listed = not sub_cat_obj.is_listed
                sub_cat_obj.save()
                status = "listed" if sub_cat_obj.is_listed else "unlisted"
                messages.success(request, f'Subcategory "{sub_cat_obj.sub_category_name}" has been {status}.')
            except Sub_Category.DoesNotExist:
                messages.error(request, 'Subcategory not found.')
            except Exception as e:
                messages.error(request, f'Error updating subcategory: {str(e)}')

        return redirect('category_app:sub_category', id=category_obj_id)
    else:
        return redirect('user_app:index')
@never_cache
def sub_category_edit(request, id):
    if request.user.is_authenticated and request.user.is_staff:
        try:
            kolkata_tz = pytz.timezone('Asia/Kolkata')
            now = datetime.now(kolkata_tz)
            sub_category = Sub_Category.objects.get(id=id)
            offer = Offer.objects.filter(end_date__gt=now)
        except Sub_Category.DoesNotExist:
            messages.error(request, 'Subcategory not found.')
            return redirect('category_app:category')
        except Exception as e:
            messages.error(request, f'Error loading subcategory: {str(e)}')
            return redirect('category_app:category')

        if request.method == 'POST':
            category_obj_id = request.session.get('category_obj_id')
            if not category_obj_id:
                messages.error(request, 'Session expired. Please navigate from the category page.')
                return redirect('category_app:category')
            try:
                sub_category_name = request.POST.get('sub_category_name', '').strip()
                sub_category_image = request.FILES.get('sub_category_image')
                is_listed = request.POST.get('available')
                offer_id = request.POST.get('offer')
                if not sub_category_name:
                    messages.error(request, 'Subcategory name cannot be empty.')
                    return render(request, 'admin/sub_category_edit.html', {'category': sub_category, 'offer': offer})
                if Sub_Category.objects.filter(sub_category_name__iexact=sub_category_name).exclude(id=id).exists():
                    messages.error(request, f'A subcategory named "{sub_category_name}" already exists.')
                    return render(request, 'admin/sub_category_edit.html', {'category': sub_category, 'offer': offer})
                sub_category.sub_category_name = sub_category_name
                sub_category.is_listed = bool(is_listed)
                if sub_category_image:
                    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
                    if sub_category_image.content_type not in allowed_types:
                        messages.error(request, 'Invalid image format. Please upload JPEG, PNG, WEBP, or GIF.')
                        return render(request, 'admin/sub_category_edit.html', {'category': sub_category, 'offer': offer})
                    sub_category.sub_category_image = sub_category_image
                if offer_id:
                    try:
                        sub_category.offer = Offer.objects.get(id=offer_id)
                    except Offer.DoesNotExist:
                        messages.error(request, 'Selected offer not found.')
                        return render(request, 'admin/sub_category_edit.html', {'category': sub_category, 'offer': offer})
                sub_category.save()
                messages.success(request, f'Subcategory "{sub_category_name}" updated successfully.')
                return redirect('category_app:sub_category', id=category_obj_id)
            except Exception as e:
                messages.error(request, f'Error updating subcategory: {str(e)}')
                return render(request, 'admin/sub_category_edit.html', {'category': sub_category, 'offer': offer})
        return render(request, 'admin/sub_category_edit.html', {'category': sub_category, 'offer': offer})
    else:
        return redirect('user_app:index')
@never_cache
def add_sub_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            category_obj_id = request.session.get('category_obj_id')
            if not category_obj_id:
                messages.error(request, 'Session expired. Please navigate from the category page.')
                return redirect('category_app:category')
            try:
                cat_obj = Category.objects.get(id=category_obj_id)
            except Category.DoesNotExist:
                messages.error(request, 'Parent category not found.')
                return redirect('category_app:category')
            try:
                sub_category_name = request.POST.get('sub_category_name', '').strip()
                sub_category_image = request.FILES.get('sub_category_image')
                is_listed = request.POST.get('available')
                if not sub_category_name:
                    messages.error(request, 'Subcategory name cannot be empty.')
                    return render(request, 'admin/add_sub_category.html')
                if not sub_category_image:
                    messages.error(request, 'Subcategory image is required.')
                    return render(request, 'admin/add_sub_category.html')
                if Sub_Category.objects.filter(
                    sub_category_name__iexact=sub_category_name,
                    category=cat_obj
                ).exists():
                    messages.error(request, f'A subcategory named "{sub_category_name}" already exists in this category.')
                    return render(request, 'admin/add_sub_category.html')
                allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
                if sub_category_image.content_type not in allowed_types:
                    messages.error(request, 'Invalid image format. Please upload JPEG, PNG, WEBP, or GIF.')
                    return render(request, 'admin/add_sub_category.html')
                new_sub_category = Sub_Category(
                    sub_category_name=sub_category_name,
                    sub_category_image=sub_category_image,
                    is_listed=bool(is_listed),
                    category=cat_obj
                )
                new_sub_category.save()
                messages.success(request, f'New subcategory "{sub_category_name}" added successfully.')
                return redirect('category_app:sub_category', id=category_obj_id)
            except Exception as e:
                messages.error(request, f'Error adding subcategory: {str(e)}')
                return render(request, 'admin/add_sub_category.html')
        return render(request, 'admin/add_sub_category.html')
    else:
        return redirect('user_app:index')




    
    

