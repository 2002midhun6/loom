# Generated by Django 5.1.2 on 2024-11-14 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0005_wallet_wallettransation"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="payment_status",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]