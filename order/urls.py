from django.urls import path,include
from . import views
app_name = 'order_app'
urlpatterns = [
path('order_complete/',views.order_complete,name='order_complete'),
]