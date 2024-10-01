from django.urls import path
from .views import (
    CreateOrderView,
    OrderPreviewView,
    ReportCreateView,
    RestaurantListView,
    ListOrderView,
    CollectorOrderListView,
    CollectorOrderUpdateView,
    CourierOrderReadyListView,
    CourierPickOrderView
)

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', ListOrderView.as_view(), name='order-list'),
    path('order-preview/', OrderPreviewView.as_view(), name='order-preview'),
    path('reports/', ReportCreateView.as_view(), name='create-report'),
    path('restaurants/', RestaurantListView.as_view(), name='restaurant-list'),
    path('collector/orders/', CollectorOrderListView.as_view(), name='collector-orders-list'),
    path('collector/orders/<int:pk>/ready/', CollectorOrderUpdateView.as_view(), name='collector-order-ready'),
    path('courier/orders/ready/', CourierOrderReadyListView.as_view(), name='courier-orders-ready'),
    path('courier/orders/<int:pk>/pick/', CourierPickOrderView.as_view(), name='courier-pick-order'),
]
