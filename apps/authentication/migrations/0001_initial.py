# Generated by Django 5.0.7 on 2024-09-26 05:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone_number', models.CharField(max_length=13, unique=True, verbose_name='Номер телефона')),
                ('code', models.CharField(blank=True, max_length=4, null=True, verbose_name='Код')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Работник')),
                ('profile_picture', models.ImageField(blank=True, max_length=255, null=True, upload_to='profile_pictures/', verbose_name='Изображение профиля')),
                ('full_name', models.CharField(blank=True, max_length=255, verbose_name='Полное имя')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Имейл')),
                ('first_visit', models.BooleanField(default=True, verbose_name='Дата первого визита')),
                ('fcm_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='Токен')),
                ('receive_notifications', models.BooleanField(blank=True, default=False, null=True, verbose_name='Получать уведомления')),
                ('last_order', models.DateTimeField(blank=True, null=True, verbose_name='Последний заказ')),
                ('bonus', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='Бонусы')),
                ('role', models.CharField(choices=[('user', 'Обычный пользователь'), ('delivery', 'Доставщик'), ('collector', 'Сборщик'), ('admin', 'Админ')], default='user', max_length=20, verbose_name='Роль')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Адрес')),
                ('apartment_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Номер квартиры')),
                ('entrance', models.CharField(blank=True, max_length=10, null=True, verbose_name='Подъезд')),
                ('floor', models.CharField(blank=True, max_length=10, null=True, verbose_name='Этаж')),
                ('intercom', models.CharField(blank=True, max_length=10, null=True, verbose_name='Домофон')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_primary', models.BooleanField(default=False, verbose_name='Главный')),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=200, null=True, verbose_name='Широта')),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=200, null=True, verbose_name='Долгота')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Адрес пользователя',
                'verbose_name_plural': 'Адреса пользователей',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BlacklistedAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.useraddress', verbose_name='Адрес пользователя')),
            ],
            options={
                'verbose_name': 'Адрес в черном списке',
                'verbose_name_plural': 'Адреса в черном списке',
            },
        ),
        migrations.CreateModel(
            name='WorkShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Время начала')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='Время окончания')),
                ('duration', models.DurationField(blank=True, null=True, verbose_name='Продолжительность смены')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_shifts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='DailyWorkSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата')),
                ('start_time', models.DateTimeField(verbose_name='Время начала первой смены')),
                ('end_time', models.DateTimeField(verbose_name='Время окончания последней смены')),
                ('total_duration', models.DurationField(verbose_name='Общая продолжительность за день')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Сводка по сменам за день',
                'verbose_name_plural': 'Сводки по сменам за день',
                'unique_together': {('user', 'date')},
            },
        ),
    ]
