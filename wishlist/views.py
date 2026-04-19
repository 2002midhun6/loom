import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Wishlist, Wishlist_items
from product.models import Product, Varient

logger = logging.getLogger(__name__)
def _staff_or_blocked_redirect(request):
    """Return a redirect Response if the user should not access the page, else None."""
    if request.user.is_staff:
        return redirect("admin_app:admin_home")
    if request.user.is_block:
        return redirect("user_app:user_logout")
    return None
@login_required
def add_to_wishlist(request, product_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    if request.method != "POST":
        return redirect("customer_app:view_product", id=product_id)
    product = get_object_or_404(Product, id=product_id)
    var_id = request.POST.get("var_id", "").strip()
    if not var_id:
        messages.error(request, "Please select a size before adding to wishlist.")
        return redirect("customer_app:view_product", id=product_id)
    try:
        var_id = int(var_id)
    except (ValueError, TypeError):
        messages.error(request, "Invalid size selection.")
        return redirect("customer_app:view_product", id=product_id)
    variant = get_object_or_404(Varient, id=var_id)
    try:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        already_exists = Wishlist_items.objects.filter(
            wishlist=wishlist, 
            product=product, 
            varient=variant
        ).exists()
        is_new = not already_exists
        if is_new:
            Wishlist_items.objects.create(
                wishlist=wishlist,
                product=product,
                varient=variant,
            )
        varients = Varient.objects.filter(product=product)
        return render(request, 'user/view_product.html', {
            'product': product,
            'id': product_id,
            'varients': varients,          
            'wishlist_alert': True,
            'wishlist_added': is_new,
            'variant_id': var_id,
        })

    except Exception as exc:
        logger.error("add_to_wishlist failed: user=%s product=%s variant=%s — %s",
                     request.user.pk, product_id, var_id, exc, exc_info=True)
        messages.error(request, "Could not add item to wishlist. Please try again.")
        return redirect("customer_app:view_product", id=product_id)
@login_required
def wishlist_view(request):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_items = wishlist.wishlist_items_set.all().select_related('product', 'varient')
    except Exception as exc:
        logger.error("wishlist_view failed: %s", exc)
        messages.error(request, "Could not load your wishlist.")
        wishlist_items = []
    just_added_info = request.session.pop('just_added_to_cart', None)
    return render(request, "user/wishlist.html", {
        "wishlist_items": wishlist_items,
        "just_added_info": just_added_info,  
    })
@login_required
def remove_from_wishlist(request, wishlist_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    wishlist_item = get_object_or_404(Wishlist_items, id=wishlist_id)
    if wishlist_item.wishlist.user != request.user:
        messages.error(request, "You do not have permission to remove this item.")
        return redirect("wishlist_app:wishlist_view")
    try:
        wishlist_item.delete()
        messages.success(request, "Item removed from your wishlist.")
    except Exception as exc:
        logger.error(
            "remove_from_wishlist: failed for user=%s item=%s — %s",
            request.user.pk, wishlist_id, exc, exc_info=True,
        )
        messages.error(request, "Could not remove item. Please try again.")

    return redirect("wishlist_app:wishlist_view")