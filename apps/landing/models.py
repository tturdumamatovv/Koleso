from tabnanny import verbose

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from colorfield.fields import ColorField


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


class MainPageSite(SingletonModel):
    icon = models.FileField(
        upload_to='site_icon/',
        verbose_name=_("Логотип"),
        help_text=_("Иконка для главной страницы."))
    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок"),
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=255,
        verbose_name=_("Описание"),
        blank=True,
        null=True
    )
    subtitle = models.CharField(
        max_length=255,
        verbose_name=_("Подзаголовок"),
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to="images/meta",
        verbose_name=_("Изображение"),
        blank=True,
        null=True
    )
    download_text = models.CharField(
        max_length=255,
        verbose_name=_("Текст"),
        help_text=_("Скачать приложение сейчас")
    )
    google_play_icon = models.FileField(
        upload_to='site_icon/',
        verbose_name=_("Иконка для Google Play"),
    )
    google_play_link = models.URLField(
        verbose_name="Ссылка",
        max_length=255,
        blank=True,
        null=True
    )
    app_store_icon = models.FileField(
        upload_to='site_icon/',
        verbose_name=_("Иконка для App Store"),
    )
    app_store_link = models.URLField(
        verbose_name="Ссылка",
        max_length=255,
        blank=True,
        null=True
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
        return self.title


class ServiceFeature(SingletonModel):
    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок")
    )
    subtitle = models.CharField(
        verbose_name=_("Подзаголовок"),
        max_length=255,
        blank=True,
        null=True
    )
    question = models.TextField(
        verbose_name=_("Поле для вопроса?"),
        blank=True,
        null=True,
        help_text=_("Что вы найдете в нашем приложении?")
    )


    class Meta:
        verbose_name = _("Особенность сервиса")
        verbose_name_plural = _("Особенности сервиса")

    def __str__(self):
        return self.title


class ServiceFeatureStep(models.Model):
    service_feature = models.ForeignKey(ServiceFeature, on_delete=models.CASCADE, verbose_name=_("Особенность сервиса"))
    icon = models.FileField(upload_to='site_icon/', verbose_name=_("Иконка"))
    title = models.CharField(
        max_length=255,
        verbose_name=_("Заголовок")
    )
    description = models.CharField(
        verbose_name=_("Описание"),
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Раздел Этап обслуживания")
        verbose_name_plural = _("Раздел Этап обслуживания")


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


class ConvenientFunctionality(SingletonModel):
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Описание"), blank=True, null=True)

    def __str__(self):
        return self.title


    class Meta:
        verbose_name = _("Раздел Удобный Функционал")
        verbose_name_plural = _("Раздел Удобный Функционал")


class ConvenientFunctionalityChapter(models.Model):
    convenient_functionality = models.ForeignKey(ConvenientFunctionality, on_delete=models.CASCADE, verbose_name=_('Удобный Функционал'))
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Описание"), blank=True, null=True)
    image = models.FileField(verbose_name=_("Изображение"), upload_to="images/static", blank=True, null=True)
    qr_image = models.FileField(verbose_name=_("Qr Изображение"), upload_to="images/static", blank=True, null=True)
    qr_link = models.URLField(verbose_name="Ссылка", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Подраздел Удобный Функционал")
        verbose_name_plural = _("Подраздел Удобный Функционал")


class PaymentMethod(models.Model):
    main_page_site = models.ForeignKey(MainPageSite, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='payment_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = _('Ссылка для оплаты')
        verbose_name_plural = _('Ссылки для оплаты')


class Product(models.Model):
    name = models.CharField(verbose_name=_("Название продукта"), max_length=255)
    image = models.FileField(upload_to='site_icon/', verbose_name=_("Изображение продукта"))

    class Meta:
        verbose_name = _('Изображение продукта')
        verbose_name_plural = _('Изображения продукта')

    def __str__(self):
        return f'{self.name}'


class SubProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Продукт"), related_name='subproducts')
    image = models.FileField(upload_to='site_icon/', verbose_name=_("Изображение продукта"))
    tag = models.CharField(verbose_name=_("Тэг"), max_length=255, null=True, blank=True)
    text_color = ColorField(default='#FF0000', format='hex', verbose_name=_('Цвет текста'))
    background_color = ColorField(default='#FF0000', format='hex', verbose_name=_('Цвет фона'))
    title = models.CharField(verbose_name=_("Название"), max_length=255, null=True, blank=True)
    price = models.IntegerField(verbose_name=_("Основная цена"))
    discounted_price = models.IntegerField(verbose_name=_("Скидочная цена"))
    link = models.URLField(verbose_name=_("Ссылка"))

    class Meta:
        verbose_name = _('Продукт')
        verbose_name_plural = _('Продукты')

    def __str__(self):
        return f'{self.title}'
