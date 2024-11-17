# Generated by Django 5.1.2 on 2024-11-17 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Offer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("offer_title", models.CharField(max_length=150)),
                ("offer_description", models.TextField()),
                ("offer_percentage", models.IntegerField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
            ],
        ),
    ]