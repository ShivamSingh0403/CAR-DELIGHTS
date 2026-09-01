from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.customization.models import CustomBuild

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_subtotal(self):
        items = list(self.items.all())
        if not items:
            return Decimal('0.00')
        return sum((Decimal(str(item.get_total_price())) for item in items), Decimal('0.00'))

    def get_total(self):
        subtotal = self.get_subtotal()
        discount = Decimal(str(self.discount_amount or '0.00'))
        total = max(Decimal('0.00'), subtotal - discount)
        return total

    def get_total_mrp(self):
        total_mrp = Decimal('0.00')
        for item in self.items.all():
            if item.product and item.product.mrp:
                total_mrp += Decimal(str(item.product.mrp)) * item.quantity
            else:
                total_mrp += Decimal(str(item.price)) * item.quantity
        return total_mrp

    def get_savings(self):
        savings = self.get_total_mrp() - self.get_total()
        return max(Decimal('0.00'), savings)

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def get_formatted_subtotal(self):
        return f"₹{self.get_subtotal():,.0f}"

    def get_formatted_total(self):
        return f"₹{self.get_total():,.0f}"

    def get_formatted_savings(self):
        return f"₹{self.get_savings():,.0f}"

    def __str__(self):
        owner = self.user.username if self.user else f"Session: {self.session_key}"
        return f"Cart ({owner}) - {self.get_item_count()} items"


class CartItem(models.Model):
    ITEM_TYPES = [
        ('product', 'Product / Spare Part'),
        ('custom_build', '3D Custom Vehicle Build'),
        ('service', 'Automotive Service / Care'),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES, default='product')
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    custom_build = models.ForeignKey(CustomBuild, on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items')
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.price * self.quantity

    def get_name(self):
        if self.item_type == 'product' and self.product:
            return self.product.name
        elif self.item_type == 'custom_build' and self.custom_build:
            return f"3D Build: {self.custom_build.name} ({self.custom_build.vehicle.full_name})"
        elif self.item_type == 'service' and self.service:
            return f"Service: {self.service.name}"
        return "Car Delights Item"

    def get_image_url(self):
        if self.item_type == 'product' and self.product and self.product.primary_image:
            return self.product.primary_image.image.url
        elif self.item_type == 'custom_build' and self.custom_build and self.custom_build.vehicle.primary_image:
            return self.custom_build.vehicle.primary_image.image.url
        elif self.item_type == 'service' and self.service and self.service.image:
            return self.service.image.url
        return '/static/images/placeholder_part.svg'

    def get_formatted_price(self):
        return f"₹{self.price:,.0f}"

    def get_formatted_total(self):
        return f"₹{self.get_total_price():,.0f}"

    def __str__(self):
        return f"{self.get_name()} (Qty: {self.quantity})"
