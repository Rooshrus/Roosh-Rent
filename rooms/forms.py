from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Booking, Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} зірок") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Поділіться вашими враженнями..."}),
        }

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

class AgreementForm(forms.Form):
    full_name = forms.CharField(label="Повне ім'я (ПІБ)", max_length=200)
    passport_data = forms.CharField(label="Паспортні дані", max_length=300, widget=forms.Textarea(attrs={'rows': 2}))
    extra_terms = forms.CharField(label="Додаткові умови (опціонально)", required=False, widget=forms.Textarea(attrs={'rows': 2}))

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email")
