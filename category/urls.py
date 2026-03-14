from django.urls import path
from . import views

app_name = 'category_app'

urlpatterns = [
    path('categories/',              views.category,           name='category'),
    path('categories/<int:id>/',     views.category_list,      name='category_list'),
    path('categories/<int:id>/edit/', views.category_edit,     name='category_edit'),
    path('categories/add/',          views.add_category,       name='add_category'),
    path('subcategories/<int:id>/',  views.sub_category,       name='sub_category'),
    path('subcategories/<int:id>/list/', views.sub_category_list, name='sub_category_list'),
    path('subcategories/<int:id>/edit/', views.sub_category_edit, name='sub_category_edit'),
    path('subcategories/add/',       views.add_sub_category,   name='add_sub_category'),
]