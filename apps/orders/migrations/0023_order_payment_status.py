# Generated by Django 5.0.7 on 2024-11-05 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0022_rename_pg_payment_id_order_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=10),
        ),
    ]
