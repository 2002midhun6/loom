from django.urls import path,include
from . import views
app_name = 'customer_app'
urlpatterns = [
     path('men_product/',views.men_product,name='men_product'),
     path('men_category/<int:id>/',views.men_category,name='men_category'),
     path('women_product/',views.women_product,name='women_product'),
     path('women_category/<int:id>/',views.women_category,name='women_category'),
     path('view_product/<int:id>/',views.view_product,name='view_product'),


    ]