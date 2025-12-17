
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from product.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def add_to_wishlist(request, product_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    if request.method=='POST':
        user = request.user
        product = get_object_or_404(Product, id=product_id)
        if not  request.POST.get('var_id'):
            error_message = "select a size"

           
            messages.error(request, error_message)
            return redirect('customer_app:view_product', id=product_id)
        varients_id = request.POST.get('var_id')
        print(f"Variant ID from POST: {varients_id}")
                
        varient = Varient.objects.get(id=varients_id)
        print(f"Variant found: {varient}")
        
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        
       
        wishlist_item, item_created = Wishlist_items.objects.get_or_create(wishlist=wishlist, product=product,varient=varient)
        
        if not item_created:
           
            pass
        
        return redirect('wishlist_app:wishlist_view')
    return redirect('customer_app:view_product', id=id)
@login_required
def wishlist_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    wishlist_items = wishlist.wishlist_items_set.all()  
    if request.session.get('exist_session'):
        exist=True
        del request.session['exist_session']
    else:
        exist=False
        

    return render(request, 'user/wishlist.html', {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
        'exist':exist,
    })

@login_required
def remove_from_wishlist(request, wishlist_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('user_app:user_logout')
    
    wishlist_item = Wishlist_items.objects.get(id = wishlist_id)
    wishlist_item.delete()
    
    return redirect('wishlist_app:wishlist_view')
