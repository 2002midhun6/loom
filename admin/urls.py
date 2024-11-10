from django.urls import path,include
from . import views
app_name= 'admin_app'
urlpatterns = [
    path('admin_home',views.admin_home,name='admin_home'),
    path('user_details',views.user_details,name='user_details'),
    path('user_block/<id>/',views.user_block,name='user_block'),
    path('admin_logout',views.admin_logout,name='admin_logout'),
    path('admin_offer/',views.admin_offer,name='admin_offer'),
    path('add_offer/',views.add_offer,name='add_offer'),
    path('edit_offer/<id>/',views.edit_offer,name='edit_offer'),
    path('delete_offer/<id>/',views.delete_offer,name='delete_offer'),
    path('admin_coupen/',views.admin_coupon,name='admin_coupon'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('edit_coupon/<int:id>/', views.edit_coupon, name='edit_coupon'),
    path('remove_coupon/<int:id>/',views.remove_coupon, name='remove_coupon'),
    path('admin_banner/',views.admin_banner,name='admin_banner'),
    path('add_banner/',views.add_banner,name='add_banner'),
    path('edit_banner/<int:id>/', views.edit_banner, name='edit_banner'),
    path('remove_banner/<int:id>/',views.remove_banner, name='remove_banner'),
    path('admin_orders/',views.admin_orders, name='admin_orders'),
    path('show_order/<int:id>/',views.show_order, name='show_order'),


]
