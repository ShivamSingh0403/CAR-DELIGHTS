from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_item_count', 'discount_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'session_key', 'coupon_code')
    inlines = [CartItemInline]
