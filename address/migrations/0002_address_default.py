# Generated by Django 5.1.2 on 2024-11-07 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("address", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="default",
            field=models.BooleanField(default=False),
        ),
    ]