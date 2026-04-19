from django.shortcuts import render, redirect, get_object_or_404
from product.models import *
from category.models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count, Sum
import re
import logging
from address.models import Address
from user.models import CustomUser
from cart.models import *
from order.models import *
from django.contrib import messages
import math
from django.contrib.auth.decorators import login_required
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)
def _expire_offers(products, now):
    for product in products:
        try:
            if product.offer and product.offer.end_date < now:
                product.offer = None
                product.save()
            elif (
                product.sub_category
                and product.sub_category.offer
                and product.sub_category.offer.end_date < now
            ):
                product.offer = None
                product.sub_category.offer = None
                product.sub_category.save()
        except Exception as exc:
            logger.warning("Failed to expire offer for product %s: %s", product.pk, exc)

def _staff_or_blocked_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_app:admin_home")
        if request.user.is_block:
            return redirect("user_app:user_logout")
    return None
def _parse_price(value):
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return None
def _paginate(queryset, page, per_page=8):
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.get_page(int(page))
    except (PageNotAnInteger, ValueError):
        return paginator.get_page(1)
    except EmptyPage:
        return paginator.get_page(paginator.num_pages)
def men_product(request):
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(kolkata_tz)
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        products = Product.objects.filter(category_id=2)
        _expire_offers(products, now)
        sub_category = Sub_Category.objects.filter(category_id=2)
        search_query = request.GET.get("search", "").strip()
        if search_query:
            products = products.filter(product_name__icontains=search_query)
            _expire_offers(products, now)
        selected_subcategory = request.GET.get("subcategory", "").strip()
        if selected_subcategory and selected_subcategory != "None":
            try:
                products = products.filter(sub_category_id=int(selected_subcategory))
                _expire_offers(products, now)
            except (ValueError, TypeError):
                messages.warning(request, "Invalid subcategory selected.")
                selected_subcategory = ""
        sort_by = request.GET.get("sort", "newest")
        sort_map = {
            "newest": "-created_at",
            "name_asc": "product_name",
            "name_desc": "-product_name",
        }
        products = products.order_by(sort_map.get(sort_by, "-created_at"))
        price_min_raw = request.GET.get("price_min", "")
        price_max_raw = request.GET.get("price_max", "")
        price_min = _parse_price(price_min_raw)
        price_max = _parse_price(price_max_raw)
        if price_min is not None:
            products = products.filter(price__gte=price_min)
        elif price_min_raw.strip():
            messages.warning(request, "Invalid minimum price value; filter ignored.")
        if price_max is not None:
            products = products.filter(price__lte=price_max)
        elif price_max_raw.strip():
            messages.warning(request, "Invalid maximum price value; filter ignored.")
        products = _paginate(products, request.GET.get("page", 1))
    except Exception as exc:
        logger.error("men_product view error: %s", exc, exc_info=True)
        messages.error(request, "An unexpected error occurred while loading products.")
        products, sub_category = [], []
        search_query = selected_subcategory = sort_by = price_min_raw = price_max_raw = ""
    context = {
        "products": products,
        "sub_category": sub_category,
        "search_query": search_query,
        "selected_subcategory": selected_subcategory,
        "sort_by": sort_by,
        "price_min": price_min_raw,
        "price_max": price_max_raw,
    }
    return render(request, "user/men.html", context)
def women_product(request):
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(kolkata_tz)
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        products = Product.objects.filter(category_id=1)
        _expire_offers(products, now)
        sub_category = Sub_Category.objects.filter(category_id=1)
        search_query = request.GET.get("search", "").strip()
        if search_query:
            products = products.filter(product_name__icontains=search_query)
        selected_subcategory = request.GET.get("subcategory", "").strip()
        if selected_subcategory and selected_subcategory != "None":
            try:
                products = products.filter(sub_category_id=int(selected_subcategory))
                _expire_offers(products, now)
            except (ValueError, TypeError):
                messages.warning(request, "Invalid subcategory selected.")
                selected_subcategory = ""
        sort_by = request.GET.get("sort", "newest")
        sort_map = {
            "newest": "-created_at",
            "name_asc": "product_name",
            "name_desc": "-product_name",
        }
        products = products.order_by(sort_map.get(sort_by, "-created_at"))
        price_min_raw = request.GET.get("price_min", "")
        price_max_raw = request.GET.get("price_max", "")
        price_min = _parse_price(price_min_raw)
        price_max = _parse_price(price_max_raw)
        if price_min is not None:
            products = products.filter(price__gte=price_min)
        elif price_min_raw.strip():
            messages.warning(request, "Invalid minimum price value; filter ignored.")
        if price_max is not None:
            products = products.filter(price__lte=price_max)
        elif price_max_raw.strip():
            messages.warning(request, "Invalid maximum price value; filter ignored.")
        products = _paginate(products, request.GET.get("page", 1))
    except Exception as exc:
        logger.error("women_product view error: %s", exc, exc_info=True)
        messages.error(request, "An unexpected error occurred while loading products.")
        products, sub_category = [], []
        search_query = selected_subcategory = sort_by = price_min_raw = price_max_raw = ""
    context = {
        "products": products,
        "sub_category": sub_category,
        "search_query": search_query,
        "selected_subcategory": selected_subcategory,
        "sort_by": sort_by,
        "price_min": price_min_raw,
        "price_max": price_max_raw,
    }
    return render(request, "user/women.html", context)
def men_category(request, id):
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(kolkata_tz)
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        products = Product.objects.filter(Q(category_id=2) & Q(sub_category=id))
        _expire_offers(products, now)
    except Exception as exc:
        logger.error("men_category view error for id=%s: %s", id, exc, exc_info=True)
        messages.error(request, "Could not load category products.")
        products = []
    return render(request, "user/casual.html", {"products": products})
def women_category(request, id):
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(kolkata_tz)
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        products = Product.objects.filter(Q(category_id=1) & Q(sub_category=id))
        _expire_offers(products, now)
    except Exception as exc:
        logger.error("women_category view error for id=%s: %s", id, exc, exc_info=True)
        messages.error(request, "Could not load category products.")
        products = []
    return render(request, "user/casual.html", {"products": products})
def view_product(request, id):
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(kolkata_tz)
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    product = get_object_or_404(Product, id=id)
    if not product.is_listed or not product.category.is_listed:
        messages.error(request, "This product is not available.")
        return redirect("customer_app:home")  
    offer_ended = False
    try:
        if product.offer and product.offer.end_date < now:
            product.offer = None
            product.save()
            offer_ended = True
        elif (
            product.sub_category
            and product.sub_category.offer
            and product.sub_category.offer.end_date < now
        ):
            product.offer = None
            product.sub_category.offer = None
            product.sub_category.save()
            offer_ended = True
    except Exception as exc:
        logger.warning("Offer expiry check failed for product %s: %s", id, exc)
    try:
        review_data = Product.objects.filter(id=id).aggregate(
            total_reviews=Count("productreview"),
            total_stars=Sum("productreview__rating"),
        )
        total_reviews = review_data["total_reviews"] or 0
        total_stars = review_data["total_stars"] or 0
        average_rating = math.floor(total_stars / total_reviews) if total_reviews > 0 else 0
        reviews = product.productreview_set.all()
    except Exception as exc:
        logger.error("Review fetch failed for product %s: %s", id, exc, exc_info=True)
        total_reviews = average_rating = 0
        reviews = []
    try:
        variants = product.varient.all()
    except Exception as exc:
        logger.error("Variant fetch failed for product %s: %s", id, exc, exc_info=True)
        variants = []
    context = {
        "varients": variants,
        "product": product,
        "average_rating": average_rating,
        "total_review": total_reviews,
        "reviews": reviews,
        "offer_ended": offer_ended,
    }
    return render(request, "user/view_product.html", context)
@login_required
def account(request):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        from user.models import UserReferral
        referral = UserReferral.objects.filter(user=request.user).first()
        referral_code = referral.referral_code if referral else "Not available"
        orders = request.user.orders.all().order_by("-id")
        user_details = get_object_or_404(CustomUser, email=request.user.email)
        address_default = Address.objects.filter(user=user_details, default=True)
        address_other = Address.objects.filter(user=user_details, default=False)
    except Exception as exc:
        logger.error("account view error for user %s: %s", request.user.pk, exc, exc_info=True)
        messages.error(request, "Failed to load account details. Please try again.")
        return redirect("customer_app:account")
    context = {
        "user_details": user_details,
        "address": address_default,
        "address1": address_other,
        "orders": orders,
        "referral_code": referral_code,
    }
    return render(request, "user/account.html", context)
_POSTAL_RE = re.compile(r'^[1-9][0-9]{2,9}$')
_PHONE_RE  = re.compile(r'^[1-9][0-9]{9,11}$')
def _validate_address_fields(postal_code, phone, alternative_phone):
    if not _POSTAL_RE.match(postal_code):
        return "Invalid postal code. Please enter a valid number (3–10 digits, no leading zero)."
    if not _PHONE_RE.match(phone):
        return "Invalid phone number. Please enter a valid 10–12 digit number."
    if alternative_phone and not _PHONE_RE.match(alternative_phone):
        return "Invalid alternative phone number. Please enter a valid 10–12 digit number."
    return None
@login_required
def add_address(request):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    if request.method == "POST":
        address_type    = request.POST.get("address_type", "").strip()
        country         = request.POST.get("country", "").strip()
        state           = request.POST.get("state", "").strip()
        street_address  = request.POST.get("street_address", "").strip()
        landmark        = request.POST.get("landmark", "").strip() or None
        postal_code     = request.POST.get("postal_code", "").strip()
        phone           = request.POST.get("phone", "").strip()
        alternative_phone = request.POST.get("alternative_phone", "").strip()
        is_default      = request.POST.get("is_default") == "on"
        context = {
            "address_type": address_type,
            "country": country,
            "state": state,
            "street_address": street_address,
            "landmark": landmark,
            "postal_code": postal_code,
            "phone": phone,
            "alternative_phone": alternative_phone,
        }
        required = {"Address type": address_type, "Country": country, "State": state,
                    "Street address": street_address, "Postal code": postal_code, "Phone": phone}
        for label, value in required.items():
            if not value:
                context["error"] = f"{label} is required."
                return render(request, "user/add_address.html", context)
        error = _validate_address_fields(postal_code, phone, alternative_phone)
        if error:
            context["error"] = error
            return render(request, "user/add_address.html", context)
        try:
            if is_default:
                Address.objects.filter(user=request.user, default=True).update(default=False)
            Address.objects.create(
                user=request.user,
                address_type=address_type,
                country=country,
                state=state,
                street_address=street_address,
                landmark=landmark,
                postal_code=postal_code,
                phone=phone,
                alternative_phone=alternative_phone or None,
                default=is_default,
            )
        except Exception as exc:
            logger.error("add_address save error for user %s: %s", request.user.pk, exc, exc_info=True)
            context["error"] = "Failed to save address. Please try again."
            return render(request, "user/add_address.html", context)
        next_url = request.session.pop("next", None)
        return redirect(next_url or "customer_app:account")
    return render(request, "user/add_address.html")
@login_required
def edit_address(request, id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    address_obj = get_object_or_404(Address, id=id)
    if request.user.id != address_obj.user.id:
        messages.error(request, "You do not have permission to edit this address.")
        return redirect("customer_app:account")
    context = {
        "landmark": address_obj.landmark,
        "postal_code": address_obj.postal_code,
        "phone": address_obj.phone,
        "street_address": address_obj.street_address,
        "alternative_phone": address_obj.alternative_phone,
        "default": address_obj.default,
    }
    if request.method == "POST":
        address_type      = request.POST.get("address_type", "").strip()
        country           = request.POST.get("country", "").strip()
        state             = request.POST.get("state", "").strip()
        street_address    = request.POST.get("street_address", "").strip()
        landmark          = request.POST.get("landmark", "").strip() or None
        postal_code       = request.POST.get("postal_code", "").strip()
        phone             = request.POST.get("phone", "").strip()
        alternative_phone = request.POST.get("alternative_phone", "").strip()
        is_default        = request.POST.get("is_default") == "on"
        context.update({
            "landmark": landmark,
            "postal_code": postal_code,
            "phone": phone,
            "street_address": street_address,
            "alternative_phone": alternative_phone,
            "default": is_default,
        })
        required = {"Address type": address_type, "Country": country, "State": state,
                    "Street address": street_address, "Postal code": postal_code, "Phone": phone}
        for label, value in required.items():
            if not value:
                context["error"] = f"{label} is required."
                return render(request, "user/edit_address.html", context)
        error = _validate_address_fields(postal_code, phone, alternative_phone)
        if error:
            context["error"] = error
            return render(request, "user/edit_address.html", context)
        try:
            if is_default:
                Address.objects.filter(user=request.user, default=True).update(default=False)
            address_obj.address_type      = address_type
            address_obj.country           = country
            address_obj.state             = state
            address_obj.street_address    = street_address
            address_obj.landmark          = landmark
            address_obj.postal_code       = postal_code
            address_obj.phone             = phone
            address_obj.alternative_phone = alternative_phone or None
            address_obj.default           = is_default
            address_obj.save()
        except Exception as exc:
            logger.error("edit_address save error for address %s: %s", id, exc, exc_info=True)
            context["error"] = "Failed to update address. Please try again."
            return render(request, "user/edit_address.html", context)
        next_url = request.session.pop("next", None)
        return redirect(next_url or "customer_app:account")
    return render(request, "user/edit_address.html", context)
@login_required
def remove_address(request, address_id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    address_item = get_object_or_404(Address, id=address_id)
    if address_item.user.id != request.user.id:
        messages.error(request, "You do not have permission to delete this address.")
        return redirect("customer_app:account")
    try:
        address_item.delete()
        messages.success(request, "Address removed successfully.")
    except Exception as exc:
        logger.error("remove_address error for address %s: %s", address_id, exc, exc_info=True)
        messages.error(request, "Failed to remove address. Please try again.")

    return redirect("customer_app:account")
_NAME_RE = re.compile(r'^[A-Za-z]+$')
@login_required
def edit_user(request, id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    user_details = get_object_or_404(CustomUser, id=id)
    if request.user.id != user_details.id:
        messages.error(request, "You do not have permission to edit this profile.")
        return redirect("customer_app:account")
    context = {
        "username": user_details.username,
        "first_name": user_details.first_name,
        "last_name": user_details.last_name,
    }
    if request.method == "POST":
        username   = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        context.update({"username": username, "first_name": first_name, "last_name": last_name})
        if not username or not first_name or not last_name:
            context["error"] = "All fields are required."
            return render(request, "user/edit_user_details.html", context)
        if not _NAME_RE.match(username):
            context["error"] = "Username should contain letters only."
            return render(request, "user/edit_user_details.html", context)
        if not _NAME_RE.match(first_name):
            context["error"] = "First name should contain letters only."
            return render(request, "user/edit_user_details.html", context)
        if not _NAME_RE.match(last_name):
            context["error"] = "Last name should contain letters only."
            return render(request, "user/edit_user_details.html", context)
        try:
            user_details.username   = username
            user_details.first_name = first_name
            user_details.last_name  = last_name
            user_details.save()
            messages.success(request, "Profile updated successfully.")
        except Exception as exc:
            logger.error("edit_user save error for user %s: %s", id, exc, exc_info=True)
            context["error"] = "Failed to update profile. Please try again."
            return render(request, "user/edit_user_details.html", context)
        return redirect("customer_app:account")
    return render(request, "user/edit_user_details.html", context)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from django.http import HttpResponse
from io import BytesIO
from decimal import Decimal, InvalidOperation
def generate_invoice_pdf(request, order, order_items, order_details):
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=60,
        )
        elements = []
        styles = getSampleStyleSheet()
        style_defs = [
            ("InvoiceTitle", "Heading1", dict(fontSize=28, textColor=colors.HexColor("#1a1a2e"), spaceAfter=4)),
            ("SubTitle",     "Normal",   dict(fontSize=10, textColor=colors.HexColor("#555555"), spaceAfter=2)),
            ("SectionHeader","Normal",   dict(fontSize=11, textColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=10)),
            ("SmallText",    "Normal",   dict(fontSize=9,  textColor=colors.HexColor("#444444"), spaceAfter=2)),
            ("RightAlign",   "Normal",   dict(fontSize=10, alignment=TA_RIGHT)),
            ("BoldRight",    "Normal",   dict(fontSize=11, fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        ]
        for name, parent, kwargs in style_defs:
            if name not in styles:
                styles.add(ParagraphStyle(name=name, parent=styles[parent], **kwargs))
        header_data = [[
            Paragraph("INVOICE", styles["InvoiceTitle"]),
            Paragraph(
                f"<b>Order #</b>{order.id}<br/>"
                f"<b>Date:</b> {order.order_date.strftime('%B %d, %Y')}<br/>"
                f"<b>Status:</b> {order.order_status.upper()}",
                styles["SmallText"],
            ),
        ]]
        header_table = Table(header_data, colWidths=[4 * inch, 3.5 * inch])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN",  (1, 0), (1, 0),  "RIGHT"),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e"), spaceAfter=12))
        bill_data = [[
            [
                Paragraph("BILL TO", styles["SectionHeader"]),
                Paragraph(f"{order.user.first_name} {order.user.last_name}", styles["SmallText"]),
                Paragraph(f"Email: {order.user.email}", styles["SmallText"]),
                Paragraph(f"Phone: {order_details.phone}", styles["SmallText"]),
            ],
            [
                Paragraph("SHIP TO", styles["SectionHeader"]),
                Paragraph(f"{order_details.street_address}", styles["SmallText"]),
                Paragraph(f"Pincode: {order_details.postal_code}", styles["SmallText"]),
                Paragraph(f"Phone: {order_details.phone}", styles["SmallText"]),
            ],
        ]]
        bill_table = Table(bill_data, colWidths=[3.75 * inch, 3.75 * inch])
        bill_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(bill_table)
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("ORDER ITEMS", styles["SectionHeader"]))
        col_widths = [3.2 * inch, 0.7 * inch, 1.1 * inch, 1.1 * inch, 1.4 * inch]
        table_data = [[
            Paragraph("<b>Product</b>",    styles["SmallText"]),
            Paragraph("<b>Qty</b>",        styles["SmallText"]),
            Paragraph("<b>Unit Price</b>", styles["SmallText"]),
            Paragraph("<b>Original</b>",   styles["SmallText"]),
            Paragraph("<b>Amount (₹)</b>", styles["SmallText"]),
        ]]
        if hasattr(order_items, "filter"):
            active_items = order_items.exclude(cancel_status="canceled").exclude(return_status="returned")
        else:
            active_items = order.items.exclude(cancel_status="canceled").exclude(return_status="returned")

        original_subtotal = Decimal("0")
        paid_subtotal     = Decimal("0")
        for item in active_items:
            try:
                item_price     = Decimal(str(item.item_price or item.product.discount_price))
                original_price = Decimal(str(item.product.price))
                qty            = Decimal(str(item.quantity))
                item_original  = qty * original_price
                item_paid      = qty * item_price
                original_subtotal += item_original
                paid_subtotal     += item_paid
                table_data.append([
                    Paragraph(item.product.product_name, styles["SmallText"]),
                    Paragraph(str(item.quantity),         styles["SmallText"]),
                    Paragraph(f"₹{item_price}",           styles["SmallText"]),
                    Paragraph(f"₹{item_original}",        styles["SmallText"]),
                    Paragraph(f"₹{item_paid}",            styles["SmallText"]),
                ])
            except (InvalidOperation, AttributeError, TypeError) as exc:
                logger.warning("Invoice: skipping item %s due to error: %s", getattr(item, "pk", "?"), exc)
                continue
        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 9),
            ("TOPPADDING",  (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING",(0, 0), (-1, 0), 8),
            ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 1), (-1, -1), 9),
            ("TOPPADDING",  (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 1), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
            ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 14))
        SHIPPING         = Decimal("50")
        product_discount = original_subtotal - paid_subtotal
        coupon_discount = Decimal("0")
        if order.coupons:
            try:
                raw = paid_subtotal + SHIPPING - (order.discount or Decimal("0"))
                coupon_discount = max(raw, Decimal("0"))
            except (InvalidOperation, TypeError):
                pass
        final_total = order.discount or paid_subtotal
        summary_data = [["Original Price (MRP):", f"₹{original_subtotal:.2f}"]]
        if product_discount > 0:
            summary_data.append(["Product / Offer Discount:", f"- ₹{product_discount:.2f}"])
        summary_data.append(["Subtotal after offers:", f"₹{paid_subtotal:.2f}"])
        summary_data.append(["Shipping:",              f"₹{SHIPPING:.2f}"])
        if coupon_discount > 0:
            summary_data.append([f"Coupon ({order.coupons.code}):", f"- ₹{coupon_discount:.2f}"])
        summary_data.append(["TOTAL PAID:", f"₹{final_total:.2f}"])
        summary_table = Table(summary_data, colWidths=[5.5 * inch, 2 * inch])
        summary_style = [
            ("ALIGN",       (1, 0), (1, -1),  "RIGHT"),
            ("FONTNAME",    (0, 0), (-1, -2),  "Helvetica"),
            ("FONTSIZE",    (0, 0), (-1, -1),  9),
            ("TOPPADDING",  (0, 0), (-1, -1),  4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
            ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE",    (0, -1), (-1, -1), 11),
            ("LINEABOVE",   (0, -1), (-1, -1), 1.5, colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR",   (0, -1), (-1, -1), colors.HexColor("#1a1a2e")),
        ]
        if product_discount > 0:
            summary_style.append(("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#2e7d32")))
        summary_table.setStyle(TableStyle(summary_style))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc"), spaceAfter=8))
        elements.append(Paragraph(
            "Thank you for shopping with us! For any queries, please contact our support.",
            styles["SmallText"],
        ))
        elements.append(Paragraph(
            f"Invoice generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["SmallText"],
        ))
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice_order_{order.id}.pdf"'
        response.write(pdf)
        return response
    except Exception as exc:
        logger.error("generate_invoice_pdf failed for order %s: %s", getattr(order, "id", "?"), exc, exc_info=True)
        response = HttpResponse("Failed to generate invoice. Please try again later.", status=500)
        return response
@login_required
def item_order(request, id):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    order = get_object_or_404(Order, id=id)
    if request.user.id != order.user.id:
        messages.error(request, "You do not have permission to view this order.")
        return redirect("customer_app:account")
    try:
        order_details = OrderAddress.objects.get(order=order)
    except OrderAddress.DoesNotExist:
        logger.error("OrderAddress missing for order %s", id)
        messages.error(request, "Order address details could not be found.")
        return redirect("customer_app:account")
    except Exception as exc:
        logger.error("item_order: OrderAddress fetch error for order %s: %s", id, exc, exc_info=True)
        messages.error(request, "An error occurred while loading order details.")
        return redirect("customer_app:account")
    if request.GET.get("download_pdf"):
        order_items = order.items.all().order_by("-id")
        return generate_invoice_pdf(request, order, order_items, order_details)
    try:
        order_items = order.items.all().order_by("-id")
        original_total = Decimal("0")
        active_total   = Decimal("0")
        canceled_total = Decimal("0")
        item_total_prices = []
        SHIPPING = Decimal("50")
        for item in order_items:
            try:
                item_total = Decimal(str(item.quantity)) * Decimal(str(item.product.discount_price))
                item_total_prices.append(item_total)
                original_total += item_total
                if item.cancel_status == "canceled":
                    canceled_total += item_total
                else:
                    active_total += item_total
            except (InvalidOperation, AttributeError, TypeError) as exc:
                logger.warning("item_order: skipping item %s: %s", getattr(item, "pk", "?"), exc)
                item_total_prices.append(Decimal("0"))
        coupon_savings = (original_total + SHIPPING) - (order.discount or Decimal("0"))
        amount_paid_for_products = (order.discount or Decimal("0")) - SHIPPING
        active_proportion = (active_total / original_total) if original_total > 0 else Decimal("1")
        if active_total == 0:
            effective_total = Decimal("0")
        else:
            effective_total = round(
                (active_proportion * amount_paid_for_products) + SHIPPING, 2
            )
        canceled_savings = (order.discount or Decimal("0")) - effective_total
    except Exception as exc:
        logger.error("item_order calculation error for order %s: %s", id, exc, exc_info=True)
        messages.error(request, "An error occurred while loading order details.")
        return redirect("customer_app:account")
    context = {
        "order": order,
        "order_items": zip(order_items, item_total_prices),
        "items": order_items,
        "total_price": original_total,
        "active_total": active_total.quantize(Decimal("0.01")),
        "canceled_total": canceled_total.quantize(Decimal("0.01")),
        "effective_total": effective_total.quantize(Decimal("0.01")),
        "canceled_savings": canceled_savings.quantize(Decimal("0.01")),
        "order_details": order_details,
        "coupon_savings": coupon_savings.quantize(Decimal("0.01")) if coupon_savings > 0 else Decimal("0"),
    }
    return render(request, "user/item_details.html", context)
@login_required
def view_wallet(request):
    guard = _staff_or_blocked_redirect(request)
    if guard:
        return guard
    try:
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet_transactions = wallet.transactions.all()
    except Exception as exc:
        logger.error("view_wallet error for user %s: %s", request.user.pk, exc, exc_info=True)
        messages.error(request, "Could not load wallet. Please try again.")
        wallet = None
        wallet_transactions = []
    context = {
        "wallet": wallet,
        "wallet_transaction": wallet_transactions,
    }
    return render(request, "user/wallet.html", context)