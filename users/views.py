from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rooms.models import Room, Booking, Message
from django.db.models import Max
from django.contrib import messages

@login_required
def profile(request):
    if request.method == 'POST' and 'toggle_subscription' in request.POST:
        profile = request.user.profile
        profile.is_subscribed = not profile.is_subscribed
        profile.save()
        status = "активовано" if profile.is_subscribed else "деактивовано"
        messages.success(request, f"Підписку на розсилку {status}.")
        return redirect('profile')

    user_rooms = Room.objects.filter(owner=request.user)
    user_bookings = Booking.objects.filter(user=request.user).select_related('room')
    
    # Отримуємо унікальні чати (групуємо за кімнатою та співрозмовником)
    # Це спрощена версія: показуємо всі повідомлення, де користувач є відправником або отримувачем
    chats = Message.objects.filter(
        recipient=request.user
    ).values('room', 'sender').annotate(last_msg=Max('created_at')).order_by('-last_msg')
    
    # Додатково чати, де користувач відправляв повідомлення (відповіді)
    sent_chats = Message.objects.filter(
        sender=request.user
    ).values('room', 'recipient').annotate(last_msg=Max('created_at')).order_by('-last_msg')

    context = {
        'user_rooms': user_rooms,
        'user_bookings': user_bookings,
        'chats': chats,
        'sent_chats': sent_chats,
    }
    return render(request, 'users/profile.html', context)
