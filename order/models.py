from django.db import models
from user.models import CustomUser
from product.models import Product
from cart.models import *
from address.models import Address


# Create your models here.

STATUS = (
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('canceled','Canceled'),
    )
CHECKOUT_STATUS = (
    ('in_progress','In_progress'),
    ('completed','Completed'),
    ('canceled','Canceled'),
)

class Order(models.Model):
    # oid = ShortUUIDField(unique=True, length=10, max_length=20, prefix='ord', alphabet="abcdefgh12345")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    order_status = models.CharField(max_length=20, choices=STATUS, default="pending")
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    address = models.ForeignKey(Address,on_delete=models.SET_NULL, null=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f'{self.user.first_name}-{self.order_status}'

class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    return_reason = models.TextField(null=True, blank=True)
    return_date = models.DateTimeField(auto_now_add=True,null=True)
    return_status = models.CharField(max_length=10,default='pending',null=True,blank=True)

    def __str__(self) -> str:
        return f'{self.product.product_name}-{self.quantity}'
    

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    # payment_status = models.CharField(max_length=50)

