# Generated by Django 5.0.7 on 2024-10-10 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_kkal_alter_product_carbohydrates_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='composition_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Состав'),
        ),
        migrations.AddField(
            model_name='product',
            name='composition_ky',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Состав'),
        ),
        migrations.AddField(
            model_name='product',
            name='composition_ru',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Состав'),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Производитель'),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer_ky',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Производитель'),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer_ru',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Производитель'),
        ),
        migrations.AddField(
            model_name='product',
            name='shelf_life_en',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Срок хранения'),
        ),
        migrations.AddField(
            model_name='product',
            name='shelf_life_ky',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Срок хранения'),
        ),
        migrations.AddField(
            model_name='product',
            name='shelf_life_ru',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Срок хранения'),
        ),
        migrations.AddField(
            model_name='product',
            name='storage_conditions_en',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Условия хранения'),
        ),
        migrations.AddField(
            model_name='product',
            name='storage_conditions_ky',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Условия хранения'),
        ),
        migrations.AddField(
            model_name='product',
            name='storage_conditions_ru',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Условия хранения'),
        ),
    ]
