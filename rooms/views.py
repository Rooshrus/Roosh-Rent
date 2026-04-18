from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import Room, RoomImage, Booking, CartItem, Message, Review
from .forms import RoomForm, RegisterForm, BookingForm, AgreementForm, ReviewForm
from .serializers import RoomSerializer

class Rooms(TemplateView):
    template_name = 'rooms/rooms.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        qs = Room.objects.filter(is_available=True)

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
        paginator = Paginator(qs, 10)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

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
        files = request.FILES.getlist('pictures')
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.is_available = True
            room.save()
            for f in files:
                RoomImage.objects.create(room=room, image=f)
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

@login_required
def send_message(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            recipient = room.owner if request.user != room.owner else User.objects.get(id=request.POST.get("recipient_id"))
            Message.objects.create(
                room=room,
                sender=request.user,
                recipient=recipient,
                text=text
            )
            return redirect('room_detail', pk=pk)
    return redirect('room_detail', pk=pk)

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    can_delete = request.user.is_authenticated and request.user == room.owner
    bookings = room.bookings.filter(status="confirmed").order_by("start_date")
    form = BookingForm()
    # Перевірка на існуючий відгук користувача
    user_review = None
    if request.user.is_authenticated:
        user_review = room.reviews.filter(user=request.user).first()
    
    # Обробка відгуку (створення або редагування)
    if request.method == "POST" and "submit_review" in request.POST:
        if request.user.is_authenticated:
            # Якщо відгук вже є — редагуємо його, інакше — створюємо новий
            r_form = ReviewForm(request.POST, instance=user_review)
            if r_form.is_valid():
                review = r_form.save(commit=False)
                review.room = room
                review.user = request.user
                review.save()
                msg = "Ваш відгук оновлено!" if user_review else "Ваш відгук додано!"
                messages.success(request, msg)
                return redirect('room_detail', pk=pk)
        else:
            messages.error(request, "Тільки авторизовані користувачі можуть залишати відгуки.")

    # Ініціалізуємо форму даними існуючого відгуку, якщо він є
    review_form = ReviewForm(instance=user_review)
    images = room.images.all().order_by("uploaded_at")

    # Завантажуємо повідомлення для чату
    messages_list = []
    if request.user.is_authenticated:
        messages_list = Message.objects.filter(
            room=room
        ).filter(
            (Q(sender=request.user) & Q(recipient=room.owner)) |
            (Q(sender=room.owner) & Q(recipient=request.user))
        ).order_by('created_at')

    return render(
        request,
        "rooms/room_detail.html",
        {
            "room": room, 
            "can_delete": can_delete, 
            "bookings": bookings, 
            "form": form, 
            "review_form": review_form,
            "user_review": user_review,
            "images": images,
            "chat_messages": messages_list,
            "reviews": room.reviews.all()
        }
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
    return redirect('rooms')

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

from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    FONT_NAME = "DejaVuSans"
    FONT_BOLD = "DejaVuSans-Bold"
except:
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

@login_required
def agreement_form(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == "POST":
        form = AgreementForm(request.POST)
        if form.is_valid():
            return generate_agreement_pdf(booking, form.cleaned_data)
    else:
        form = AgreementForm()
    return render(request, "rooms/agreement_form.html", {"form": form, "booking": booking})

def generate_agreement_pdf(booking, cleaned_data):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="agreement_{booking.id}.pdf"'
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    p.setFont(FONT_BOLD, 16)
    p.drawCentredString(width / 2.0, height - 50, "ДОГОВІР ОРЕНДИ ЖИТЛА")
    p.setFont(FONT_NAME, 12)
    y_position = height - 100
    lines = [
        f"Номер бронювання: {booking.id}",
        f"Орендар: {cleaned_data['full_name']}",
        f"Паспортні дані: {cleaned_data['passport_data']}",
        f"Об'єкт оренди: {booking.room.title or booking.room.address}",
        f"Адреса: {booking.room.address}",
        f"Термін: з {booking.start_date} по {booking.end_date}",
        f"Ціна за добу: ${booking.room.price}",
        f"Додаткові умови: {cleaned_data['extra_terms'] or 'немає'}",
        "",
        "Підписи сторін:",
        "____________________ (Орендар)",
        "",
        "____________________ (Власник)"
    ]
    for line in lines:
        p.drawString(50, y_position, line)
        y_position -= 20
    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

@login_required
def my_bookings(request):
    qs = Booking.objects.filter(user=request.user, status="confirmed").select_related("room")
    return render(request, "rooms/bookings.html", {"bookings": qs})
