# Generated by Django 5.1.2 on 2024-11-13 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0003_orderitems_discount"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitems",
            name="discount",
        ),
        migrations.AddField(
            model_name="order",
            name="discount",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
