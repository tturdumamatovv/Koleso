import hashlib
import requests
import uuid

from apps.pages.models import PaymentSettings

import xml.etree.ElementTree as ET


payment_settings = PaymentSettings.objects.first()
if payment_settings:
    PAYBOX_URL = payment_settings.paybox_url
    PAYBOX_MERCHANT_ID = payment_settings.merchant_id
else:
    PAYBOX_URL = ''
    PAYBOX_MERCHANT_ID = ''


def make_flat_params_array(arr_params, parent_name=''):
    flat_params = {}
    i = 0
    for key, val in arr_params.items():
        i += 1
        name = f"{parent_name}{key}{i:03d}"
        if isinstance(val, dict):
            flat_params.update(make_flat_params_array(val, name))
        else:
            flat_params[name] = str(val)
    return flat_params


def generate_signature(request, script_name):
    payment_settings = PaymentSettings.objects.first()
    if not payment_settings:
        raise ValueError("Payment settings are not configured.")

    secret_key = payment_settings.merchant_secret
    flat_request = make_flat_params_array(request)
    ksorted_request = dict(sorted(flat_request.items()))

    # Отладка: вывод значений для подписи
    print("Flat request parameters:", flat_request)
    print("Sorted request parameters:", ksorted_request)

    values_list = [script_name] + list(ksorted_request.values()) + [secret_key]
    concat_string = ';'.join(values_list)

    # Отладка: вывод строки для хеширования
    print("String to hash for signature:", concat_string)

    return hashlib.md5(concat_string.encode()).hexdigest()


def send_get_request(endpoint, params):
    url = PAYBOX_URL + endpoint
    response = requests.get(url, params=params)
    return response.json()


def send_post_request(endpoint, data):
    url = PAYBOX_URL + endpoint
    response = requests.post(url, data=data)
    print("Response Text:", response.text)
    try:
        return response.json()
    except ValueError:
        try:
            root = ET.fromstring(response.text)
            response_dict = {child.tag: child.text for child in root}
            return response_dict
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return {"error": "Invalid XML response", "response_text": response.text}


def check_freedompay_payment_status(order, deduct_bonuses_and_inventory):
    """Проверяет статус оплаты через FreedomPay."""
    payment_settings = PaymentSettings.objects.first()
    pg_salt = uuid.uuid4().hex
    pg_merchant_id = payment_settings.merchant_id

    request_data = {
        'pg_merchant_id': pg_merchant_id,
        'pg_payment_id': order.payment_id,
        'pg_salt': pg_salt,
    }

    signature = generate_signature(request_data, 'get_status3.php')
    request_data['pg_sig'] = signature

    response = send_post_request('/get_status3.php', request_data)

    if response.get('pg_payment_status') == 'success':
        order.payment_status = 'completed'
        order.save()
        print(f"Оплата подтверждена для заказа {order.id}, списание бонусов и товаров...")
        deduct_bonuses_and_inventory(order)  # Списываем бонусы и количество
        return 'success'
    elif response.get('pg_payment_status') == 'error':
        order.payment_status = 'failed'
        order.save()
        print(f"Ошибка оплаты для заказа {order.id}")
        return 'error'
    print(f"Платёж в статусе ожидания для заказа {order.id}")
    return 'pending'


def cancel_freedompay_payment(order):
    payment_settings = PaymentSettings.objects.first()
    url = f"{payment_settings.paybox_url}/cancel.php"
    request_data = {
        'pg_merchant_id': payment_settings.merchant_id,
        'pg_payment_id': order.payment_id,
        'pg_salt': uuid.uuid4().hex,
    }
    request_data['pg_sig'] = generate_signature(request_data, 'cancel.php')

    try:
        response = requests.post(url, data=request_data)
        response.raise_for_status()

        response_text = response.text
        print("Response Text (Cancel):", response_text)

        root = ET.fromstring(response_text)
        response_data = {child.tag: child.text for child in root}

        if response_data.get('pg_status') == 'ok':
            print(f"Платеж для заказа {order.id} успешно отменен.")
            order.payment_status = 'failed'
            order.save()
            return 'success'
        else:
            error_description = response_data.get('pg_error_description', 'Неизвестная ошибка')
            print(f"Ошибка при отмене платежа для заказа {order.id}: {error_description}")
            return 'error'
    except requests.RequestException as e:
        print(f"Ошибка запроса к FreedomPay: {e}")
        return 'error'
