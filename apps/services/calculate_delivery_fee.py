import math
from django.db.models import Max, Min
from django.core.exceptions import ObjectDoesNotExist

from apps.orders.models import DistancePricing


def get_price_from_db(distance_km):
    if not DistancePricing.objects.exists():
        DistancePricing.objects.create(distance=3, price=150)
        return 150
    if distance_km <= 3:
        return DistancePricing.objects.aggregate(Min('price'))['price__min']
    try:
        pricing = DistancePricing.objects.get(distance=distance_km)
        return pricing.price
    except ObjectDoesNotExist:
        return DistancePricing.objects.filter(distance__lte=distance_km).aggregate(Max('price'))['price__max']


def calculate_delivery_fee(raw_distance_km):
    rounded_distance = math.ceil(raw_distance_km)
    return get_price_from_db(rounded_distance)


