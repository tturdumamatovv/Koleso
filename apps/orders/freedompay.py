import hashlib
from apps.pages.models import PaymentSettings

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
    # Получаем настройки платежа
    payment_settings = PaymentSettings.objects.first()
    if not payment_settings:
        raise ValueError("Payment settings are not configured.")

    secret_key = payment_settings.merchant_secret
    flat_request = make_flat_params_array(request)
    ksorted_request = dict(sorted(flat_request.items()))
    values_list = [script_name] + list(ksorted_request.values()) + [secret_key]
    concat_string = ';'.join(values_list)
    return hashlib.md5(concat_string.encode()).hexdigest()
