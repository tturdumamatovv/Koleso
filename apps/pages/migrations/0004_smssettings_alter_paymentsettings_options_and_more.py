# Generated by Django 5.0.7 on 2024-10-28 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_paymentsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=100, verbose_name='Логин')),
                ('password', models.CharField(max_length=100, verbose_name='Пароль')),
                ('sender', models.CharField(max_length=100, verbose_name='Отправитель')),
            ],
            options={
                'verbose_name': 'Настройка SMS-сообщений',
                'verbose_name_plural': 'Настройки SMS-сообщений',
            },
        ),
        migrations.AlterModelOptions(
            name='paymentsettings',
            options={'verbose_name': 'Настройка платежа', 'verbose_name_plural': 'Настройки платежа'},
        ),
        migrations.AlterField(
            model_name='paymentsettings',
            name='merchant_id',
            field=models.CharField(max_length=100, verbose_name='ID магазина'),
        ),
        migrations.AlterField(
            model_name='paymentsettings',
            name='merchant_secret',
            field=models.CharField(max_length=100, verbose_name='Секретный ключ магазины'),
        ),
        migrations.AlterField(
            model_name='paymentsettings',
            name='merchant_secret_payout',
            field=models.CharField(max_length=100, verbose_name='Секретный ключ магазина для выплаты'),
        ),
        migrations.AlterField(
            model_name='paymentsettings',
            name='paybox_url',
            field=models.URLField(verbose_name='FreedomPay Ссылка'),
        ),
    ]
