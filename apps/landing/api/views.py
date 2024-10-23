from rest_framework import generics
from drf_spectacular.utils import extend_schema
from apps.landing.models import (
    MainPageSite, ServiceFeature, StaticPage, PaymentMethod, Product, SubProduct, ConvenientFunctionality
)
from .serializers import (
    MainPageSiteSerializer, ServiceFeatureSerializer, StaticPageSerializer,
    PaymentMethodSerializer, ProductSerializer, SubProductSerializer, ConvenientFunctionalitySerializer
)

# MainPageSite View
class MainPageSiteView(generics.ListAPIView):
    queryset = MainPageSite.objects.all()
    serializer_class = MainPageSiteSerializer

    @extend_schema(summary="Retrieve Main Page Site Info")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ServiceFeature View with nested ServiceFeatureSteps
class ServiceFeatureView(generics.ListAPIView):
    queryset = ServiceFeature.objects.all()
    serializer_class = ServiceFeatureSerializer

    @extend_schema(summary="Retrieve Service Features with Steps")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# StaticPage View with slug-based retrieval
class StaticPageView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'

    @extend_schema(summary="Retrieve Static Page by Slug")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# PaymentMethod View
class PaymentMethodView(generics.ListAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

    @extend_schema(summary="Retrieve Payment Methods")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Product View
class ProductView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @extend_schema(summary="Retrieve Products")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# SubProduct View
class SubProductView(generics.ListAPIView):
    queryset = SubProduct.objects.all()
    serializer_class = SubProductSerializer

    @extend_schema(summary="Retrieve SubProducts")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# ConvenientFunctionality View with nested ConvenientFunctionalityChapters
class ConvenientFunctionalityView(generics.ListAPIView):
    queryset = ConvenientFunctionality.objects.all()
    serializer_class = ConvenientFunctionalitySerializer

    @extend_schema(summary="Retrieve Convenient Functionalities with Chapters")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
