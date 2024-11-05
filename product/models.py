from django.db import models
from category.models import *
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone
from user.models import CustomUser


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1=models.ImageField(upload_to='product/')
    image2=models.ImageField(upload_to='product/',null=True,blank=True)
    image3=models.ImageField(upload_to='product/',null=True,blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='product')
    sub_category=models.ForeignKey(Sub_Category,on_delete=models.CASCADE,related_name='product')
    is_listed=models.BooleanField(default=True)

    @property
    def discount_price(self):
        if self.offer:
            discount = self.price - (self.offer.offer_percentage * self.price / 100)
            return round(discount, 2)
        return self.price
RATING = (
    (1,"⭐☆☆☆☆"),
    (2,"⭐⭐☆☆☆"),
    (3,"⭐⭐⭐☆☆"),
    (4,"⭐⭐⭐⭐☆"),
    (5,"⭐⭐⭐⭐⭐"),
)
    
class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING, default=None)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Varient(models.Model):
    size=models.IntegerField()
    stock=models.IntegerField()
    product=models.ManyToManyField(Product,related_name='varient') 
class Offer(models.Model):
    offer_title=models.CharField(max_length=150)
    offer_description=models.TextField()
    offer_percentage=models.IntegerField()
    start_date=models.DateField()
    end_date=models.DateField()
class Coupen(models.Model):
    code = models.CharField(max_length=50, unique=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    maximum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    used_limit = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        
        if not isinstance(self.expiry_date, datetime):
            raise ValidationError('Invalid expiry date format.')
        
        if self.expiry_date < timezone.now():
            raise ValidationError('The coupon has already expired.')

        
        if self.minimum_order_amount > self.maximum_order_amount:
            raise ValidationError('Minimum order amount cannot be greater than the maximum order amount.')
class Banner(models.Model):
    banner_name = models.CharField(max_length=255)
    banner_description = models.TextField()
    product = models.OneToOneField(Product,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deal_price = models.DecimalField(max_digits=10, decimal_places=2)
    banner_image = models.ImageField(upload_to='banner/')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_listed = models.BooleanField(default=True)

    