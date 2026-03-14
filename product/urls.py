from django.urls import path
from . import views

app_name = 'product_app'

urlpatterns = [
    path('products/',                    views.admin_product_view,  name='admin_product_view'),
    path('products/<int:id>/',           views.product_list,       name='product_list'),
    path('products/<int:id>/add/',       views.add_product,        name='add_product'),
    path('products/<int:id>/variants/',  views.product_varients,   name='product_varients'),
    path('variants/<int:id>/edit/',      views.edit_varient,       name='edit_varient'),
    path('variants/add/',                views.add_varient,        name='add_varient'),
    path('products/<int:id>/edit/',      views.edit_product,       name='edit_product'),
]