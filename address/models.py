
from django.db import models
from  user.models import CustomUser
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('H','Home'),
        ('O','Office'),
        ('OT','Other')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses")
    country = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    address_type = models.CharField(max_length=10,choices=ADDRESS_TYPE_CHOICES)
    default = models.BooleanField(default=False)

    