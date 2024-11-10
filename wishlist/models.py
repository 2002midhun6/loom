from django.db import models
from user.models import *
from product.models import *

# Create your models here.

class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Wishlist_items(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    varient = models.ForeignKey(Varient, on_delete=models.CASCADE,null=True,blank=True)
    
    