from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import UserAddress
from apps.orders.models import TelegramBotToken
from apps.services.get_coordinates import get_coordinates


@receiver(pre_save, sender=UserAddress)
def set_coordinates(sender, instance, **kwargs):
    token = TelegramBotToken.objects.first()

    if instance.city and (
            instance.latitude is None or instance.longitude is None):
        address = f"{instance.city}"
        latitude, longitude = get_coordinates(address, token.google_map_api_key)
        if latitude and longitude:
            instance.latitude = latitude
            instance.longitude = longitude

