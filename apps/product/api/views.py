from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from apps.product.api.filters import ProductFilter
from apps.product.api.serializers import ProductSerializer, CategoryProductSerializer, \
    CategoryOnlySerializer, ProductSizeWithBonusSerializer, ArticleSerializer, ProductDetailSerializer
from apps.product.models import Category, Product, ProductSize, Article  # Set


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductBonusView(generics.ListAPIView):
    queryset = ProductSize.objects.filter(
        product__bonuses=True,
        bonus_price__gt=0
    )
    serializer_class = ProductSizeWithBonusSerializer


class ProductListByCategorySlugView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise NotFound("Категория не найдена")

        products = Product.objects.filter(category=category, product_sizes__isnull=False).distinct().order_by('order')
        # sets = Set.objects.filter(category=category)

        product_serializer = ProductSerializer(products, many=True, context={'request': request})
        # set_serializer = SetSerializer(sets, many=True, context={'request': request})

        return Response({
            'products': product_serializer.data,
            # 'sets': set_serializer.data
        })


# class SetListView(generics.ListAPIView):
#     serializer_class = SetSerializer
#
#     def get_queryset(self):
#         return Set.objects.prefetch_related(
#             'products__product__ingredients',
#             'products__product__toppings',
#             'products__size'
#         )


class CategoryListView(generics.ListAPIView):
    serializer_class = CategoryProductSerializer

    def get(self, request, *args, **kwargs):
        categories = Category.objects.prefetch_related('products').filter(parent=None)
        serializer = CategoryProductSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryOnlyListView(generics.ListAPIView):
    serializer_class = CategoryOnlySerializer

    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(parent=None)
        serializer = CategoryOnlySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class PopularProducts(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_popular=True)


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get(self, request, *args, **kwargs):
        articles = Article.objects.filter(product=self.kwargs['product_id'])
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'
