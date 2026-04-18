from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Room
from .tasks import send_new_room_notification_task
from django.contrib.sites.models import Site

@receiver(post_save, sender=Room)
def notify_on_new_room(sender, instance, created, **kwargs):
    if created:
        # Отримуємо домен сайту. Якщо Site не налаштовано, використовуємо локалхост
        try:
            current_site = Site.objects.get_current()
            domain = f"http://{current_site.domain}"
        except:
            domain = "http://localhost:8000"
        
        # Викликаємо асинхронну задачу Celery
        send_new_room_notification_task.delay(instance.id, domain)
