from django.db import models
from category.models import *


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
class Varient(models.Model):
    size=models.IntegerField()
    stock=models.IntegerField()
    product=models.ManyToManyField(Product,related_name='varient') 
  

    

