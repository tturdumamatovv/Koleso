# Generated by Django 5.0.7 on 2024-09-26 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_message_is_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='is_read',
        ),
    ]
