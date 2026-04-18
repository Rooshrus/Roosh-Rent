from django.contrib import admin, messages
from .models import Room, RoomImage, Booking, Review
from .tasks import send_new_room_notification_task
from django.contrib.sites.models import Site

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

@admin.action(description='Надіслати сповіщення підписникам')
def send_notification(modeladmin, request, queryset):
    try:
        current_site = Site.objects.get_current()
        domain = f"http://{current_site.domain}"
    except:
        domain = "http://localhost:8000"
    
    count = 0
    for room in queryset:
        send_new_room_notification_task.delay(room.id, domain)
        count += 1
    
    modeladmin.message_user(request, f"Запущено розсилку для {count} оголошень.", messages.SUCCESS)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at', 'rooms')
    search_fields = ('title', 'address', 'description')
    inlines = [RoomImageInline]
    actions = [send_notification]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'rating', 'created_at')

admin.site.register(RoomImage)
