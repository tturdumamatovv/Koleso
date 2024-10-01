from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone
from django.db.models import Sum, Min, Max


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, role='user', full_name=None):
        if not phone_number:
            raise ValueError('Необходимо указать номер телефона')
        if not full_name:
            raise ValueError('Необходимо указать полное имя')

        user = self.model(phone_number=phone_number, role=role, full_name=full_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, role='admin', full_name=None):
        user = self.create_user(phone_number, password=password, role=role, full_name=full_name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('user', _('Обычный пользователь')),
        ('delivery', _('Доставщик')),
        ('collector', _('Сборщик')),
        ('admin', _('Админ'))
    ]
    phone_number = models.CharField(max_length=13, unique=True, verbose_name=_('Номер телефона'))
    code = models.CharField(max_length=4, blank=True, null=True, verbose_name=_('Код'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Работник'))
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, max_length=255,
                                        verbose_name=_('Изображение профиля'))
    full_name = models.CharField(max_length=255, blank=True, verbose_name=_('Полное имя'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('Дата рождения'))
    email = models.EmailField(blank=True, verbose_name=_('Имейл'))
    first_visit = models.BooleanField(default=True, verbose_name=_('Дата первого визита'))
    fcm_token = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Токен'))
    receive_notifications = models.BooleanField(default=False, verbose_name=_('Получать уведомления'), null=True,
                                                blank=True)
    last_order = models.DateTimeField(null=True, blank=True, verbose_name=_("Последний заказ"))
    bonus = models.DecimalField(max_digits=9, decimal_places=2, verbose_name=_('Бонусы'), null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name=_('Роль'))
    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def get_admin_url(self):
        return f"/admin/authentication/user/{self.id}/change/"

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _("Пользователи")


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name=_("Пользователь"))
    city = models.CharField(max_length=100, verbose_name=_("Адрес"), null=True, blank=True)
    # street = models.CharField(max_length=100, verbose_name=_("Улица"), null=True, blank=True)
    # house_number = models.CharField(max_length=10, verbose_name=_("Номер дома"), null=True, blank=True)
    apartment_number = models.CharField(max_length=10, verbose_name=_("Номер квартиры"), null=True, blank=True)
    entrance = models.CharField(max_length=10, verbose_name=_("Подъезд"), null=True, blank=True)
    floor = models.CharField(max_length=10, verbose_name=_("Этаж"), null=True, blank=True)
    intercom = models.CharField(max_length=10, verbose_name=_("Домофон"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Главный"))
    latitude = models.DecimalField(max_digits=200, decimal_places=6, verbose_name=_('Широта'), null=True, blank=True)
    longitude = models.DecimalField(max_digits=200, decimal_places=6, verbose_name=_('Долгота'), null=True, blank=True)
    comment = models.TextField(verbose_name=_("Комментарий"), null=True, blank=True)

    class Meta:
        verbose_name = _("Адрес пользователя")
        verbose_name_plural = _("Адреса пользователей")
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.city}'  # - {self.street} {self.house_number}'


class BlacklistedAddress(models.Model):
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, verbose_name=_('Адрес пользователя'))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата добавления'))

    class Meta:
        verbose_name = _('Адрес в черном списке')
        verbose_name_plural = _('Адреса в черном списке')

    def __str__(self):
        return f"Адрес: {self.address.city}, {self.address.apartment_number}"


class DailyWorkSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    date = models.DateField(verbose_name=_("Дата"))
    start_time = models.DateTimeField(verbose_name=_("Время начала первой смены"))
    end_time = models.DateTimeField(verbose_name=_("Время окончания последней смены"))
    total_duration = models.DurationField(verbose_name=_("Общая продолжительность за день"))

    class Meta:
        verbose_name = _("Сводка по сменам за день")
        verbose_name_plural = _("Сводки по сменам за день")
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} - {self.date}"


class WorkShift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_shifts', verbose_name=_("Пользователь"))
    start_time = models.DateTimeField(verbose_name=_("Время начала"), null=True, blank=True)
    end_time = models.DateTimeField(verbose_name=_("Время окончания"), null=True, blank=True)
    duration = models.DurationField(verbose_name=_("Продолжительность смены"), null=True, blank=True)

    def calculate_duration(self):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
            self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.end_time:
            self.update_daily_summary()

    def update_daily_summary(self):
        # Получаем текущую дату
        shift_date = self.start_time.date()

        # Получаем все завершенные смены за этот день
        shifts = WorkShift.objects.filter(user=self.user, start_time__date=shift_date, end_time__isnull=False)

        # Рассчитываем общее время за день
        total_duration = shifts.aggregate(total_duration=Sum('duration'))['total_duration'] or timedelta(0)

        # Получаем время начала первой смены и время окончания последней смены
        start_time = shifts.aggregate(start_time=Min('start_time'))['start_time']
        end_time = shifts.aggregate(end_time=Max('end_time'))['end_time']

        # Обновляем или создаем сводку за день
        summary, created = DailyWorkSummary.objects.update_or_create(
            user=self.user,
            date=shift_date,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'total_duration': total_duration
            }
        )