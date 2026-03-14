from django.urls import path
from . import views

app_name = 'customer_app'

urlpatterns = [
    path('men/',                  views.men_product,     name='men_product'),
    path('men/<int:id>/',         views.men_category,    name='men_category'),
    path('women/',                views.women_product,   name='women_product'),
    path('women/<int:id>/',       views.women_category,  name='women_category'),
    path('product/<int:id>/',     views.view_product,    name='view_product'),
    path('account/',              views.account,         name='account'),
    path('address/add/',          views.add_address,     name='add_address'),
    path('address/<int:id>/edit/',   views.edit_address,    name='edit_address'),
    path('address/<int:address_id>/remove/', views.remove_address, name='remove_address'),
    path('profile/edit/<int:id>/', views.edit_user,       name='edit_user'),
    path('buy/<int:id>/',         views.item_order,      name='item_order'),
    path('wallet/',               views.view_wallet,     name='view_wallet'),
]