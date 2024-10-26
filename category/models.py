from django.db import models

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
     

   

    

