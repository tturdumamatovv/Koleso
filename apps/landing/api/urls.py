from django.urls import path
from .views import (
    MainPageSiteView, ServiceFeatureView, StaticPageView,
    PaymentMethodView, ProductView, SubProductView, ConvenientFunctionalityView
)

urlpatterns = [
    path('main-page-site/', MainPageSiteView.as_view(), name='main-page-site'),
    path('service-features/', ServiceFeatureView.as_view(), name='service-features'),
    path('static-pages/slug/<slug:slug>/', StaticPageView.as_view(), name='static-page-by-slug'),
    path('payment-methods/', PaymentMethodView.as_view(), name='payment-methods'),
    path('products/', ProductView.as_view(), name='products'),
    path('sub-products/', SubProductView.as_view(), name='sub-products'),
    path('convenient-functionalities/', ConvenientFunctionalityView.as_view(), name='convenient-functionalities'),
]
