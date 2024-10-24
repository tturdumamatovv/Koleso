def generate_order_message(order, delivery_distance_km, delivery_fee):
    if delivery_distance_km is None:
        delivery_distance_km = 0
    if order.is_pickup:
        delivery_info = "Самовывоз"
        delivery_fee_info = ""
    else:
        delivery_info = (
            f"Расстояние доставки: {delivery_distance_km} км\n"
            f"Стоимость доставки: {delivery_fee} сом\n"
        )
        delivery_fee_info = f"Стоимость доставки: {delivery_fee} сом\n"

    payment_info = (
        f"Способ оплаты: {order.get_payment_method_display()}\n"
    )
    if order.payment_method == 'cash':
        payment_info += f"Сумма наличными: {order.change if order.change else 0} сом\n"
        payment_info += f"Сдача: {order.change - order.total_amount if order.change else 0} сом\n"

    message = (
        f"Новый заказ #{order.id}\n"
        f"Пользователь: {order.user.full_name if order.user and order.user.full_name else 'Имя не указано'}\n"
        f"Номер: {order.user.phone_number if order.user and order.user.phone_number else 'Номер не указан'}\n"

        f"Ресторан: {order.restaurant.name}\n"

        "ЗАКАЗ:\n"
        "===============\n"
    )
    message += "-----------------\n"

    for item in order.order_items.all():
        if item.product_size:
            item_details = f"Продукт: {item.product_size.product.name} ({item.product_size.size})\n"
        # else:
            # item_details = f"Сет: {item.set.name}\n"

        item_details += f"Количество: {item.quantity}\n"

        if not item.is_bonus:
            item_details += f"Сумма: {item.total_amount}\n"
        else:
            item_details += f"БОНУСНЫЙ ПРОДУКТ\n"

        if item.topping.exists():
            item_details += "Топинги:\n"
            for topping in item.topping.all():
                item_details += f" - {topping.name}\n"

        # if item.excluded_ingredient.exists():
        #     item_details += "Исключенные ингредиенты:\n"
        #     for ingredient in item.excluded_ingredient.all():
        #         item_details += f" - {ingredient.name}\n"

        message += item_details + "-----------------\n"
    message += "===============\n"

    user_address = order.delivery.user_address

    address = (
        f"Адрес: {user_address.city if user_address else 'Самовывоз'}\n"
        # f"Адрес: {user_address.street} {user_address.house_number}\n"
    )

    if user_address and user_address.apartment_number:
        address += f"Квартира: {user_address.apartment_number}\n"

    if user_address and user_address and user_address.entrance:
        address += f"Подъезд: {user_address.entrance}\n"

    if user_address and user_address.floor:
        address += f"Этаж: {user_address.floor}\n"

    if user_address and user_address.intercom:
        address += f"Домофон: {user_address.intercom}\n"

    if user_address and user_address.comment:
        address += f"Комментарий: {user_address.comment}\n"


    message += (
        f"Адрес доставки:\n{address if not order.is_pickup else ''}\n"
        # f"Статус: {order.get_order_status_display()}\n \n"
        f"{delivery_info}\n"
        f"{payment_info}\n"
        f"Общая сумма: {order.total_amount}\n"

    )
    if order.comment:
        message += f"Комментарий: {order.comment}\n"

    return message



def format_order_status_change_message(order_date, order_id, order_status):
    formatted_date = order_date.strftime('%d.%m.%Y %H:%M')
    return (
        f"Статус вашего заказа {order_id} изменен на {order_status}.\n"
        f"Дата заказа: {formatted_date}"
    )
