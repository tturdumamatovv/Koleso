from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Задайте настройки Django для использования в Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создайте приложение Celery
app = Celery('config')

# Загрузите настройки из конфигурации Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживайте задачи в установленных приложениях
app.autodiscover_tasks()
