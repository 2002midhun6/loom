from django.urls import path
from . import views

app_name = 'order_app'

urlpatterns = [
    path('order/complete/',       views.order_complete,   name='order_complete'),
    path('order/success/',        views.complete,         name='complete'),
    path('order/<int:id>/cancel/',   views.cancel_order,     name='cancel_order'),
    path('order/<int:id>/return/',   views.return_order,     name='return_order'),
    path('return/confirm/<int:item_id>/<int:order_id>/',  views.return_confirm,   name='return_confirm'),
    path('review/submit/<int:product_id>/<int:order_id>/',  views.submit_review,    name='submit_review'),
    path('payment/verify/',       views.verify_payment,   name='verify_payment'),
    path('payment/failed/',       views.payment_failed,   name='payment_failed'),
    path('payment/retry/<int:order_id>/',  views.retry_payment,    name='retry_payment'),
]