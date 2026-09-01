from django.contrib import admin
from .models import ServiceCategory, Service, ServiceBooking

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'slug', 'service_count')
    prepopulated_fields = {'slug': ('name',)}

    def service_count(self, obj):
        return obj.services.count()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'is_featured', 'is_active', 'booking_available')
    list_filter = ('category', 'is_featured', 'is_active', 'booking_available')
    search_fields = ('name', 'description', 'features')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['mark_featured', 'activate_services']

    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    def activate_services(self, request, queryset):
        queryset.update(is_active=True)

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'service', 'user', 'booking_date', 'time_slot', 'status', 'technician_name')
    list_filter = ('status', 'booking_date', 'service__category')
    search_fields = ('booking_id', 'user__username', 'service__name', 'phone', 'technician_name')
    actions = ['mark_confirmed', 'mark_technician_assigned', 'mark_completed']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')

    def mark_technician_assigned(self, request, queryset):
        queryset.update(status='Technician Assigned')

    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')
