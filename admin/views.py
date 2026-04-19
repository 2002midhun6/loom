import calendar
import logging
import re
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO

import pandas as pd
import pytz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import (
    ExtractMonth, ExtractYear, TruncDate, TruncMonth, TruncWeek, TruncYear,
    Coalesce,
)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from offer.models import Offer
from order.models import Order, OrderAddress, OrderItems, STATUS
from product.models import Category, Product
from user.models import CustomUser
from product.models import Banner, Coupen
logger = logging.getLogger(__name__)
def _require_staff(request):
    """Return a redirect if the user is not an authenticated staff member, else None."""
    if request.user.is_authenticated and request.user.is_staff:
        return None
    return redirect("user_app:index")
def _parse_aware_datetime(date_str, fmt="%Y-%m-%dT%H:%M"):
    """
    Parse a datetime string and return a timezone-aware datetime.
    Raises ValueError on bad input — callers should catch it.
    """
    naive = datetime.strptime(date_str, fmt)
    return timezone.make_aware(naive, timezone.get_current_timezone())
def _validate_offer_fields(offer_title, offer_description, offer_percentage,
                            start_date, end_date):
    """Return an error string or None."""
    if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$', offer_title):
        return "Offer title is not valid."
    if not re.match(r'^[a-zA-Z]+(\s+[a-zA-Z]*)*$', offer_description):
        return "Description is not valid."
    if not re.match(r'^[0-9]+$', offer_percentage):
        return "Percentage must be a whole number."
    if end_date < timezone.now() or end_date < start_date:
        return "Please check the start and end dates."
    return None
@never_cache
def user_details(request):
    guard = _require_staff(request)
    if guard:
        return guard

    query = request.GET.get("search", "").strip()
    try:
        users = CustomUser.objects.exclude(is_staff=True)
        if query:
            users = users.filter(
                Q(first_name__icontains=query) | Q(email__icontains=query)
            )
    except Exception as exc:
        logger.error("user_details: DB error — %s", exc, exc_info=True)
        messages.error(request, "Could not load user list. Please try again.")
        users = CustomUser.objects.none()

    return render(request, "admin/admin_user_management.html", {
        "user": users,
        "query": query,
    })
@never_cache
def user_block(request, id):
    guard = _require_staff(request)
    if guard:
        return guard

    if request.method != "POST":
        return redirect("admin_app:user_details")

    user = get_object_or_404(CustomUser, id=id)
    try:
        user.is_block = not user.is_block
        user.save()
        status = "blocked" if user.is_block else "unblocked"
        messages.success(request, f"User {user.email} has been {status}.")
    except Exception as exc:
        logger.error("user_block: failed for user %s — %s", id, exc, exc_info=True)
        messages.error(request, "Could not update user status. Please try again.")

    return redirect("admin_app:user_details")
@never_cache
def admin_logout(request):
    guard = _require_staff(request)
    if guard:
        return guard

    if request.method == "POST":
        logout(request)
        return redirect("user_app:user_login")

    return redirect("admin_app:admin_home")
@never_cache
def admin_offer(request):
    guard = _require_staff(request)
    if guard:
        return guard
    query = request.GET.get("search_query", "").strip()
    try:
        offers = Offer.objects.filter(offer_title__icontains=query) if query else Offer.objects.all()
    except Exception as exc:
        logger.error("admin_offer: DB error — %s", exc, exc_info=True)
        messages.error(request, "Could not load offers.")
        offers = Offer.objects.none()
    return render(request, "admin/offer.html", {"offers": offers, "query": query})
@never_cache
def add_offer(request):
    guard = _require_staff(request)
    if guard:
        return guard
    if request.method != "POST":
        return render(request, "admin/add_offer.html")
    offer_title       = request.POST.get("offer_title", "").strip()
    offer_description = request.POST.get("offer_description", "").strip()
    offer_percentage  = request.POST.get("offer_percentage", "").strip()
    start_date_str    = request.POST.get("start_date", "").strip()
    end_date_str      = request.POST.get("end_date", "").strip()
    context = {
        "offer_title": offer_title,
        "offer_description": offer_description,
        "offer_percentage": offer_percentage,
    }
    try:
        start_date = _parse_aware_datetime(start_date_str)
        end_date   = _parse_aware_datetime(end_date_str)
    except (ValueError, TypeError):
        context["error"] = "Invalid date format. Please use the date picker."
        return render(request, "admin/add_offer.html", context)
    context.update({"start_date": start_date, "end_date": end_date})
    error = _validate_offer_fields(
        offer_title, offer_description, offer_percentage, start_date, end_date
    )
    if error:
        context["error"] = error
        return render(request, "admin/add_offer.html", context)
    try:
        Offer.objects.create(
            offer_title=offer_title,
            offer_description=offer_description,
            offer_percentage=offer_percentage,
            start_date=start_date,
            end_date=end_date,
        )
        messages.success(request, f"New offer '{offer_title}' added.")
        return redirect("admin_app:admin_offer")
    except Exception as exc:
        logger.error("add_offer: save failed — %s", exc, exc_info=True)
        context["error"] = "Failed to save offer. Please try again."
        return render(request, "admin/add_offer.html", context)
def edit_offer(request, id):
    guard = _require_staff(request)
    if guard:
        return guard
    offer = get_object_or_404(Offer, id=id)
    if request.method != "POST":
        return render(request, "admin/edit_offer.html", {"offer": offer})
    offer_title       = request.POST.get("offer_title", "").strip()
    offer_description = request.POST.get("offer_description", "").strip()
    offer_percentage  = request.POST.get("offer_percentage", "").strip()
    start_date_str    = request.POST.get("start_date", "").strip()
    end_date_str      = request.POST.get("end_date", "").strip()
    context = {
        "offer_title": offer_title,
        "offer_description": offer_description,
        "offer_percentage": offer_percentage,
        "offer": offer,
    }
    try:
        start_date = _parse_aware_datetime(start_date_str)
        end_date   = _parse_aware_datetime(end_date_str)
    except (ValueError, TypeError):
        context["error"] = "Invalid date format. Please use the date picker."
        return render(request, "admin/edit_offer.html", context)
    context.update({"start_date": start_date, "end_date": end_date})
    error = _validate_offer_fields(
        offer_title, offer_description, offer_percentage, start_date, end_date
    )
    if error:
        context["error"] = error
        return render(request, "admin/edit_offer.html", context)
    try:
        offer.offer_title       = offer_title
        offer.offer_description = offer_description
        offer.offer_percentage  = offer_percentage
        offer.start_date        = start_date
        offer.end_date          = end_date
        offer.save()
        messages.success(request, f"Offer '{offer_title}' updated.")
        return redirect("admin_app:admin_offer")
    except Exception as exc:
        logger.error("edit_offer: save failed for offer %s — %s", id, exc, exc_info=True)
        context["error"] = "Failed to update offer. Please try again."
        return render(request, "admin/edit_offer.html", context)
def delete_offer(request, id):
    guard = _require_staff(request)
    if guard:
        return guard
    offer = get_object_or_404(Offer, id=id)
    if request.method != "POST":
        return redirect("admin_app:admin_offer")
    try:
        title = offer.offer_title
        offer.delete()
        messages.success(request, f"Offer '{title}' removed.")
    except Exception as exc:
        logger.error("delete_offer: failed for offer %s — %s", id, exc, exc_info=True)
        messages.error(request, "Failed to delete offer. Please try again.")
    return redirect("admin_app:admin_offer")




def _validate_coupon_fields(code, minimum_order_amount, maximum_order_amount,
                             used_limit, discount_amount, expiry_date):
    """Return an error string or None."""
    if not re.match(r'^([a-zA-Z]+[0-9]*)+$', code):
        return "Code must not contain symbols."
    if not re.match(r'^\d*\.?\d+$', minimum_order_amount):
        return "Minimum amount must be a number."
    if not re.match(r'^\d*\.?\d+$', maximum_order_amount):
        return "Maximum amount must be a number."
    if not re.match(r'^[1-9][0-9]*$', used_limit):
        return "Usage limit must be 1 or more."
    if not re.match(r'^\d*\.?\d+$', discount_amount):
        return "Discount must be a positive number."
    if expiry_date < timezone.now():
        return "Expiry date cannot be in the past."

    try:
        min_amt      = float(minimum_order_amount)
        max_amt      = float(maximum_order_amount)
        discount_amt = float(discount_amount)
    except ValueError:
        return "Amount fields must be valid numbers."

    if max_amt < min_amt:
        return "Minimum amount cannot be greater than maximum amount."
    if min_amt <= discount_amt:
        return "Discount amount must be less than the minimum order amount."

    return None


def admin_coupon(request):
    guard = _require_staff(request)
    if guard:
        return guard

    query = request.GET.get("search_query", "").strip()
    try:
        coupons = Coupen.objects.filter(code__icontains=query) if query else Coupen.objects.all()
    except Exception as exc:
        logger.error("admin_coupon: DB error — %s", exc, exc_info=True)
        messages.error(request, "Could not load coupons.")
        coupons = Coupen.objects.none()

    return render(request, "admin/coupon.html", {"coupons": coupons, "query": query})


def add_coupon(request):
    guard = _require_staff(request)
    if guard:
        return guard

    if request.method != "POST":
        return render(request, "admin/add_coupen.html")

    code                  = request.POST.get("code", "").strip()
    minimum_order_amount  = request.POST.get("minimum_order_amount", "").strip()
    maximum_order_amount  = request.POST.get("maximum_order_amount", "").strip()
    used_limit            = request.POST.get("used_limit", "").strip()
    expiry_date_str       = request.POST.get("expiry_date", "").strip()
    discount_amount       = request.POST.get("discount_amount", "").strip()

    context = {
        "code": code,
        "minimum_order_amount": minimum_order_amount,
        "maximum_order_amount": maximum_order_amount,
        "used_limit": used_limit,
        "discount_amount": discount_amount,
    }

    try:
        expiry_date = _parse_aware_datetime(expiry_date_str)
    except (ValueError, TypeError):
        context["error"] = "Invalid expiry date format."
        return render(request, "admin/add_coupen.html", context)

    context["expiry_date"] = expiry_date

    error = _validate_coupon_fields(
        code, minimum_order_amount, maximum_order_amount,
        used_limit, discount_amount, expiry_date,
    )
    if error:
        context["error"] = error
        return render(request, "admin/add_coupen.html", context)

    try:
        Coupen.objects.create(
            code=code,
            minimum_order_amount=minimum_order_amount,
            maximum_order_amount=maximum_order_amount,
            used_limit=used_limit,
            expiry_date=expiry_date,
            discount_amount=discount_amount,
        )
        messages.success(request, f"New coupon '{code}' added.")
        return redirect("admin_app:admin_coupon")
    except Exception as exc:
        logger.error("add_coupon: save failed — %s", exc, exc_info=True)
        context["error"] = "Failed to save coupon. Please try again."
        return render(request, "admin/add_coupen.html", context)


def edit_coupon(request, id):
    guard = _require_staff(request)
    if guard:
        return guard

    coupon = get_object_or_404(Coupen, id=id)

    if request.method != "POST":
        return render(request, "admin/edit_coupen.html", {"coupon": coupon})

    code                 = request.POST.get("code", "").strip()
    minimum_order_amount = request.POST.get("minimum_order_amount", "").strip()
    maximum_order_amount = request.POST.get("maximum_order_amount", "").strip()
    used_limit           = request.POST.get("used_limit", "").strip()
    expiry_date_str      = request.POST.get("expiry_date", "").strip()
    discount_amount      = request.POST.get("discount_amount", "").strip()

    context = {
        "code": code,
        "minimum_order_amount": minimum_order_amount,
        "maximum_order_amount": maximum_order_amount,
        "used_limit": used_limit,
        "discount_amount": discount_amount,
        "coupon": coupon,
    }

    try:
        expiry_date = _parse_aware_datetime(expiry_date_str)
    except (ValueError, TypeError):
        context["error"] = "Invalid expiry date format."
        return render(request, "admin/edit_coupen.html", context)

    context["expiry_date"] = expiry_date

    error = _validate_coupon_fields(
        code, minimum_order_amount, maximum_order_amount,
        used_limit, discount_amount, expiry_date,
    )
    if error:
        context["error"] = error
        return render(request, "admin/edit_coupen.html", context)

    try:
        coupon.code                 = code
        coupon.minimum_order_amount = minimum_order_amount
        coupon.maximum_order_amount = maximum_order_amount
        coupon.used_limit           = used_limit
        coupon.expiry_date          = expiry_date
        coupon.discount_amount      = discount_amount
        coupon.save()
        messages.success(request, f"Coupon '{code}' updated.")
        return redirect("admin_app:admin_coupon")
    except Exception as exc:
        logger.error("edit_coupon: save failed for coupon %s — %s", id, exc, exc_info=True)
        context["error"] = "Failed to update coupon. Please try again."
        return render(request, "admin/edit_coupen.html", context)


def remove_coupon(request, id):
    guard = _require_staff(request)
    if guard:
        return guard

    coupon = get_object_or_404(Coupen, id=id)

    if request.method != "POST":
        return redirect("admin_app:admin_coupon")

    try:
        code = coupon.code
        coupon.delete()
        messages.success(request, f"Coupon '{code}' removed.")
    except Exception as exc:
        logger.error("remove_coupon: failed for coupon %s — %s", id, exc, exc_info=True)
        messages.error(request, "Failed to remove coupon. Please try again.")

    return redirect("admin_app:admin_coupon")




def _validate_banner_fields(banner_name, description, start_date, end_date):
    """Return an error string or None."""
    if not re.match(r'^[a-zA-Z]+[0-9]*(\s+[a-zA-Z0-9]*)*$', banner_name):
        return "Banner name is not valid."
    if not re.match(r'^[a-zA-Z]+(\s+[a-zA-Z]*)*$', description):
        return "Description is not valid."
    now = timezone.now()
    if end_date < now or start_date < now or end_date < start_date:
        return "Please check the start and end dates."
    return None


def admin_banner(request):
    guard = _require_staff(request)
    if guard:
        return guard

    query = request.GET.get("search_query", "").strip()
    try:
        banners = Banner.objects.filter(banner_name__icontains=query) if query else Banner.objects.all()
    except Exception as exc:
        logger.error("admin_banner: DB error — %s", exc, exc_info=True)
        messages.error(request, "Could not load banners.")
        banners = Banner.objects.none()

    return render(request, "admin/banner.html", {"banners": banners, "query": query})


def add_banner(request):
    guard = _require_staff(request)
    if guard:
        return guard

    if request.method != "POST":
        return render(request, "admin/add_banner.html", {"banner": Banner.objects.all()})

    banner_name    = request.POST.get("banner_name", "").strip()
    description    = request.POST.get("description", "").strip()
    banner_image   = request.FILES.get("banner_image")
    start_date_str = request.POST.get("start_date", "").strip()
    end_date_str   = request.POST.get("end_date", "").strip()

    context = {
        "banner_name": banner_name,
        "description": description,
        "banner_image": banner_image,
    }

    if not banner_image:
        context["error"] = "A banner image is required."
        return render(request, "admin/add_banner.html", context)

    try:
        start_date = _parse_aware_datetime(start_date_str)
        end_date   = _parse_aware_datetime(end_date_str)
    except (ValueError, TypeError):
        context["error"] = "Invalid date format. Please use the date picker."
        return render(request, "admin/add_banner.html", context)

    context.update({"start_date": start_date, "end_date": end_date})

    error = _validate_banner_fields(banner_name, description, start_date, end_date)
    if error:
        context["error"] = error
        return render(request, "admin/add_banner.html", context)

    try:
        Banner.objects.create(
            banner_name=banner_name,
            banner_description=description,
            banner_image=banner_image,
            start_date=start_date,
            end_date=end_date,
        )
        messages.success(request, f"New banner '{banner_name}' added.")
        return redirect("admin_app:admin_banner")
    except Exception as exc:
        logger.error("add_banner: save failed — %s", exc, exc_info=True)
        context["error"] = "Failed to save banner. Please try again."
        return render(request, "admin/add_banner.html", context)


def edit_banner(request, id):
    guard = _require_staff(request)
    if guard:
        return guard

    banner = get_object_or_404(Banner, id=id)

    if request.method != "POST":
        return render(request, "admin/edit_banner.html", {"banner": banner})

    banner_name    = request.POST.get("banner_name", "").strip()
    description    = request.POST.get("description", "").strip()
    banner_image   = request.FILES.get("banner_image")
    start_date_str = request.POST.get("start_date", "").strip()
    end_date_str   = request.POST.get("end_date", "").strip()

    context = {
        "banner_name": banner_name,
        "description": description,
        "banner_image": banner_image,
        "banner": banner,
    }

    try:
     
        start_date = _parse_aware_datetime(start_date_str)
        end_date   = _parse_aware_datetime(end_date_str)
    except (ValueError, TypeError):
        context["error"] = "Invalid date format. Please use the date picker."
        return render(request, "admin/edit_banner.html", context)

    context.update({"start_date": start_date, "end_date": end_date})

    error = _validate_banner_fields(banner_name, description, start_date, end_date)
    if error:
        context["error"] = error
        return render(request, "admin/edit_banner.html", context)

    try:
        banner.banner_name        = banner_name
        banner.banner_description = description
        banner.start_date         = start_date
        banner.end_date           = end_date
        if banner_image:
            banner.banner_image = banner_image
        banner.save()
        messages.success(request, f"Banner '{banner_name}' updated.")
        return redirect("admin_app:admin_banner")
    except Exception as exc:
        logger.error("edit_banner: save failed for banner %s — %s", id, exc, exc_info=True)
        context["error"] = "Failed to update banner. Please try again."
        return render(request, "admin/edit_banner.html", context)


def remove_banner(request, id):
    guard = _require_staff(request)
    if guard:
        return guard

    banner = get_object_or_404(Banner, id=id)

    if request.method != "POST":
        return redirect("admin_app:admin_banner")

    try:
        name = banner.banner_name
        banner.delete()
        messages.success(request, f"Banner '{name}' removed.")
    except Exception as exc:
        logger.error("remove_banner: failed for banner %s — %s", id, exc, exc_info=True)
        messages.error(request, "Failed to remove banner. Please try again.")

    return redirect("admin_app:admin_banner")


def admin_orders(request):
    guard = _require_staff(request)
    if guard:
        return guard

    query = request.GET.get("search_query", "").strip()
    try:
        orders = (
            Order.objects.filter(id__icontains=query)
            if query
            else Order.objects.all().order_by("-id")
        )
    except Exception as exc:
        logger.error("admin_orders: DB error — %s", exc, exc_info=True)
        messages.error(request, "Could not load orders.")
        orders = Order.objects.none()

    return render(request, "admin/order.html", {"orders": orders, "query": query})


def show_order(request, id):
    guard = _require_staff(request)
    if guard:
        return redirect("user_app:user_index")

    order = get_object_or_404(Order, id=id)

    try:
        order_details = OrderAddress.objects.get(order=order)
    except OrderAddress.DoesNotExist:
        logger.error("show_order: OrderAddress missing for order %s", id)
        messages.error(request, "Order address details could not be found.")
        return redirect("admin_app:admin_orders")
    except Exception as exc:
        logger.error("show_order: OrderAddress fetch error — %s", exc, exc_info=True)
        messages.error(request, "An error occurred loading order details.")
        return redirect("admin_app:admin_orders")

    if request.method == "POST":
        new_status = request.POST.get("order_status", "").strip()
        valid_statuses = dict(STATUS)
        if new_status in valid_statuses:
            try:
                order.order_status = new_status
                order.save()
                messages.success(request, "Order status updated successfully.")
            except Exception as exc:
                logger.error("show_order: status update failed for order %s — %s", id, exc, exc_info=True)
                messages.error(request, "Failed to update order status.")
        else:
            messages.error(request, "Invalid order status selected.")

    try:
        order_items = order.items.all()
        total_price = 0
        item_total_prices = []

        for item in order_items:
            item_total = item.quantity * item.product.discount_price
            total_price += item_total
            item_total_prices.append(item_total)

        coupon_savings = (
            (float(total_price) + 50) - float(order.discount)
            if order.discount else 0
        )
    except Exception as exc:
        logger.error("show_order: price calculation error for order %s — %s", id, exc, exc_info=True)
        messages.error(request, "An error occurred while calculating order totals.")
        total_price = coupon_savings = 0
        order_items = []
        item_total_prices = []

    context = {
        "order": order,
        "order_items": zip(order_items, item_total_prices),
        "total_price": total_price,
        "status_choices": STATUS,
        "items": order_items,
        "order_details": order_details,
        "coupon_savings": coupon_savings,
    }
    return render(request, "admin/show_order.html", context)




class SalesReportView(TemplateView):
    template_name = "admin/sales_report.html"
    timezone = pytz.timezone("Asia/Kolkata")

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect("user_app:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        download_format = request.GET.get("download_format")
        if download_format:
            try:
                start_date, end_date = self.get_date_range()
                sales_data = self.get_sales_data(start_date, end_date)
                if download_format == "excel":
                    return self.download_excel(sales_data)
                elif download_format == "pdf":
                    return self.download_pdf(sales_data)
                else:
                    return HttpResponse("Unsupported format.", status=400)
            except Exception as exc:
                logger.error("SalesReportView.get: download failed — %s", exc, exc_info=True)
                return HttpResponse("Failed to generate report.", status=500)

        return super().get(request, *args, **kwargs)

    def get_date_range(self):
        report_type  = self.request.GET.get("report_type", "daily")
        current_time = timezone.localtime(timezone.now(), self.timezone)
        today        = current_time.date()

        try:
            if report_type == "custom":
                start_str = self.request.GET.get("start_date", "")
                end_str   = self.request.GET.get("end_date", "")
                if not start_str or not end_str:
                    raise ValueError("Both start_date and end_date are required for custom range.")
                start = datetime.strptime(start_str, "%Y-%m-%d").date()
                end   = datetime.strptime(end_str,   "%Y-%m-%d").date() + timedelta(days=1)
                if start > end:
                    raise ValueError("Start date must be before end date.")
                return start, end

            date_ranges = {
                "daily":   (today - timedelta(days=1),      today + timedelta(days=1)),
                "weekly":  (today - timedelta(days=7),      today + timedelta(days=1)),
                "monthly": (today.replace(day=1),           today + timedelta(days=1)),
                "yearly":  (today.replace(month=1, day=1),  today + timedelta(days=1)),
            }
            return date_ranges.get(report_type, (today, today + timedelta(days=1)))

        except ValueError as exc:
            logger.warning("get_date_range: invalid input — %s", exc)
            return today, today + timedelta(days=1)
        except Exception as exc:
            logger.error("get_date_range: unexpected error — %s", exc, exc_info=True)
            return today, today + timedelta(days=1)

    def get_sales_data(self, start_date, end_date):
        try:
            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time()), self.timezone
            )
            end_datetime = timezone.make_aware(
                datetime.combine(end_date, datetime.min.time()), self.timezone
            )

            trunc_func = self.get_trunc_function()

            base_qs = OrderItems.objects.filter(
                order__order_date__gte=start_datetime,
                order__order_date__lt=end_datetime,
            )

            sales_data = (
                base_qs
                .annotate(period=trunc_func("order__order_date", tzinfo=self.timezone))
                .values("period")
                .annotate(
                    total_orders=Count("order", distinct=True),
                    delivered_orders=Count("order", distinct=True,
                        filter=Q(order__order_status="delivered")),
                    pending_orders=Count("order", distinct=True,
                        filter=Q(order__order_status="pending")),
                    cancelled_orders=Count("order", distinct=True,
                        filter=Q(order__order_status="canceled")),
                    total_amount=Coalesce(
                        Sum(F("price") * F("quantity")), Decimal("0.00")
                    ),
                    total_discount=Coalesce(Sum("order__discount"), Decimal("0.00")),
                )
                .order_by("period")
            )

            return [
                {
                    "period":           item["period"],
                    "total_orders":     item["total_orders"],
                    "delivered_orders": item["delivered_orders"],
                    "pending_orders":   item["pending_orders"],
                    "cancelled_orders": item["cancelled_orders"],
                    "total_amount":     item["total_amount"],
                    "discount":         item["total_discount"],
                    "net_amount":       item["total_amount"] - item["total_discount"],
                }
                for item in sales_data
            ]

        except Exception as exc:
            logger.error("get_sales_data: error — %s", exc, exc_info=True)
            return []

    def get_trunc_function(self):
        report_type = self.request.GET.get("report_type", "daily")
        return {
            "daily":   TruncDate,
            "weekly":  TruncWeek,
            "monthly": TruncMonth,
            "yearly":  TruncYear,
        }.get(report_type, TruncDate)

    def prepare_data_for_excel(self, sales_data):
        return [
            {
                "Period":            item["period"].strftime("%Y-%m-%d"),
                "Total Orders":      item["total_orders"],
                "Delivered Orders":  item["delivered_orders"],
                "Pending Orders":    item["pending_orders"],
                "Cancelled Orders":  item["cancelled_orders"],
                "Product Amount":    float(item["total_amount"]),
                "Discount":          float(item["discount"]),
                "Net Amount":        float(item["net_amount"]),
            }
            for item in sales_data
        ]

    def download_excel(self, sales_data):
        try:
            rows = self.prepare_data_for_excel(sales_data)
            if not rows:
                return HttpResponse("No data available for the selected period.", status=204)

            df     = pd.DataFrame(rows)
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Sales Report")
            output.seek(0)

            response = HttpResponse(
                output.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="sales_report.xlsx"'
            return response

        except Exception as exc:
            logger.error("download_excel: failed — %s", exc, exc_info=True)
            return HttpResponse("Error generating Excel file.", status=500)

    def download_pdf(self, sales_data):
        try:
            if not sales_data:
                return HttpResponse("No data available for the selected period.", status=204)

            buffer = BytesIO()
            doc    = SimpleDocTemplate(buffer, pagesize=A4,
                                       rightMargin=72, leftMargin=72,
                                       topMargin=72, bottomMargin=72)
            styles   = getSampleStyleSheet()
            elements = [
                Paragraph("Sales Report", styles["Heading1"]),
                Spacer(1, 20),
            ]

            header = [
                "Period", "Total Orders", "Delivered", "Pending",
                "Cancelled", "Product Amount", "Total Discount",
            ]
            table_data = [header]

            for item in sales_data:
                try:
                    table_data.append([
                        item["period"].strftime("%Y-%m-%d"),
                        str(item["total_orders"]),
                        str(item["delivered_orders"]),
                        str(item["pending_orders"]),
                        str(item["cancelled_orders"]),
                        f"₹{item['total_amount']:.2f}",
                        f"₹{item['discount']:.2f}",
                    ])
                except (KeyError, AttributeError) as exc:
                    logger.warning("download_pdf: skipping row — %s", exc)
                    continue

         
            try:
                table_data.append([
                    "Total",
                    str(sum(i["total_orders"]     for i in sales_data)),
                    str(sum(i["delivered_orders"]  for i in sales_data)),
                    str(sum(i["pending_orders"]    for i in sales_data)),
                    str(sum(i["cancelled_orders"]  for i in sales_data)),
                    f"₹{sum(i['total_amount'] for i in sales_data):.2f}",
                    f"₹{sum(i['discount']     for i in sales_data):.2f}",
                ])
            except Exception as exc:
                logger.warning("download_pdf: totals row failed — %s", exc)

            style = TableStyle([
                ("BACKGROUND",    (0, 0),  (-1, 0),  colors.grey),
                ("TEXTCOLOR",     (0, 0),  (-1, 0),  colors.whitesmoke),
                ("ALIGN",         (0, 0),  (-1, -1), "CENTER"),
                ("FONTNAME",      (0, 0),  (-1, 0),  "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0),  (-1, 0),  12),
                ("BOTTOMPADDING", (0, 0),  (-1, 0),  12),
                ("BACKGROUND",    (0, -1), (-1, -1), colors.lightgrey),
                ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID",          (0, 0),  (-1, -1), 1, colors.black),
                ("BOX",           (0, 0),  (-1, -1), 2, colors.black),
            ])
            for i in range(1, len(table_data) - 1):
                if i % 2 == 0:
                    style.add("BACKGROUND", (0, i), (-1, i), colors.lightgrey)

            table = Table(table_data)
            table.setStyle(style)
            elements.append(table)

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="sales_report.pdf"'
            response.write(pdf)
            return response

        except Exception as exc:
            logger.error("download_pdf: failed — %s", exc, exc_info=True)
            return HttpResponse("Error generating PDF file.", status=500)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            start_date, end_date = self.get_date_range()
            sales_data           = self.get_sales_data(start_date, end_date)

            overall_stats = {
                "total_orders":     sum(i["total_orders"]     for i in sales_data),
                "delivered_orders": sum(i["delivered_orders"]  for i in sales_data),
                "pending_orders":   sum(i["pending_orders"]    for i in sales_data),
                "cancelled_orders": sum(i["cancelled_orders"]  for i in sales_data),
                "total_amount":     sum(Decimal(str(i["total_amount"])) for i in sales_data),
                "total_discount":   sum(Decimal(str(i["discount"]))     for i in sales_data),
                "net_amount":       sum(Decimal(str(i["net_amount"]))   for i in sales_data),
            }

            context.update({
                "sales_data":   sales_data,
                "report_type":  self.request.GET.get("report_type", "daily"),
                "start_date":   start_date,
                "end_date":     end_date - timedelta(days=1),
                "overall_stats": overall_stats,
            })

        except Exception as exc:
            logger.error("get_context_data: error — %s", exc, exc_info=True)
            context.update({
                "error_message": "An error occurred while generating the report.",
                "sales_data":    [],
                "overall_stats": {},
            })

        return context



def top_selling_products(request):
    guard = _require_staff(request)
    if guard:
        return guard

    try:
        products     = Product.objects.all().order_by("-sold_count")[:10]
        total_sales  = products.aggregate(total=Sum("sold_count"))["total"] or 0
        avg_price    = products.aggregate(avg=Avg("price"))["avg"] or 0

        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago  = timezone.now() - timedelta(days=60)

        current_month_sales = (
            Product.objects.filter(created_at__gte=thirty_days_ago)
            .aggregate(total=Sum("sold_count"))["total"] or 0
        )
        previous_month_sales = (
            Product.objects.filter(created_at__range=(sixty_days_ago, thirty_days_ago))
            .aggregate(total=Sum("sold_count"))["total"] or 1  # avoid division by zero
        )

        monthly_growth = (
            (current_month_sales - previous_month_sales) / previous_month_sales
        ) * 100

        product_names = list(products.values_list("product_name", flat=True))
        sold_counts   = list(products.values_list("sold_count",   flat=True))

    except Exception as exc:
        logger.error("top_selling_products: error — %s", exc, exc_info=True)
        messages.error(request, "Could not load top-selling products.")
        products = Product.objects.none()
        total_sales = avg_price = monthly_growth = 0
        product_names = sold_counts = []

    context = {
        "products":       products,
        "total_sales":    total_sales,
        "avg_price":      round(avg_price, 2),
        "monthly_growth": round(monthly_growth, 1),
        "categories":     Category.objects.all(),
        "product_names":  product_names,
        "sold_counts":    sold_counts,
    }
    return render(request, "admin/top_selling_products.html", context)


def top_selling_categories_and_products(request):
    guard = _require_staff(request)
    if guard:
        return redirect("user_app:user_index")

    try:
        categories = (
            Category.objects.filter(is_listed=True)
            .annotate(total_sold=Sum("sub_category__product__sold_count"))
            .order_by("-total_sold")[:10]
        )

        category_data = []
        for category in categories:
            if category.category_name.lower() == "kidsware":
                continue
            try:
                top_products = (
                    Product.objects.filter(category__sub_category__category=category)
                    .order_by("-sold_count")
                    .distinct()[:10]
                )
                category_data.append({"category": category, "top_products": top_products})
            except Exception as exc:
                logger.warning(
                    "top_selling_categories: skipping category %s — %s",
                    category.pk, exc,
                )

    except Exception as exc:
        logger.error("top_selling_categories: error — %s", exc, exc_info=True)
        messages.error(request, "Could not load category data.")
        category_data = []

    return render(request, "admin/top_selling_categories.html", {"category_data": category_data})


def admin_dashboard(request):
    guard = _require_staff(request)
    if guard:
        return redirect("user_app:index")

    try:
        orders     = Order.objects.exclude(order_status="canceled")
        days_count = [0] * 7

        for order in orders:
            try:
                local_date = timezone.localtime(order.order_date)
                days_count[local_date.weekday()] += 1
            except Exception as exc:
                logger.warning("admin_dashboard: skipping order %s — %s", order.pk, exc)

        day_names = [calendar.day_name[i] for i in range(7)]

        orders_monthly = (
            Order.objects.exclude(order_status="canceled")
            .annotate(month=ExtractMonth("order_date", tzinfo=timezone.get_current_timezone()))
            .values("month")
            .annotate(count_month=Count("id"))
            .values("month", "count_month")
        )

        orders_yearly = (
            Order.objects.exclude(order_status="canceled")
            .annotate(year=ExtractYear("order_date", tzinfo=timezone.get_current_timezone()))
            .values("year")
            .annotate(count_year=Count("id"))
            .values("year", "count_year")
        )

        month              = []
        total_order_month  = []
        year               = []
        total_order_year   = []

        for i in orders_monthly:
            try:
                month.append(calendar.month_name[i["month"]])
                total_order_month.append(i["count_month"])
            except (KeyError, IndexError) as exc:
                logger.warning("admin_dashboard: monthly data error — %s", exc)

        for i in orders_yearly:
            try:
                year.append(str(i["year"]))
                total_order_year.append(i["count_year"])
            except KeyError as exc:
                logger.warning("admin_dashboard: yearly data error — %s", exc)

    except Exception as exc:
        logger.error("admin_dashboard: error — %s", exc, exc_info=True)
        messages.error(request, "Could not load dashboard data.")
        days_count = [0] * 7
        day_names = total_order_month = month = total_order_year = year = []

    context = {
        "total_order_day":   days_count,
        "day":               day_names,
        "total_order_month": total_order_month,
        "month":             month,
        "total_order_year":  total_order_year,
        "year":              year,
    }
    return render(request, "admin/admin_index.html", context)