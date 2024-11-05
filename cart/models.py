from django.db import models
from user.models import *
from product.models import *

# Create your models here
class Cart(models.Model):
    user=models.OneToOneField(CustomUser,max_length=100,on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True)
class Cart_item(models.Model):
    varient = models.ForeignKey(Varient, on_delete=models.CASCADE,null=True,blank=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE, related_name='items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='item')
    quantity=models.PositiveIntegerField()
    total_price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

    class Meta:
        unique_together = ('cart', 'product', 'varient')

    def __str__(self):
        return f"CartItem {self.id} - {self.product.product_name} (Qty: {self.quantity})"

    


