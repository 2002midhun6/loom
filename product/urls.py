from django.urls import path,include
from . import views
app_name = 'product_app'
urlpatterns = [
    path('admin_product_view',views.admin_product_view,name='admin_product_view'),
    path('product_list/<int:id>/',views.product_list,name='product_list'),
    path('add_product/<int:id>/',views.add_product,name='add_product'),
    path('product_varients/<int:id>/',views.product_varients,name='product_varients'),
    path('edit_varient/<int:id>/',views.edit_varient,name='edit_varient'),
    path('add_varient',views.add_varient,name='add_varient'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
]