# Generated by Django 5.0.7 on 2024-10-17 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_remove_order_promo_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='topping',
        ),
    ]
