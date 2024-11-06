import time

from celery import shared_task
from .models import Order  # Предполагается, что ваша модель называется Order
from apps.orders.freedompay import check_freedompay_payment_status, cancel_freedompay_payment
from .utils import deduct_bonuses_and_inventory

from celery.exceptions import MaxRetriesExceededError


@shared_task(bind=True, max_retries=20)
def check_order_payment_status(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.payment_status == 'pending':
            # Проверка статуса оплаты
            status = check_freedompay_payment_status(order, deduct_bonuses_and_inventory)
            print(f"Результат проверки статуса для заказа {order.id}: {status}")

            if status == 'pending':
                # Перезапуск задачи, если статус всё ещё "pending"
                raise self.retry(countdown=15)
            elif status == 'success':
                print(f"Заказ {order.id} успешно оплачен")
            else:
                print(f"Ошибка при обработке оплаты для заказа {order.id}")
    except Order.DoesNotExist:
        print(f"Заказ с ID {order_id} не найден.")
    except MaxRetriesExceededError:
        print(
            f"Достигнуто максимальное количество попыток для заказа {order_id}. Меняю статус на 'failed' и отменяю платёж.")

        # Установка статуса 'failed' и отмена платежа
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])

        # Логирование перед отменой
        print(f"Отправка запроса на отмену платежа для заказа {order.id}")

        # Отмена платежа на стороне FreedomPay
        cancel_status = cancel_freedompay_payment(order)

        # Проверка результата отмены платежа
        if cancel_status == 'success':
            print(f"Платёж для заказа {order.id} успешно отменён.")
        else:
            print(f"Ошибка при отмене платежа для заказа {order.id}.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка для заказа {order_id}: {e}")
