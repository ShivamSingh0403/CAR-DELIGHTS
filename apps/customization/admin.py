from django.contrib import admin
from .models import PaintOption, CustomBuild

@admin.register(PaintOption)
class PaintOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'finish_type', 'hex_color', 'price', 'is_featured')
    list_filter = ('finish_type', 'is_featured')
    search_fields = ('name', 'hex_color')

@admin.register(CustomBuild)
class CustomBuildAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle', 'user', 'paint', 'total_price', 'created_at')
    list_filter = ('vehicle__brand', 'created_at')
    search_fields = ('name', 'vehicle__model', 'user__username')
