import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.products.models import Product
from apps.customization.models import CustomBuild

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Confirmation'),
        ('Confirmed', 'Order Confirmed'),
        ('Processing', 'Processing / In Workshop'),
        ('Packed', 'Packed & Quality Checked'),
        ('Shipped', 'Shipped with Express Courier'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Payment Pending'),
        ('Paid', 'Payment Successful (Verified)'),
        ('Failed', 'Payment Failed'),
        ('Refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'Instant UPI / QR / NetBanking (Demo Gateway)'),
        ('Card', 'Credit / Debit Card (Visa, MasterCard, RuPay)'),
        ('COD', 'Cash on Delivery (Verified Delivery)'),
    ]

    order_id = models.CharField(max_length=40, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Customer Details at checkout
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Shipping Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Financials (₹ INR)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Paid')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Confirmed')
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    courier_partner = models.CharField(max_length=100, default='Car Delights Logistics Express')
    customer_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['user', 'status']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_id:
            today_str = timezone.now().strftime('%Y%m%d')
            rand_suffix = uuid.uuid4().hex[:6].upper()
            self.order_id = f"CD-{today_str}-{rand_suffix}"
        super().save(*args, **kwargs)

    def get_formatted_total(self):
        from apps.core.utils import format_inr
        return format_inr(self.total_amount)

    def get_formatted_subtotal(self):
        from apps.core.utils import format_inr
        return format_inr(self.subtotal)

    def get_formatted_discount(self):
        from apps.core.utils import format_inr
        return format_inr(self.discount_amount)

    def __str__(self):
        return f"Order #{self.order_id} - {self.full_name} ({self.get_formatted_total()})"


class OrderItem(models.Model):
    ITEM_TYPES = [
        ('product', 'Product / Spare Part'),
        ('custom_build', '3D Custom Vehicle Build'),
        ('service', 'Automotive Service / Care'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES, default='product')
    
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    custom_build = models.ForeignKey(CustomBuild, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    
    item_name = models.CharField(max_length=255)
    item_sku = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def get_formatted_price(self):
        from apps.core.utils import format_inr
        return format_inr(self.price)

    def get_formatted_total(self):
        from apps.core.utils import format_inr
        return format_inr(self.total_price)

    def __str__(self):
        return f"{self.item_name} x {self.quantity} ({self.order.order_id})"
