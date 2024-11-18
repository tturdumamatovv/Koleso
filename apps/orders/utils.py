# utils.py
from decimal import Decimal
from .models import ProductSize

from rest_framework.exceptions import ValidationError

def convert_quantity_to_kg(product_size, ordered_quantity):
    """Конвертирует количество продукта в килограммы, если это необходимо."""
    if product_size.unit == 'g':
        return product_size.quantity * ordered_quantity / Decimal('1000')
    elif product_size.unit == 'kg':
        return product_size.quantity * ordered_quantity
    elif product_size.unit == 'ml':
        return product_size.quantity * ordered_quantity / Decimal('1000')
    elif product_size.unit == 'l':
        return ordered_quantity
    else:
        return ordered_quantity

def deduct_bonuses_and_inventory(order):
    """Списывает бонусы и уменьшает количество товаров после подтверждения оплаты."""
    user = order.user
    user.bonus -= order.partial_bonus_amount
    user.save()
    print(f"Списаны бонусы у пользователя {user.id}, оставшийся бонус: {user.bonus}")

    # Подготовка продуктов и проверка доступности количества
    for item in order.order_items.all():  # Используем related_name "order_items"
        product_size_id = item.product_size.id
        ordered_quantity = item.quantity
        try:
            product_size = ProductSize.objects.get(id=product_size_id)
            product = product_size.product

            # Конвертация заказанного количества в кг, если требуется
            quantity_in_kg = convert_quantity_to_kg(product_size, ordered_quantity)

            # Проверка на наличие достаточного количества
            if product.quantity < quantity_in_kg:
                raise ValidationError(f"Недостаточно товара для {product.name}. Текущий остаток: {product.quantity}")

            # Уменьшение количества товара
            product.quantity -= quantity_in_kg
            product.save()
            print(f"Товар {product.name} обновлён, оставшееся количество: {product.quantity}")

        except ProductSize.DoesNotExist:
            print(f"Продукт с указанным размером не найден (ID: {product_size_id}).")
            raise ValueError(f"Продукт с указанным размером не найден.")
