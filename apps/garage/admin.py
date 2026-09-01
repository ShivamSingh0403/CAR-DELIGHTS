from django.contrib import admin
from .models import UserVehicle

@admin.register(UserVehicle)
class UserVehicleAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'nickname', 'registration_number', 'is_primary', 'purchase_year')
    list_filter = ('is_primary', 'vehicle__brand', 'purchase_year')
    search_fields = ('user__username', 'vehicle__model', 'nickname', 'registration_number')
