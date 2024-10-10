from apps.product.models import ProductSize, Product, Category
from unfold.admin import forms


class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'price', 'discounted_price', 'bonus_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'product' in self.initial:
            product = self.initial['product']
        elif 'product' in self.data:
            product = self.data['product']
        else:
            product = None

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем категории, оставляя только конечные (без подкатегорий)
        self.fields['category'].queryset = Category.objects.filter(children__isnull=True)
