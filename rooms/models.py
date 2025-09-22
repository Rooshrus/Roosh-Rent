from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import date

def room_image_upload_to(instance, filename):
    return f"rooms/{instance.room.owner_id}/{instance.room.id}/{filename}"

class Room(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms", default=1)
    title = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    address = models.CharField(max_length=300)
    coordX = models.FloatField()
    coordY = models.FloatField()

    # Головне зображення (опціонально) — зворотна сумісність
    picture = models.ImageField(upload_to=room_image_upload_to, blank=True, null=True)

    description = models.TextField(blank=True)
    rooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    area = models.PositiveIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"{self.address} — {self.price}$"

    @property
    def image_url(self):
        # повертає головне фото або плейсхолдер
        if self.picture:
            return self.picture.url
        first = self.images.first()
        if first:
            return first.image.url
        return "/static/rooms/images/placeholder.jpg"

    def is_range_available(self, start: date, end: date) -> bool:
        overlap = self.bookings.filter(
            status="confirmed",
            start_date__lte=end,
            end_date__gte=start
        ).exists()
        return not overlap

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=room_image_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.room.pk} — {self.image.name}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Очікує"),
        ("confirmed", "Підтверджено"),
        ("cancelled", "Скасовано"),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.room} [{self.start_date} → {self.end_date}]"

    def clean(self):
        if self.end_date < self.start_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("Кінцева дата не може бути раніше за початкову.")

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="in_carts")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "room")
        ordering = ["-added_at"]

    def __str__(self):
        return f"CartItem({self.user} -> {self.room})"
