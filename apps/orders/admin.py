from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_type', 'item_name', 'item_sku', 'price', 'quantity', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'full_name', 'user', 'total_amount', 'payment_method', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('order_id', 'full_name', 'email', 'phone', 'tracking_number')
    inlines = [OrderItemInline]
    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered', 'mark_paid']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')
    mark_confirmed.short_description = "Mark selected as Confirmed"

    def mark_shipped(self, request, queryset):
        queryset.update(status='Shipped')
    mark_shipped.short_description = "Mark selected as Shipped"

    def mark_delivered(self, request, queryset):
        queryset.update(status='Delivered')
    mark_delivered.short_description = "Mark selected as Delivered"

    def mark_paid(self, request, queryset):
        queryset.update(payment_status='Paid')
    mark_paid.short_description = "Mark payment as Paid"
