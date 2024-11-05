from django.urls import path,include
from . import views
app_name = 'cart_app'
urlpatterns = [
    path('add_to_cart/<int:id>/',views.add_to_cart,name='add_to_cart'),
    path('view_cart',views.view_cart,name='view_cart'),
   

]