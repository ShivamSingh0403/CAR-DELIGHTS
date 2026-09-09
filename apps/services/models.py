import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from apps.vehicles.models import Vehicle

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi-wrench-adjustable')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in ₹ INR")
    duration = models.CharField(max_length=50, default='60 mins', help_text="e.g. 45 mins, 2 hours, 1 day")
    features = models.TextField(help_text="Newline-separated list of included features")
    image = models.ImageField(upload_to='services/gallery/', blank=True, null=True)
    
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    booking_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', '-is_featured', 'price']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]

    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return f"{settings.STATIC_URL}images/default_service.svg"

    def get_formatted_price(self):
        from apps.core.utils import format_inr
        return format_inr(self.price)

    def __str__(self):
        return f"{self.name} - {self.get_formatted_price()}"


class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Booking Received'),
        ('Confirmed', 'Slot Confirmed'),
        ('Technician Assigned', 'Technician Assigned'),
        ('In Progress', 'Service In Progress'),
        ('Completed', 'Service Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    booking_id = models.CharField(max_length=40, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle_custom_name = models.CharField(max_length=150, blank=True, help_text="e.g. Hyundai Creta 2025")
    
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=50, help_text="e.g. 10:00 AM - 12:00 PM")
    
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default='Mumbai')
    pincode = models.CharField(max_length=10, default='400001')
    phone = models.CharField(max_length=20)
    
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Confirmed')
    technician_name = models.CharField(max_length=100, default='Rahul Sharma (Lead Specialist)')
    technician_phone = models.CharField(max_length=20, default='+91 98765 12345')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_id:
            today_str = timezone.now().strftime('%Y%m%d')
            rand_suffix = uuid.uuid4().hex[:6].upper()
            self.booking_id = f"BK-{today_str}-{rand_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.booking_id} - {self.service.name} ({self.status})"
