import os
from celery import Celery

# Встановлюємо модуль налаштувань за замовчуванням для 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rent.settings')

app = Celery('rent')

# Використовуємо рядок для конфігурації, щоб воркер не мусив серіалізувати об'єкт
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматичне виявлення задач у файлах tasks.py ваших додатків
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
