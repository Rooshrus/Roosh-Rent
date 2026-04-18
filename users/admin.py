from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профіль'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_is_subscribed',)

    def get_is_subscribed(self, instance):
        return instance.profile.is_subscribed
    get_is_subscribed.short_description = 'Підписка'
    get_is_subscribed.boolean = True

# Перереєструємо UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
