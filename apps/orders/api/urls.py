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
    CourierPickOrderView,
    CourierOrderDeliverListView,
    CourierCompleteOrderView,
    CourierOrderHistoryView,
    CollectorOrderHistoryView,
    CancelOrderView,
    get_user_orders,
    get_order_details

)

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('orders/<int:pk>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    path('orders/', ListOrderView.as_view(), name='order-list'),
    path('order-preview/', OrderPreviewView.as_view(), name='order-preview'),
    path('reports/', ReportCreateView.as_view(), name='create-report'),
    path('restaurants/', RestaurantListView.as_view(), name='restaurant-list'),
    path('collector/orders/', CollectorOrderListView.as_view(), name='collector-orders-list'),
    path('collector/orders/<int:pk>/ready/', CollectorOrderUpdateView.as_view(), name='collector-order-ready'),
    path('courier/orders/ready/', CourierOrderReadyListView.as_view(), name='courier-orders-ready'),
    path('courier/orders/<int:pk>/pick/', CourierPickOrderView.as_view(), name='courier-pick-order'),
    path('courier/order/delivery/', CourierOrderDeliverListView.as_view(), name='courier-order-delivery'),
    path('courier/order/<int:pk>/complete/', CourierCompleteOrderView.as_view(), name='courier-complete-order'),
    path('courier/orders/history/', CourierOrderHistoryView.as_view(), name='courier-order-history'),
    path('collector/orders/history/', CollectorOrderHistoryView.as_view(), name='collector-order-history'),
    path('user/orders/', get_user_orders, name='user_orders'),
    path('details/', get_order_details, name='get_order_details'),
]
