from io import BytesIO
from PIL import Image
from colorfield.fields import ColorField
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from unidecode import unidecode
from mptt.models import MPTTModel, TreeForeignKey


class Size(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Описание'))

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    text_color = ColorField(default='#FF0000', format='hex', verbose_name=_('Цвет текста'))
    background_color = ColorField(default='#FF0000', format='hex', verbose_name=_('Цвет фона'))

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Category(MPTTModel):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Описание'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Ссылка'), blank=True, null=True)
    image = models.FileField(upload_to='category_photos/', verbose_name=_('Фото'), blank=True, null=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/admin/product/category/{self.id}/change/"

    def clean(self):
        # Проверка на глубину вложенности (не более 3 уровней)
        if self.parent and self.parent.get_level() >= 2:
            raise ValidationError(_('Категория не может быть вложена глубже, чем на 3 уровня (category → subcategory → subsubcategory).'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        self.clean()
        super().save(*args, **kwargs)


class ProductSize(models.Model):
    UNIT_CHOICES = [
        ('kg', 'кг'),
        ('g', 'гр'),
        ('l', 'л'),
        ('ml', 'мл'),
        ('pcs', 'шт')
    ]

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_sizes',
                                verbose_name=_('Продукт'))
    size = models.CharField(max_length=255, verbose_name=_('Размер'), blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена со скидкой'),
                                           blank=True, null=True)
    bonus_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name=_('Цена бонусами'))
    quantity = models.DecimalField(max_digits=10, decimal_places=1, verbose_name=_('Количество'), default=0.0)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, verbose_name=_('Единица измерения'), default='pcs')

    class Meta:
        verbose_name = "Цена продукта по размеру"
        verbose_name_plural = "Цены продуктов по размерам"

    def __str__(self):
        return f"{self.size} - {self.get_price()}"

    def get_price(self):
        return self.discounted_price if self.discounted_price else self.price

    def save(self, *args, **kwargs):
        # Генерация строки размера с русскими обозначениями
        unit_mapping = dict(self.UNIT_CHOICES)  # Создаем отображение из choices
        self.size = f"{self.quantity} {unit_mapping[self.unit]}"  # Используем русское значение
        print(f"Saving Product: {self.size}, Quantity: {self.quantity}")
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        # Логика проверки
        if self.unit in ['l', 'ml'] and self.product.unit == 'kg':
            raise ValidationError(_('Нельзя выбрать литры или миллилитры для продукта, который измеряется в килограммах.'))
        if self.unit in ['kg', 'g'] and self.product.unit in ['l', 'ml']:
            raise ValidationError(_('Нельзя выбрать килограммы или граммы для продукта, который измеряется в литрах.'))


class Product(models.Model):
    is_popular = models.BooleanField(default=False, verbose_name=_('Популярный'))
    is_new = models.BooleanField(default=False, verbose_name=_('Новинка'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Категория'),
                                 related_name='products', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'), blank=True, null=True)
    photo = models.FileField(upload_to='product_photos/', verbose_name=_('Фото'), blank=True, null=True)
    kkal = models.CharField(max_length=100, verbose_name=_('Ккал'), blank=True, null=True)
    proteins = models.CharField(max_length=100, verbose_name=_('Белки (граммы)'), blank=True, null=True)
    fats = models.CharField(max_length=100, verbose_name=_('Жиры (граммы)'), blank=True, null=True)
    carbohydrates = models.CharField(max_length=100, verbose_name=_('Углеводы (граммы)'), blank=True, null=True)
    composition = models.CharField(max_length=255, verbose_name=_('Состав'), blank=True, null=True)
    shelf_life = models.CharField(max_length=50, verbose_name=_('Срок хранения'), blank=True, null=True)
    storage_conditions = models.CharField(max_length=100, verbose_name=_('Условия хранения'), blank=True, null=True)
    manufacturer = models.CharField(max_length=255, verbose_name=_('Производитель'), blank=True, null=True)
    toppings = models.ManyToManyField('Topping', related_name='products', verbose_name=_('Добавки'), blank=True)
    bonuses = models.BooleanField(default=False, verbose_name=_('Можно оптатить бонусами'))
    tags = models.ManyToManyField('Tag', related_name='products', verbose_name=_('Теги'), blank=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Активный Торав"))
    quantity = models.DecimalField(max_digits=10, decimal_places=1, verbose_name=_('Количество'), default=0.0)
    unit = models.CharField(max_length=5, choices=ProductSize.UNIT_CHOICES, verbose_name=_('Единица измерения'),
                            default='pcs')

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/admin/product/product/{self.id}/change/"

    def get_min_price(self):
        prices = [size.discounted_price if size.discounted_price else size.price for size in self.product_sizes.all()]
        return min(prices) if prices else None

    def save(self, *args, **kwargs):
        # Проверка на привязку к конечной категории
        if self.category and self.category.get_children().exists():
            raise ValueError(_('Продукты могут быть привязаны только к конечным категориям без подкатегорий'))

        print(f"Saving Product: {self.name}, Quantity: {self.quantity}")

        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.photo:
            try:
                image = Image.open(self.photo)

                max_width = 800
                max_height = 800

                original_width, original_height = image.size
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)

                resized_image = image.resize((new_width, new_height), Image.LANCZOS)

                image_io = BytesIO()
                # Устанавливаем имя файла без добавления дополнительных путей
                new_filename = f"{slugify(self.name)}_{self.pk}.webp"
                resized_image.save(image_io, format='WEBP', quality=85)

                # Сохраняем файл с корректным именем и без лишних путей
                self.photo.save(new_filename, ContentFile(image_io.getvalue()), save=False)
            except:
                print("Except")

        super().save(*args, **kwargs)


class Topping(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    photo = models.ImageField(upload_to='topping_photos/', verbose_name=_('Фото'), blank=True, null=True)

    class Meta:
        verbose_name = "Добавка"
        verbose_name_plural = "Добавки"

    def __str__(self):
        return self.name


class Set(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Категория'), related_name='sets')
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'), blank=True, null=True)
    photo = models.ImageField(upload_to='topping_photos/', verbose_name=_('Фото'), blank=True, null=True)
    products = models.ManyToManyField(ProductSize, related_name='sets', verbose_name=_('Продукты'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    bonus_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name=_('Цена бонусами'))
    bonuses = models.BooleanField(default=False, verbose_name=_('Можно оптатить бонусами'))
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена со скидкой'),
                                           blank=True, null=True)

    class Meta:
        verbose_name = "Сет"
        verbose_name_plural = "Сеты"

    def __str__(self):
        return self.name

    def get_price(self):
        return self.discounted_price if self.discounted_price else self.price


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    photo = models.ImageField(upload_to='topping_photos/', verbose_name=_('Фото'), blank=True, null=True)
    possibly_remove = models.BooleanField(default=False, verbose_name=_('Возможность удаления'))

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Название'))
    text = models.TextField(verbose_name=_('Текст'))
    product = models.ManyToManyField(Product, related_name='articles', verbose_name=_('Продукт'))

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return self.title
