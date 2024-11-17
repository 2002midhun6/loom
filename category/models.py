from django.db import models
from offer.models import *

# Create your models here.
class Category(models.Model):
    category_name=models.TextField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)
    is_listed=models.BooleanField(default=True)
    category_image=models.ImageField(upload_to='category/')
    
class Sub_Category(models.Model):
     sub_category_name=models.TextField(max_length=50)
     sub_category_image=models.ImageField(upload_to='sub_category/')
     is_listed=models.BooleanField(default=True)
     created_at=models.DateTimeField(auto_now_add=True)
     category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='sub_category')
     offer= models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
     

   

    

