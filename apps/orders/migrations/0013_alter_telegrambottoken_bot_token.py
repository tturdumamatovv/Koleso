# Generated by Django 5.0.7 on 2024-10-22 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_orderitem_topping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegrambottoken',
            name='bot_token',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True, verbose_name='Телеграм Бот Токен'),
        ),
    ]
