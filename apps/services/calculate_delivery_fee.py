import math

from django.db.models import Max

from apps.orders.models import DistancePricing


def get_price_from_db(distance_km):
    # Проверим наличие объектов в базе
    if not DistancePricing.objects.exists():
        # Создаем начальное значение, если в базе пусто
        DistancePricing.objects.create(distance=650, price=15)
        return 15

    # Ищем цену для ближайшего меньшего или равного расстояния
    pricing = DistancePricing.objects.filter(distance__lte=distance_km * 1000).aggregate(Max('price'))

    if pricing['price__max'] is None:
        # Если нет подходящего расстояния, берем максимальную цену
        return DistancePricing.objects.aggregate(Max('price'))['price__max']
    else:
        # Возвращаем найденную цену
        return pricing['price__max']

def calculate_delivery_fee(raw_distance_km):
    rounded_distance = math.ceil(raw_distance_km)
    return get_price_from_db(rounded_distance)