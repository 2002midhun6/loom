from django.urls import path,include
from . import views
app_name= 'category_app'
urlpatterns = [
 path('category',views.category,name='category'),
 path('category_list/<id>/',views.category_list,name='category_list'),
 path('category_edit/<id>/',views.category_edit,name='category_edit'),
 path('add_category',views.add_category,name='add_category'),
 path('sub_category/<id>/',views.sub_category,name='sub_category'),
 path('sub_category_list/<id>/',views.sub_category_list,name='sub_category_list'),
 path('sub_category_edit/<id>/',views.sub_category_edit,name='sub_category_edit'),
 path('add_sub_category',views.add_sub_category,name='add_sub_category'),

]