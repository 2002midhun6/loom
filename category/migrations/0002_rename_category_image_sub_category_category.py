# Generated by Django 5.1.2 on 2024-10-25 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sub_category',
            old_name='category_image',
            new_name='category',
        ),
    ]
