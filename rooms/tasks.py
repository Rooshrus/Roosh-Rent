from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from .models import Room

@shared_task
def send_new_room_notification_task(room_id, site_url):
    try:
        room = Room.objects.get(pk=room_id)
        # Отримуємо всіх користувачів, які підписані
        # Оскільки ми додали Profile, фільтруємо через нього
        users = User.objects.filter(profile__is_subscribed=True).exclude(email='')
        recipient_list = list(users.values_list('email', flat=True))
        
        if not recipient_list:
            return "No recipients subscribed."

        subject = f"Нова кімната: {room.title}"
        room_url = f"{site_url}/rooms/{room.id}/" # Або як у вас побудовані URL
        
        context = {
            'room': room,
            'room_url': room_url,
        }
        
        html_content = render_to_string('emails/new_room_notification.html', context)
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f"Sent notifications for room {room_id} to {len(recipient_list)} users."
    except Room.DoesNotExist:
        return f"Room {room_id} does not exist."
    except Exception as e:
        return str(e)
