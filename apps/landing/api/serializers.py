from rest_framework import serializers
from apps.landing.models import (
    MainPageSite, ServiceFeature, ServiceFeatureStep, StaticPage,
    PaymentMethod, Product, SubProduct, ConvenientFunctionality,
    ConvenientFunctionalityChapter
)

# Serializer for ServiceFeatureStep, to be included in ServiceFeatureSerializer
class ServiceFeatureStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFeatureStep
        fields = '__all__'

# Serializer for ServiceFeature with nested ServiceFeatureStep
class ServiceFeatureSerializer(serializers.ModelSerializer):
    servicefeaturestep_set = ServiceFeatureStepSerializer(many=True, read_only=True)  # Nested steps

    class Meta:
        model = ServiceFeature
        fields = '__all__'


# Serializer for ConvenientFunctionalityChapter, to be included in ConvenientFunctionalitySerializer
class ConvenientFunctionalityChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConvenientFunctionalityChapter
        fields = '__all__'

# Serializer for ConvenientFunctionality with nested ConvenientFunctionalityChapter
class ConvenientFunctionalitySerializer(serializers.ModelSerializer):
    convenientfunctionalitychapter_set = ConvenientFunctionalityChapterSerializer(many=True, read_only=True)  # Nested chapters

    class Meta:
        model = ConvenientFunctionality
        fields = '__all__'


# Serializer for PaymentMethod
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


# Serializer for MainPageSite
class MainPageSiteSerializer(serializers.ModelSerializer):
    payment_method = PaymentMethodSerializer(source='paymentmethod_set', many=True, read_only=True)  # Display related PaymentMethod links

    class Meta:
        model = MainPageSite
        fields = ("icon", 'title', 'description', 'subtitle', 'image', 'download_text',
                  'google_play_icon', 'google_play_link', 'app_store_icon', 'app_store_link',
                  'meta_title', 'meta_description', 'meta_image', 'payment_method')


# Serializer for StaticPage
class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = '__all__'


class SubProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubProduct
        fields = '__all__'


# Serializer for Product
class ProductSerializer(serializers.ModelSerializer):
    subproducts = SubProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('image', 'subproducts')
