# Generated by Django 5.0.7 on 2024-10-24 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_product_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsize',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=10, verbose_name='Количество'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productsize',
            name='unit',
            field=models.CharField(choices=[('kg', 'Килограммы (кг)'), ('g', 'Граммы (г)'), ('l', 'Литры (л)'), ('ml', 'Миллилитры (мл)'), ('unit', 'Штуки (шт)')], default=1, max_length=10, verbose_name='Единица измерения'),
            preserve_default=False,
        ),
    ]
