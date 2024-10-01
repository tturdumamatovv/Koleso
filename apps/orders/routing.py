from django.urls import path
import apps.orders.consumers as consumers
ws_urlpatterns = [
    path('ws/notification/', consumers.WSConsumer.as_asgi()),
]
