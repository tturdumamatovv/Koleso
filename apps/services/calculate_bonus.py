from decimal import Decimal


def calculate_and_apply_bonus(order):
    total_order_amount = Decimal('0.00')
    total_bonus_amount = Decimal('0.00')
    user = order.user

    for order_item in order.order_items.all():
        if order_item.is_bonus:
            total_bonus_amount += order_item.calculate_total_amount()
        else:
            total_order_amount += order_item.calculate_total_amount()

    if user.bonus is None:
        user.bonus = 0
    print(total_bonus_amount, user.bonus)
    if total_bonus_amount > user.bonus:
        raise ValueError("Not enough bonus points.")

    user.bonus -= total_bonus_amount  # Use the bonuses
    user.save()

    order.total_amount = total_order_amount
    order.save()

    return total_order_amount
