from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'coupon_code', 'section', 'offer_type', 'discount_percentage', 'fixed_discount', 'minimum_order', 'is_active')
    list_filter = ('section', 'offer_type', 'is_active')
    search_fields = ('title', 'coupon_code', 'description')
    actions = ['activate_offers', 'deactivate_offers']

    def activate_offers(self, request, queryset):
        queryset.update(is_active=True)

    def deactivate_offers(self, request, queryset):
        queryset.update(is_active=False)
