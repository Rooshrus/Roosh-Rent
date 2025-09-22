from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Booking

class RoomForm(forms.ModelForm):
    # прибираємо старе picture повністю із відображення, додаємо окреме поле в шаблоні для множинного upload
    class Meta:
        model = Room
        exclude = ("owner", "is_available",)
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Короткий опис житла"}),
            "phone": forms.TextInput(attrs={"placeholder": "Номер телефону"}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("start_date", "end_date")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "id": "js-start-date"}),
            "end_date": forms.DateInput(attrs={"type": "date", "id": "js-end-date"}),
        }

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
