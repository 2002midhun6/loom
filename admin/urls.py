from django.urls import path
from . import views
from .views import SalesReportView

app_name = 'admin_app'

urlpatterns = [
    # Dashboard & Home
    path('dashboard/',              views.admin_dashboard,     name='admin_home'),
    path('dashboard/',              views.admin_dashboard,     name='admin_dashboard'),  # ← alias if needed
    path('users/',                  views.user_details,        name='user_details'),
    path('users/<int:id>/block/',   views.user_block,          name='user_block'),
    path('logout/',                 views.admin_logout,        name='admin_logout'),

    # Offers
    path('offers/',                 views.admin_offer,         name='admin_offer'),
    path('offers/add/',             views.add_offer,           name='add_offer'),
    path('offers/<int:id>/edit/',   views.edit_offer,          name='edit_offer'),
    path('offers/<int:id>/delete/', views.delete_offer,        name='delete_offer'),

    # Coupons
    path('coupons/',                views.admin_coupon,        name='admin_coupon'),
    path('coupons/add/',            views.add_coupon,          name='add_coupon'),
    path('coupons/<int:id>/edit/',  views.edit_coupon,         name='edit_coupon'),
    path('coupons/<int:id>/delete/',views.remove_coupon,       name='remove_coupon'),

    # Banners
    path('banners/',                views.admin_banner,        name='admin_banner'),
    path('banners/add/',            views.add_banner,          name='add_banner'),
    path('banners/<int:id>/edit/',  views.edit_banner,         name='edit_banner'),
    path('banners/<int:id>/delete/',views.remove_banner,       name='remove_banner'),

    # Orders
    path('orders/',                 views.admin_orders,        name='admin_orders'),
    path('orders/<int:id>/',        views.show_order,          name='show_order'),

    # Analytics & Reports
    path('top-products/',           views.top_selling_products,           name='admin-top-selling'),
    path('top-categories/',         views.top_selling_categories_and_products, name='top_selling_categories'),
    path('sales-report/',           SalesReportView.as_view(),            name='sales_report'),
]