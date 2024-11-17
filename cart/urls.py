from django.urls import path,include
from . import views
app_name = 'cart_app'
urlpatterns = [
    path('add_to_cart/<int:id>/',views.add_to_cart,name='add_to_cart'),
    path('view_cart',views.view_cart,name='view_cart'),
    path('cart/update/<int:product_id>/<int:varient_id>/<str:action>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('remove_cart_item/<int:cart_id>/',views.remove_cart_item,name='remove_cart_item'),
    # path('check_coupon/',views.check_coupon,name='check_coupon'),
    path('checkout/<int:cart_id>/',views.checkout,name='checkout'),
    path('coupon/',views.coupon,name='coupon'),
    


]