from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to='vehicles/brands/', blank=True, null=True)
    origin_country = models.CharField(max_length=100, default='India')
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    BODY_TYPES = [
        ('Hatchback', 'Hatchback'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('XUV', 'XUV'),
        ('MUV', 'MUV'),
        ('MPV', 'MPV'),
        ('Coupe', 'Coupe'),
        ('Convertible', 'Convertible'),
        ('Luxury', 'Luxury'),
        ('Sports', 'Sports'),
        ('EV', 'Electric Vehicle (EV)'),
    ]

    FUEL_TYPES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
        ('CNG', 'CNG'),
    ]

    TRANSMISSION_TYPES = [
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
        ('DCT', 'Dual Clutch (DCT/DSG)'),
        ('CVT', 'Continuously Variable (CVT)'),
        ('iMT', 'Intelligent Manual (iMT)'),
        ('EV-Direct', 'Direct Drive (EV)'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='vehicles')
    model = models.CharField(max_length=150)
    variant = models.CharField(max_length=150, blank=True, default='Standard')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    year = models.PositiveIntegerField(default=2025)
    body_type = models.CharField(max_length=50, choices=BODY_TYPES, default='SUV')
    fuel_type = models.CharField(max_length=50, choices=FUEL_TYPES, default='Petrol')
    transmission = models.CharField(max_length=50, choices=TRANSMISSION_TYPES, default='Manual')
    engine = models.CharField(max_length=150, help_text="e.g. 1.5L Turbo GDi")
    engine_capacity = models.CharField(max_length=100, help_text="e.g. 1482 cc or 60 kWh")
    power = models.CharField(max_length=100, help_text="e.g. 160 PS @ 5500 rpm")
    torque = models.CharField(max_length=100, help_text="e.g. 253 Nm @ 1500-3500 rpm")
    seating = models.PositiveIntegerField(default=5)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in INR (₹)")
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    is_3d_available = models.BooleanField(default=False)
    model_3d_path = models.CharField(max_length=255, blank=True, null=True, help_text="Relative or media path to 3D asset (.glb/.gltf)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', 'brand__name', 'model', 'year']
        indexes = [
            models.Index(fields=['brand', 'model']),
            models.Index(fields=['body_type', 'fuel_type']),
            models.Index(fields=['price']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand.name}-{self.model}-{self.variant}-{self.year}")
            slug_cand = base_slug
            idx = 1
            while Vehicle.objects.filter(slug=slug_cand).exclude(id=self.id).exists():
                slug_cand = f"{base_slug}-{idx}"
                idx += 1
            self.slug = slug_cand
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('vehicles:vehicle_detail', kwargs={'slug': self.slug})

    @property
    def full_name(self):
        if self.variant and self.variant != 'Standard':
            return f"{self.brand.name} {self.model} {self.variant} ({self.year})"
        return f"{self.brand.name} {self.model} ({self.year})"

    @property
    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()

    @property
    def has_real_image(self):
        return self.has_real_photo

    @property
    def has_real_photo(self):
        primary = self.primary_image
        if primary and primary.image:
            name = primary.image.name.lower()
            return not (name.endswith('.svg') or 'placeholder' in name or 'outline' in name) and primary.license_status in ['REAL_PHOTO', 'VALID', 'PROPRIETARY', 'EDITORIAL']
        return False

    def get_primary_image_url(self):
        img = self.primary_image
        if img and img.image:
            try:
                name = img.image.name.lower()
                if not (name.endswith('.svg') or 'placeholder' in name or 'outline' in name):
                    return img.image.url
            except Exception:
                pass
        return '/static/images/real_photo_asset_required.svg'

    def get_formatted_price(self):
        return f"₹{self.price:,.0f}"

    def __str__(self):
        return self.full_name


class VehicleVariant(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50, blank=True)
    transmission = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    features = models.TextField(blank=True, help_text="Comma-separated or bullet list of exclusive features")

    def __str__(self):
        return f"{self.vehicle.model} - {self.name}"


def vehicle_image_upload_path(instance, filename):
    from django.utils.text import slugify
    brand_slug = slugify(instance.vehicle.brand.name) if instance.vehicle and instance.vehicle.brand else 'general'
    model_slug = slugify(instance.vehicle.model) if instance.vehicle else 'model'
    return f"vehicles/{brand_slug}/{model_slug}/{filename}"


class VehicleImage(models.Model):
    IMAGE_TYPES = [
        ('front', 'Front View'),
        ('front_three_quarter', 'Front Three-Quarter View'),
        ('side', 'Side Profile View'),
        ('rear', 'Rear View'),
        ('rear_three_quarter', 'Rear Three-Quarter View'),
        ('interior', 'Interior Cockpit'),
        ('dashboard', 'Dashboard & Infotainment'),
        ('gallery', 'Gallery View'),
    ]

    LICENSE_STATUS_CHOICES = [
        ('REAL_PHOTO', 'Real Photograph (Approved)'),
        ('VALID', 'Valid & Cleared'),
        ('PROPRIETARY', 'Proprietary OEM Asset'),
        ('EDITORIAL', 'Editorial Use Only'),
        ('LICENSE_REQUIRED', 'License Required'),
        ('MISSING', 'Missing Photograph'),
        ('DUPLICATE', 'Duplicate Assignment'),
        ('BROKEN', 'Broken File'),
        ('PENDING_REVIEW', 'Pending Review'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=vehicle_image_upload_path)
    image_type = models.CharField(max_length=50, choices=IMAGE_TYPES, default='front_three_quarter')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Real-world Image Source & Licensing tracking
    source = models.CharField(max_length=150, default='Car Delights Automotive Media Lab', help_text="e.g. OEM Studio Press, Manufacturer Media, Car Delights Studio")
    source_url = models.URLField(blank=True, null=True, help_text="Official origin or asset repository link")
    license = models.CharField(max_length=200, default='Commercial & Editorial License Cleared', help_text="Licensing terms or rights status")
    license_info = models.CharField(max_length=200, default='Commercial & Editorial License Cleared', help_text="Licensing terms or rights status")
    license_url = models.URLField(blank=True, null=True, help_text="Licensing terms documentation URL")
    license_status = models.CharField(max_length=30, choices=LICENSE_STATUS_CHOICES, default='REAL_PHOTO')

    # Media Integrity and Verification Fields
    width = models.PositiveIntegerField(null=True, blank=True, help_text="Image pixel width")
    height = models.PositiveIntegerField(null=True, blank=True, help_text="Image pixel height")
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    image_hash = models.CharField(max_length=64, blank=True, db_index=True, help_text="MD5 perceptual image hash")
    verified = models.BooleanField(default=True, db_index=True, help_text="Verified real photograph")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-is_primary', 'sort_order', 'id']
        indexes = [
            models.Index(fields=['vehicle', 'is_primary']),
            models.Index(fields=['image_hash']),
            models.Index(fields=['verified']),
            models.Index(fields=['license_status']),
        ]

    def get_image_url(self):
        if self.image:
            try:
                name = self.image.name.lower()
                if not (name.endswith('.svg') or 'placeholder' in name or 'outline' in name):
                    return self.image.url
            except Exception:
                pass
        return '/static/images/real_photo_asset_required.svg'

    def save(self, *args, **kwargs):
        if self.is_primary:
            VehicleImage.objects.filter(vehicle=self.vehicle, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        if not self.alt_text and self.vehicle:
            self.alt_text = f"{self.vehicle.full_name} - {self.get_image_type_display()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.model} - {self.get_image_type_display()} ({self.license_status})"


class VehicleSpecification(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='specifications')
    category = models.CharField(max_length=100, default='General', help_text="e.g. Dimensions, Engine, Brakes, Safety")
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    class Meta:
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.vehicle.model} - {self.key}: {self.value}"


class VehicleCompatibility(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='compatibility_records')
    category_slug = models.CharField(max_length=100, help_text="Product category slug compatible with this vehicle")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle.full_name} -> {self.category_slug}"
