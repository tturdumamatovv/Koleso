# Generated by Django 5.0.7 on 2024-10-17 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_product_composition_en_product_composition_ky_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['order'], 'verbose_name': 'Cклад', 'verbose_name_plural': 'Склады'},
        ),
    ]
