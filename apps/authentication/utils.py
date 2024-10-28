import requests
import uuid
import random
from django.conf import settings
from xml.etree import ElementTree as ET
from apps.pages.models import SMSSettings  # Импортируйте вашу модель

def generate_confirmation_code():
    confirmation_code = ''.join(random.choices('0123456789', k=4))
    print(confirmation_code)
    return confirmation_code

def send_sms(phone_number, confirmation_code):
    # Получаем настройки SMS
    sms_settings = SMSSettings.objects.first()
    if not sms_settings:
        raise ValueError("SMS settings are not configured.")

    login = sms_settings.login
    password = sms_settings.password
    sender = sms_settings.sender
    transaction_id = str(uuid.uuid4())
    text = f'Your confirmation code is: {confirmation_code}'

    request_body = ET.Element("message")
    ET.SubElement(request_body, "login").text = login
    ET.SubElement(request_body, "pwd").text = password
    ET.SubElement(request_body, "id").text = transaction_id
    ET.SubElement(request_body, "sender").text = sender
    ET.SubElement(request_body, "text").text = text
    phones_element = ET.SubElement(request_body, "phones")
    ET.SubElement(phones_element, "phone").text = phone_number
    print(phone_number)

    if settings.DEBUG:
        ET.SubElement(request_body, "test").text = "0"

    request_body_str = ET.tostring(request_body, encoding="UTF-8", method="xml")

    url = 'https://smspro.nikita.kg/api/message'
    headers = {'Content-Type': 'application/xml'}

    response = requests.post(url, data=request_body_str, headers=headers)
    if response.status_code == 200:
        print(response)
        print(response.content)
        print('SMS sent successfully')
    else:
        print('Failed to send SMS')
