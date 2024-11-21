from django.urls import path,include
from . import views
app_name = 'order_app'
urlpatterns = [
path('order_complete/',views.order_complete,name='order_complete'),
path('complete/',views.complete,name='complete'),
path('cancel_order/<int:id>/',views.cancel_order,name='cancel_order'),
path('return_order/<int:id>/',views.return_order,name='return_order'),
path('return_confirm/<int:item_id>/<int:order_id>/',views.return_confirm,name='return_confirm'),
path('submit_review/<int:product_id>/<int:order_id>/',views.submit_review,name='submit_review'),
path('payment-callback/', views.payment_callback, name='payment_callback'),

]