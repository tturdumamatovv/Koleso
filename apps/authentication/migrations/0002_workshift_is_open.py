# Generated by Django 5.0.7 on 2024-10-10 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshift',
            name='is_open',
            field=models.BooleanField(default=False, verbose_name='Смена открыта'),
        ),
    ]
