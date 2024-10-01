import django_filters

from apps.product.models import Product


class ProductFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['id', 'name']
