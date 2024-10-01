from datetime import datetime, time


def is_restaurant_open(restaurant, order_time):
    return True
    # if restaurant.opening_hours and isinstance(restaurant.opening_hours, str):
    #     opening_hours = restaurant.opening_hours.split('-')
    #     if len(opening_hours) == 2:
    #         try:
    #             opening_time = datetime.strptime(opening_hours[0].strip(), '%H:%M').time()
    #             closing_time = datetime.strptime(opening_hours[1].strip(), '%H:%M').time()
    #
    #             if opening_time < closing_time:
    #                 # Ресторан работает в пределах одного дня
    #                 return opening_time <= order_time.time() <= closing_time
    #             else:
    #                 # Ресторан работает через полночь
    #                 return order_time.time() >= opening_time or order_time.time() <= closing_time
    #         except ValueError:
    #             # Обработка некорректного формата времени
    #             return False
    # return False
