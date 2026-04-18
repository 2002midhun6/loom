from django.urls import path
from . import views

app_name = 'cart_app'

urlpatterns = [
    path('add/<int:id>/',                        views.add_to_cart,                      name='add_to_cart'),
    path('cart/',                                views.view_cart,                        name='view_cart'),
    path('cart/item/<int:product_id>/<int:varient_id>/<str:action>/', views.update_cart_item_quantity,        name='update_cart_item_quantity'),
    path('cart/item/<int:cart_id>/remove/',      views.remove_cart_item,                 name='remove_cart_item'),
    # path('coupon/check/',                      views.check_coupon,                     name='check_coupon'),
    path('set-address/',                         views.set_checkout_address,             name='set_checkout_address'),
    path('checkout/<int:cart_id>/edit-address/<int:addr_id>/', views.checkout_edit_address, name='checkout_edit_address'),
    path('checkout/<int:cart_id>/add-address/', views.checkout_add_address, name='checkout_add_address'),
    path('checkout/<int:cart_id>/',              views.checkout,                         name='checkout'),
    path('coupon/',                              views.coupon,                           name='coupon'),
    path('cart/item/update/',                    views.update_cart_item_quantity_ajax,   name='update_cart_item_quantity_ajax'),
    
]