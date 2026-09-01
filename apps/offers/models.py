from django.db import models
from django.utils import timezone

class Offer(models.Model):
    SECTION_CHOICES = [
        ('daily', 'Daily Deals'),
        ('weekend', 'Weekend Specials'),
        ('festival', 'Festival Bonanza'),
        ('tata', 'Tata Owners Special'),
        ('tyres', 'Tyre Deals'),
        ('services', 'Service & Care Offers'),
        ('accessories', 'Accessories Discounts'),
    ]

    OFFER_TYPE_CHOICES = [
        ('percentage', 'Percentage (%) Off'),
        ('fixed', 'Flat Amount (₹) Off'),
    ]

    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255, blank=True)
    coupon_code = models.CharField(max_length=50, unique=True, help_text="e.g. TATA20, DELIGHT500")
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='percentage')
    
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Percentage discount e.g. 15 for 15%")
    fixed_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fixed amount discount in ₹")
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum cap in ₹")
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Minimum order value in ₹")
    
    section = models.CharField(max_length=30, choices=SECTION_CHOICES, default='daily')
    badge_text = models.CharField(max_length=50, default='Special Offer')
    banner_image = models.ImageField(upload_to='offers/banners/', blank=True, null=True)
    description = models.TextField(blank=True)
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['section', '-created_at']

    def is_valid_now(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    def get_discount_label(self):
        if self.offer_type == 'percentage' or self.discount_percentage > 0:
            return f"{self.discount_percentage}% OFF"
        return f"FLAT ₹{self.fixed_discount:,.0f} OFF"

    def __str__(self):
        return f"{self.title} [{self.coupon_code}] - {self.get_discount_label()}"
