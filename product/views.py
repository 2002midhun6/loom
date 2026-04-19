from django.shortcuts import render, redirect
from .models import *
from category.models import *
from django.db.models import F
from django.contrib import messages
from django.views.decorators.cache import never_cache
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import pytz
import sys
import re
VALID_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
PRODUCT_NAME_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*(\s+[a-zA-Z0-9]+)*$')
PRICE_RE = re.compile(r'^(0|[1-9]\d*)(\.\d{1,2})?$')
def _get_kolkata_now():
    return datetime.now(pytz.timezone('Asia/Kolkata'))
def _is_staff(request):
    return request.user.is_authenticated and request.user.is_staff
def _validate_image(image_file, field_label):
    if not image_file:
        return f'{field_label} is required.'
    ext = image_file.name.rsplit('.', 1)[-1].lower()
    if ext not in VALID_IMAGE_EXTENSIONS:
        return f'{field_label} must be a valid image (jpg, jpeg, png, gif, webp).'
    if hasattr(image_file, 'content_type') and image_file.content_type not in ALLOWED_IMAGE_TYPES:
        return f'{field_label} has an unsupported format.'
    return None
def crop_image(image_file, size=(800, 800)):
    img = Image.open(image_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    img = img.crop((left, top, right, bottom))
    img = img.resize(size, Image.Resampling.LANCZOS)
    output = BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    base_name = image_file.name.rsplit('.', 1)[0]
    return InMemoryUploadedFile(
        output, 'ImageField',
        f'{base_name}.jpg',
        'image/jpeg',
        sys.getsizeof(output),
        None,
    )
@never_cache
def admin_product_view(request):
    if not _is_staff(request):
        return redirect('user_app:index')
    try:
        products = Product.objects.all()
        categories = Category.objects.all()
        return render(request, 'admin/product.html', {'product': products, 'categories': categories})
    except Exception:
        messages.error(request, 'Error loading products.')
        return render(request, 'admin/product.html', {'product': [], 'categories': []})
@never_cache
def product_list(request, id):
    if not _is_staff(request):
        return redirect('user_app:index')
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=id)
            product.is_listed = not product.is_listed
            product.save()
            status = 'listed' if product.is_listed else 'unlisted'
            messages.success(request, f'"{product.product_name}" has been {status}.')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
        except Exception:
            messages.error(request, 'Error updating product status.')
    return redirect('product_app:admin_product_view')
@never_cache
def add_product(request, id):
    if not _is_staff(request):
        return redirect('user_app:index')
    now = _get_kolkata_now()
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
        return redirect('product_app:admin_product_view')
    sub_categories = category.sub_category.all()
    offers = Offer.objects.filter(end_date__gt=now)
    base_context = {'sub_categories': sub_categories, 'offers': offers}
    if request.method != 'POST':
        return render(request, 'admin/add_product.html', base_context)
    product_name = request.POST.get('product_name', '').strip()
    price = request.POST.get('price', '').strip()
    description = request.POST.get('description', '').strip()
    is_listed = request.POST.get('available')
    sub_category_id = request.POST.get('sub_category')
    offer_id = request.POST.get('offer')
    image1 = request.FILES.get('image1')
    image2 = request.FILES.get('image2')
    image3 = request.FILES.get('image3')
    context = {
        **base_context,
        'product_name': product_name,
        'price': price,
        'description': description,
        'is_listed': is_listed,
    }
    def fail(msg):
        context['error'] = msg
        return render(request, 'admin/add_product.html', context)
    if not product_name:
        return fail('Product name is required.')
    if not PRODUCT_NAME_RE.match(product_name):
        return fail('Product name must start with a letter and contain only letters, numbers, and spaces.')
    if not price:
        return fail('Price is required.')
    if not PRICE_RE.match(price):
        return fail('Price must be a valid positive number (e.g. 299 or 299.99).')
    if not description:
        return fail('Description is required.')
    if len(description) < 10:
        return fail('Description must be at least 10 characters.')
    if not sub_category_id:
        return fail('Please select a subcategory.')
    for img, label in ((image1, 'Image 1'), (image2, 'Image 2'), (image3, 'Image 3')):
        err = _validate_image(img, label)
        if err:
            return fail(err)
    if Product.objects.filter(product_name__iexact=product_name, category=category).exists():
        return fail(f'A product named "{product_name}" already exists in this category.')
    try:
        sub_category = Sub_Category.objects.get(id=sub_category_id)
    except Sub_Category.DoesNotExist:
        return fail('Selected subcategory does not exist.')
    try:
        image1 = crop_image(image1)
        image2 = crop_image(image2)
        image3 = crop_image(image3)
    except Exception:
        return fail('Error processing images. Please ensure the files are valid images.')
    try:
        new_product = Product(
            product_name=product_name,
            description=description,
            price=price,
            image1=image1,
            image2=image2,
            image3=image3,
            category=category,
            sub_category=sub_category,
            is_listed=bool(is_listed),
        )
        if offer_id:
            try:
                new_product.offer = Offer.objects.get(id=offer_id)
            except Offer.DoesNotExist:
                return fail('Selected offer does not exist.')
        new_product.save()
        messages.success(request, f'Product "{product_name}" added successfully.')
        return redirect('product_app:admin_product_view')
    except Exception:
        return fail('Error saving product. Please try again.')
@never_cache
def product_varients(request, id):
    if not _is_staff(request):
        return redirect('user_app:index')
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('product_app:admin_product_view')
    request.session['product_id'] = id
    varients = product.varient.all()
    return render(request, 'admin/product_varients.html', {'varients': varients, 'product': product})
@never_cache
def edit_varient(request, id):
    if not _is_staff(request):
        return redirect('user_app:index')
    try:
        varient = Varient.objects.get(id=id)
    except Varient.DoesNotExist:
        messages.error(request, 'Variant not found.')
        return redirect('product_app:admin_product_view')
    if request.method == 'POST':
        stock = request.POST.get('stock', '').strip()
        if not stock:
            messages.error(request, 'Stock value is required.')
            return render(request, 'admin/edit_varient.html', {'varient': varient})
        try:
            stock_int = int(stock)
            if stock_int < 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Stock must be a non-negative whole number.')
            return render(request, 'admin/edit_varient.html', {'varient': varient})
        product_id = request.session.get('product_id')
        if not product_id:
            messages.error(request, 'Session expired. Please navigate from the product page.')
            return redirect('product_app:admin_product_view')
        try:
            varient.stock = F('stock') + stock_int
            varient.save()
            messages.success(request, f'Stock updated by {stock_int} units.')
            return redirect('product_app:product_varients', id=product_id)
        except Exception:
            messages.error(request, 'Error updating stock. Please try again.')
            return render(request, 'admin/edit_varient.html', {'varient': varient})
    return render(request, 'admin/edit_varient.html', {'varient': varient})
@never_cache
def add_varient(request):
    if not _is_staff(request):
        return redirect('user_app:index')
    product_id = request.session.get('product_id')
    if not product_id:
        messages.error(request, 'Session expired. Please navigate from the product page.')
        return redirect('product_app:admin_product_view')
    if request.method == 'POST':
        size = request.POST.get('size', '').strip()
        stock = request.POST.get('stock', '').strip()
        if not size:
            messages.error(request, 'Size is required.')
            return render(request, 'admin/add_varients.html')
        if not stock:
            messages.error(request, 'Stock is required.')
            return render(request, 'admin/add_varients.html')
        try:
            stock_int = int(stock)
            if stock_int < 0:
                raise ValueError
        except ValueError:
            messages.error(request, 'Stock must be a non-negative whole number.')
            return render(request, 'admin/add_varients.html')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
            return redirect('product_app:admin_product_view')
        if Varient.objects.filter(product=product, size__iexact=size).exists():
            messages.error(request, f'A variant with size "{size}" already exists for this product.')
            return render(request, 'admin/add_varients.html')
        try:
            new_varient = Varient(size=size, stock=stock_int)
            new_varient.save()
            new_varient.product.add(product)
            messages.success(request, f'Variant (size: {size}) added successfully.')
            return redirect('product_app:product_varients', id=product_id)
        except Exception:
            messages.error(request, 'Error saving variant. Please try again.')
            return render(request, 'admin/add_varients.html')
    return render(request, 'admin/add_varients.html')
@never_cache
def edit_product(request, id):
    if not _is_staff(request):
        return redirect('user_app:index')
    now = _get_kolkata_now()
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('product_app:admin_product_view')
    offers = Offer.objects.filter(end_date__gt=now)
    context = {'product': product, 'offers': offers}
    if request.method != 'POST':
        return render(request, 'admin/edit_product.html', context)
    product_name = request.POST.get('product_name', '').strip()
    price = request.POST.get('price', '').strip()
    description = request.POST.get('description', '').strip()
    offer_id = request.POST.get('offer')
    image1 = request.FILES.get('image1')
    image2 = request.FILES.get('image2')
    image3 = request.FILES.get('image3')
    def fail(msg):
        messages.error(request, msg)
        return render(request, 'admin/edit_product.html', context)
    if not product_name:
        return fail('Product name is required.')
    if not PRODUCT_NAME_RE.match(product_name):
        return fail('Product name must start with a letter and contain only letters, numbers, and spaces.')
    if not price:
        return fail('Price is required.')
    if not PRICE_RE.match(price):
        return fail('Price must be a valid positive number (e.g. 299 or 299.99).')

    if description and len(description) < 10:
        return fail('Description must be at least 10 characters.')
    for img, label in ((image1, 'Image 1'), (image2, 'Image 2'), (image3, 'Image 3')):
        if img:
            err = _validate_image(img, label)
            if err:
                return fail(err)
    if Product.objects.filter(
        product_name__iexact=product_name, category=product.category
    ).exclude(id=id).exists():
        return fail(f'A product named "{product_name}" already exists in this category.')
    try:
        product.product_name = product_name
        product.price = price
        if description:
            product.description = description
        if image1:
            product.image1 = crop_image(image1)
        if image2:
            product.image2 = crop_image(image2)
        if image3:
            product.image3 = crop_image(image3)
        if offer_id:
            try:
                product.offer = Offer.objects.get(id=offer_id)
            except Offer.DoesNotExist:
                return fail('Selected offer does not exist.')
        product.save()
        messages.success(request, f'Product "{product_name}" updated successfully.')
        return redirect('product_app:admin_product_view')
    except Exception:
        return fail('Error saving product. Please try again.')