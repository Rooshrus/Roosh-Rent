from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Room, RoomImage, Booking, CartItem
from .forms import RoomForm, RegisterForm, BookingForm
from .serializers import RoomSerializer

class Rooms(TemplateView):
    template_name = 'rooms/rooms.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        qs = Room.objects.filter(is_available=True)

        # фільтри
        q = self.request.GET.get("q")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        rooms = self.request.GET.get("rooms")

        if q:
            qs = qs.filter(Q(address__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if rooms:
            try:
                rooms_int = int(rooms)
                qs = qs.filter(rooms=rooms_int)
            except ValueError:
                pass

        qs = qs.order_by('-created_at')
        paginator = Paginator(qs, 10)  # 10 оголошень на сторінці
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        # Топ-5 найпопулярніших (підтверджені бронювання)
        top_qs = Room.objects.filter(is_available=True).annotate(
            bookings_count=Count('bookings', filter=Q(bookings__status='confirmed'))
        ).order_by('-bookings_count', '-created_at')[:5]

        context['rooms'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['top_rooms'] = top_qs
        return context

@login_required
def add_room(request, *args, **kwargs):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        files = request.FILES.getlist('pictures')  # очікуємо input name="pictures" multiple
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.is_available = True
            # Якщо ви хочете, щоб головне picture брало перший з uploaded files:
            if files:
                # тимчасово не зберюємо picture — спочатку save room
                pass
            room.save()
            # зберігаємо перші фото як RoomImage
            for f in files:
                RoomImage.objects.create(room=room, image=f)
            # якщо головне поле picture пусте, пишемо перше з images як picture для сумісності (опціонально)
            if not room.picture and room.images.exists():
                first = room.images.first()
                room.picture = first.image
                room.save()
            messages.success(request, "Оголошення додано.")
            return redirect('room_detail', pk=room.pk)
        else:
            messages.error(request, "Перевірте форму.")
    else:
        form = RoomForm()
    return render(request, 'rooms/room.html', {"form": form})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    can_delete = request.user.is_authenticated and request.user == room.owner
    bookings = room.bookings.filter(status="confirmed").order_by("start_date")
    form = BookingForm()
    images = room.images.all().order_by("uploaded_at")
    return render(
        request,
        "rooms/room_detail.html",
        {"room": room, "can_delete": can_delete, "bookings": bookings, "form": form, "images": images}
    )

@login_required
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if room.owner != request.user:
        messages.error(request, "Видалити може тільки власник.")
        return redirect('room_detail', pk=pk)
    room.delete()
    messages.success(request, "Оголошення видалено.")
    return redirect('rooms')

@login_required
def my_rooms(request):
    qs = Room.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, "rooms/my_rooms.html", {"rooms": qs})

@api_view(['GET'])
def roomsApi(request, *args, **kwargs):
    qs = Room.objects.filter(is_available=True).annotate(
        bookings_count=Count('bookings', filter=Q(bookings__status='confirmed'))
    )
    q = request.GET.get("q")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    rooms = request.GET.get("rooms")
    if q:
        qs = qs.filter(Q(address__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q))
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)
    if rooms:
        try:
            rooms_int = int(rooms)
            qs = qs.filter(rooms=rooms_int)
        except ValueError:
            pass
    serializer = RoomSerializer(qs.order_by('-created_at'), many=True, context={"request": request})
    return Response(serializer.data)

def index(request):
    # Замість показу порожньої сторінки — редірект на rooms
    return redirect('rooms')



# ---------- CART ----------
@login_required
def cart_add(request, pk):
    room = get_object_or_404(Room, pk=pk)
    CartItem.objects.get_or_create(user=request.user, room=room)
    messages.success(request, "Додано до кошика.")
    return redirect('room_detail', pk=pk)

@login_required
def cart_remove(request, pk):
    room = get_object_or_404(Room, pk=pk)
    CartItem.objects.filter(user=request.user, room=room).delete()
    messages.info(request, "Видалено з кошика.")
    return redirect('cart')

@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user).select_related("room")
    return render(request, "rooms/cart.html", {"items": items})

# ---------- BOOKINGS ----------
@login_required
def book_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method != "POST":
        return redirect('room_detail', pk=pk)

    form = BookingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Невірні дати.")
        return redirect('room_detail', pk=pk)

    booking = form.save(commit=False)
    start = booking.start_date
    end = booking.end_date

    if start > end:
        messages.error(request, "Кінцева дата раніше початкової.")
        return redirect('room_detail', pk=pk)

    if not room.is_range_available(start, end):
        messages.error(request, "Обрані дати вже зайняті.")
        return redirect('room_detail', pk=pk)

    booking.room = room
    booking.user = request.user
    booking.status = "confirmed"
    booking.save()

    messages.success(request, f"Заброньовано: {start} → {end}.")
    return redirect('my_bookings')

@login_required
def my_bookings(request):
    qs = Booking.objects.filter(user=request.user, status="confirmed").select_related("room")
    return render(request, "rooms/bookings.html", {"bookings": qs})
