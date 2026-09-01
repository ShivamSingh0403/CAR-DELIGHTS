from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'display_name', 'phone', 'city', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'preferred_theme')
    search_fields = ('username', 'email', 'display_name', 'phone', 'city')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Info', {
            'fields': ('display_name', 'phone', 'avatar', 'preferred_theme')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode')
        }),
    )
