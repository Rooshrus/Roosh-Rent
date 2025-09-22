from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rooms import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rooms
    path('', views.index, name='index'),
    path('rooms/', views.Rooms.as_view(), name='rooms'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:pk>/delete/', views.delete_room, name='room_delete'),
    path('addroom/', views.add_room, name='add_room'),
    path('myrooms/', views.my_rooms, name='my_rooms'),
    path('roomsapi/', views.roomsApi, name='roomsApi'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:pk>/', views.cart_remove, name='cart_remove'),

    # Bookings
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('rooms/<int:pk>/book/', views.book_room, name='book_room'),

    # Auth (allauth)
    path('accounts/', include('allauth.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
