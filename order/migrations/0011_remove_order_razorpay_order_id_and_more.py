# Generated by Django 5.1.2 on 2024-11-21 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0010_order_razorpay_order_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="razorpay_order_id",
        ),
        migrations.RemoveField(
            model_name="payment",
            name="razor_pay_order_id",
        ),
        migrations.RemoveField(
            model_name="payment",
            name="razor_pay_payment_id",
        ),
        migrations.RemoveField(
            model_name="payment",
            name="razor_pay_payment_signature",
        ),
        migrations.AddField(
            model_name="payment",
            name="razorpay_order_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="payment",
            name="razorpay_payment_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
