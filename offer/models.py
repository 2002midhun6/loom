from django.db import models

# Create your models here.
class Offer(models.Model):
    offer_title=models.CharField(max_length=150)
    offer_description=models.TextField()
    offer_percentage=models.IntegerField()
    start_date=models.DateField()
    end_date=models.DateField()