from rest_framework import serializers
from apps.product.models import (
    Product,
    ProductSize,
    Topping,
    Category,
    Tag, Article
)  # Set, Ingredient


# class IngredientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ingredient
#         fields = ['name', 'photo', 'possibly_remove']


class ToppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topping
        fields = ['id', 'name', 'price', 'photo']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price'])
        return representation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'text_color', 'background_color']


class ProductSizeSerializer(serializers.ModelSerializer):
    size = serializers.StringRelatedField()

    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'price', 'discounted_price', 'bonus_price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['bonus_price'] = float(representation['bonus_price'])
        representation['price'] = float(representation['price'])
        representation['discounted_price'] = float(representation['discounted_price']) if representation[
                                                                                              'discounted_price'] is not None else None
        return representation


class ProductSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True)
    toppings = ToppingSerializer(many=True)
    tags = TagSerializer(many=True)
    product_sizes = ProductSizeSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    bonus_price = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', 'kkal', 'proteins', 'fats', 'carbohydrates',
                  'composition', 'shelf_life', 'storage_conditions', 'manufacturer', 'tags', 'toppings',
                  'min_price', 'bonus_price', 'bonuses', 'product_sizes', 'category_slug', 'category_name']

    def get_min_price(self, obj):
        return obj.get_min_price()

    def get_bonus_price(self, obj):
        # Логика для вычисления bonus_price
        # Предположим, что bonus_price - это минимальная бонусная цена среди всех размеров продукта
        min_bonus_price = None
        for size in obj.product_sizes.all():
            if min_bonus_price is None or size.bonus_price < min_bonus_price:
                min_bonus_price = size.bonus_price
        return min_bonus_price

    def get_category_slug(self, obj):
        if obj.category:
            return obj.category.slug
        return None

    def get_category_name(self, obj):
        # Проверяем, существует ли категория у продукта
        if obj.category:
            return obj.category.name
        return None


class SizeProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    size = serializers.StringRelatedField()

    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'price', 'discounted_price']


class SetProductSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', ]  # 'ingredients', ]


class ComboProductSerializer(serializers.ModelSerializer):
    product = SetProductSerializer()
    size = serializers.StringRelatedField()

    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'price', 'discounted_price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price'])
        representation['discounted_price'] = float(representation['discounted_price']) if representation[
                                                                                              'discounted_price'] is not None else None
        return representation


# class SetSerializer(serializers.ModelSerializer):
#     products = ComboProductSerializer(many=True)
#
#     class Meta:
#         model = Set
#         fields = ['id', 'name', 'description', 'photo', 'products', 'price', 'discounted_price', 'bonuses']

# def to_representation(self, instance):
#     representation = super().to_representation(instance)
#     representation['price'] = float(representation['price'])
#     representation['discounted_price'] = float(representation['discounted_price']) if representation[
#                                                                                           'discounted_price'] is not None else None
#     return representation


class CategoryProductSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    # sets = SetSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'image', 'products', 'children']  # 'sets']
    def get_children(self, obj):
        if obj.children.exists():
            return CategoryProductSerializer(obj.children.all(), many=True, context=self.context).data
        return []


class CategoryOnlySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'image', 'children']

    def get_children(self, obj):
        if obj.children.exists():
            return CategoryOnlySerializer(obj.children.all(), many=True).data
        return []

class ProductSizeWithBonusSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_description = serializers.CharField(source='product.description')
    product_photo = serializers.ImageField(source='product.photo')
    size = serializers.CharField(source='size.name')

    def get_bonus_price(self, obj):
        return obj.bonus_price

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['bonus_price'] = float(representation['bonus_price'])
        return representation

    class Meta:
        model = ProductSize
        fields = ['product_name', 'product_description', 'product_photo', 'size', 'id', 'bonus_price']


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'text']


class ProductDetailSerializer(serializers.ModelSerializer):
    toppings = ToppingSerializer(many=True)
    tags = TagSerializer(many=True)
    product_sizes = ProductSizeSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    bonus_price = serializers.SerializerMethodField()
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', 'tags', 'toppings', 'min_price', 'bonus_price', 'bonuses',
                  'product_sizes', 'category_slug', 'category_name', 'kkal', 'proteins', 'fats', 'carbohydrates',
                  'composition', 'shelf_life', 'storage_conditions', 'manufacturer']  # добавлены новые поля

    def get_min_price(self, obj):
        return obj.get_min_price()

    def get_bonus_price(self, obj):
        min_bonus_price = None
        for size in obj.product_sizes.all():
            if min_bonus_price is None or size.bonus_price < min_bonus_price:
                min_bonus_price = size.bonus_price
        return min_bonus_price

    def get_category_slug(self, obj):
        if obj.category:
            return obj.category.slug
        return None

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None
