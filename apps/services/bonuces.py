import logging

from decimal import Decimal

from apps.orders.models import PercentCashback

logger = logging.getLogger(__name__)


def calculate_bonus_points(order_total, order_source):
    percents = PercentCashback.objects.all().first()
    if not percents:
        percents = PercentCashback.objects.create(mobile_percent=5, web_percent=3)

    BONUS_PERCENTAGE_MOBILE = percents.mobile_percent
    BONUS_PERCENTAGE_WEB = percents.web_percent
    total_order_amount = order_total
    if order_source == 'mobile':
        bonus_percentage = BONUS_PERCENTAGE_MOBILE
    elif order_source == 'web':
        bonus_percentage = BONUS_PERCENTAGE_WEB
    else:
        bonus_percentage = Decimal('0.0')

    bonus_points = total_order_amount * (bonus_percentage / Decimal('100'))
    return bonus_points


def apply_bonus_points(user, bonus_points):
    if user.bonus is None:
        user.bonus = 0
    user.bonus += bonus_points
    user.save()


def restore_stock_and_bonus(order):
    """Восстанавливает запасы и возвращает бонусы при отмене заказа."""
    UNIT_CONVERSIONS = {
        'g': Decimal('0.001'),  # граммы в килограммы
        'kg': Decimal('1'),     # килограммы остаются без изменений
        'ml': Decimal('0.001'), # миллилитры в литры
        'l': Decimal('1'),      # литры остаются без изменений
        'pcs': Decimal('1'),    # штучный товар без изменений
    }

    for order_item in order.order_items.all():
        product_size = order_item.product_size
        if not product_size or not product_size.product:
            continue

        ordered_quantity = Decimal(order_item.quantity)
        size_quantity = Decimal(product_size.quantity)
        actual_quantity_to_restore = ordered_quantity * size_quantity

        unit = product_size.unit
        conversion_rate = UNIT_CONVERSIONS.get(unit, Decimal('1'))

        # Восстанавливаемое количество в базовых единицах
        restored_quantity = actual_quantity_to_restore * conversion_rate
        product = product_size.product
        product.quantity += restored_quantity
        product.save()

        logger.info(
            f"Restored {actual_quantity_to_restore} {unit} ({restored_quantity} base units) to {product.name}. "
            f"New stock quantity: {product.quantity}"
        )

    # Восстанавливаем бонусные баллы, если они были использованы
    if order.partial_bonus_amount:
        user = order.user
        user.bonus += order.partial_bonus_amount
        user.save()
        logger.info(f"Returned {order.partial_bonus_amount} bonus points to user {user.phone_number}. "
                    f"New bonus balance: {user.bonus}")
