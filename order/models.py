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
        ('payment_pending', 'Payment Pending')
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
    coupons = models.ForeignKey(Coupen, on_delete=models.SET_NULL, null=True, blank=True)
    discount=models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
   
    
    def __str__(self) -> str:
        return f'{self.user.first_name}-{self.order_status}'
class OrderAddress(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE, related_name="orderaddress")
   
    street_address = models.CharField(max_length=255)
   
    landmark = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, null=True, blank=True)
    
  


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    varient = models.ForeignKey(Varient, on_delete=models.CASCADE,null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    item_price =  models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    return_date = models.DateTimeField(auto_now_add=True,null=True)
    return_status = models.CharField(max_length=10,default='pending',null=True,blank=True)
    return_reason = models.TextField(null=True,blank=True)

    def __str__(self) -> str:
        return f'{self.product.product_name}-{self.quantity}'
    

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50,null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_attempts = models.PositiveIntegerField(default=0)


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    balance=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
class WalletTransation(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('refund', 'Refund'),
        ('cancellation', 'Cancellation'),
        ('debited', 'Debited'),
        
    ]

    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE,related_name='transactions')
    transaction_type = models.CharField(max_length=20,choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    created_at =  models.DateField(auto_now_add=True)

