from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User
from apps.product.models import Product, Category


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        if not cls.objects.exists():
            cls.objects.create()
        return cls.objects.get()


class MainPage(SingletonModel):
    icon = models.ImageField(
        upload_to="images/icons",
        verbose_name=_("Иконка"),
        help_text=_("Иконка для главной страницы.")
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Телефон"),
        help_text=_("Контактный телефон для главной страницы.")
    )
    meta_title = models.CharField(
        max_length=255,
        verbose_name=_("Мета заголовок"),
        blank=True,
        null=True
    )
    meta_description = models.CharField(
        max_length=255,
        verbose_name=_("Мета описание"),
        blank=True,
        null=True
    )
    meta_image = models.ImageField(
        upload_to="images/meta",
        verbose_name=_("Мета изображение"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Главная страница")
        verbose_name_plural = _("Главная страница")

    def __str__(self):
        return self.phone


class OrderTypes(models.Model):
    page = models.ForeignKey(MainPage, on_delete=models.CASCADE, related_name='order_types')
    image = models.ImageField(verbose_name=_("Изображение"), blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Тип заказа")
        verbose_name_plural = _("Типы заказа")


class DeliveryConditions(models.Model):
    page = models.ForeignKey(MainPage, related_name='delivery_conditions', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_("Изображение"), blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Условия доставки")
        verbose_name_plural = _("Условия доставки")


class MethodsOfPayment(models.Model):
    page = models.ForeignKey(MainPage, related_name='methods_of_payment', on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_("Изображение"), blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Способ оплаты")
        verbose_name_plural = _("Способы оплаты")


class StaticPage(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
    slug = models.SlugField(unique=True, verbose_name=_("Слаг"), blank=True, null=True)
    image = models.FileField(verbose_name=_("Изображение"), upload_to="images/static", blank=True, null=True)
    meta_title = models.CharField(max_length=255, verbose_name=_("Мета заголовок"), blank=True, null=True)
    meta_description = models.CharField(max_length=255, verbose_name=_("Мета описание"), blank=True, null=True)
    meta_image = models.FileField(verbose_name=_("Мета изображение"), upload_to="images/meta", blank=True, null=True)

    class Meta:
        verbose_name = _("Статическая страница")
        verbose_name_plural = _("Статические страницы")

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Banner(models.Model):
    TYPE_CHOICES = (
        ('category', 'Категория'),
        ('product', 'Продукт'),
        ('link', 'Отдельная ссылка'),
    )
    type = models.CharField(verbose_name="Тип баннера", max_length=10, choices=TYPE_CHOICES, default='product')
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(verbose_name="ссылка", max_length=200, blank=True, null=True)
    title = models.CharField(verbose_name="Заголовок", max_length=123, blank=True, null=True)
    image_desktop = models.ImageField(verbose_name="Картинка круп", upload_to="images/banners/desktop/%Y/%m/")
    image_mobile = models.ImageField(verbose_name="Картинка моб", upload_to="images/banners/mobile/%Y/%m/")
    is_active = models.BooleanField(verbose_name="Активный", default=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ["is_active", "-created_at"]

    def get_image_desktop(self):
        if self.image_desktop:
            return mark_safe(
                f'<img src="{self.image_desktop.url}" width="328" height="100" />'
            )
        return ""

    def get_image_mobile(self):
        if self.image_mobile:
            return mark_safe(
                f'<img src="{self.image_mobile.url}" width="328" height="100" />'
            )
        return ""

    def __str__(self):
        return f"{self.title}"

    def clean(self):
        if self.type == 'category':
            if not self.category:
                raise ValidationError("Для типа 'Категория' необходимо указать категорию.")
            self.product = None
            self.link = ''
        elif self.type == 'product':
            if not self.product:
                raise ValidationError("Для типа 'Продукт' необходимо указать продукт.")
            self.category = None
            self.link = ''
        elif self.type == 'link':
            if not self.link:
                raise ValidationError("Для типа 'Отдельная ссылка' необходимо указать ссылку.")
            self.product = None
            self.category = None
        super().clean()


class Contacts(SingletonModel):
    pass

    def __str__(self):
        return 'Контактная информация'

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'


class Phone(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.phone}'

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'


class Email(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'Имейл'
        verbose_name_plural = 'Имейлы'


class SocialLink(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='social_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = 'Ссылка соцсети'
        verbose_name_plural = 'Ссылки соцсетей'


class Address(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'


class PaymentMethod(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='payment_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = 'Ссылка для оплаты'
        verbose_name_plural = 'Ссылки для оплаты'


class Stories(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=123, blank=True, null=True)
    image = models.ImageField(verbose_name="Изображение", upload_to="images/stories", blank=True, null=True)
    is_active = models.BooleanField(verbose_name="Активный", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа историй"
        verbose_name_plural = "Группы историй"


class Story(models.Model):
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(verbose_name="Изображение", upload_to="images/stories", blank=True, null=True)
    TYPE_CHOICES = (
        ('category', 'Категория'),
        ('product', 'Продукт'),
        ('link', 'Отдельная ссылка'),
    )
    type = models.CharField(verbose_name="Тип баннера", max_length=10, choices=TYPE_CHOICES, default='product')
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name="Категория", on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(verbose_name="ссылка", max_length=200, blank=True, null=True)

    is_active = models.BooleanField(verbose_name="Активный", default=True)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, blank=True, null=True)

    def clean(self):
        if self.type == 'category':
            if not self.category:
                raise ValidationError("Для типа 'Категория' необходимо указать категорию.")
            self.product = None
            self.link = ''
        elif self.type == 'product':
            if not self.product:
                raise ValidationError("Для типа 'Продукт' необходимо указать продукт.")
            self.category = None
            self.link = ''
        elif self.type == 'link':
            if not self.link:
                raise ValidationError("Для типа 'Отдельная ссылка' необходимо указать ссылку.")
            self.product = None
            self.category = None
        super().clean()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = "История"
        verbose_name_plural = "Истории"


class StoriesUserCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories_user_check')
    stories = models.ForeignKey(Stories, on_delete=models.CASCADE, related_name='stories_user_check')
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True, blank=True, null=True)