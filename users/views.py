from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rooms.models import Room, Booking

@login_required
def profile(request):
    user_rooms = Room.objects.filter(owner=request.user)
    user_bookings = Booking.objects.filter(user=request.user).select_related('room')
    
    context = {
        'user_rooms': user_rooms,
        'user_bookings': user_bookings,
    }
    return render(request, 'users/profile.html', context)
