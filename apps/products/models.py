from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from apps.vehicles.models import Vehicle

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    icon = models.CharField(max_length=50, default='bi-gear-wide-connected', help_text="Bootstrap Icon class name")
    image = models.ImageField(upload_to='products/categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name


class ProductBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to='products/brands/', blank=True, null=True)
    origin_country = models.CharField(max_length=100, default='India')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    brand = models.ForeignKey(ProductBrand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    sku = models.CharField(max_length=60, unique=True)
    
    # Pricing in INR ₹
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum Retail Price (₹)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Discounted Selling Price (₹)")
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Calculated automatically or manual override")
    
    stock = models.PositiveIntegerField(default=25)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    review_count = models.PositiveIntegerField(default=12)
    warranty = models.CharField(max_length=100, default='1 Year Manufacturer Warranty')
    
    is_universal = models.BooleanField(default=False, help_text="Fits all standard vehicles")
    is_3d_part = models.BooleanField(default=False, help_text="Can be configured in 3D Customizer")
    part_type = models.CharField(
        max_length=50, 
        blank=True, 
        choices=[
            ('paint', 'Paint Option'),
            ('wheels', 'Wheel / Rim'),
            ('tyres', 'Tyre'),
            ('bumper_front', 'Front Bumper'),
            ('bumper_rear', 'Rear Bumper'),
            ('spoiler', 'Rear Spoiler'),
            ('side_skirt', 'Side Skirts'),
            ('diffuser', 'Rear Diffuser'),
            ('grille', 'Front Grille'),
            ('headlight', 'Headlight Set'),
            ('taillight', 'Tail Light Set'),
            ('exhaust', 'Performance Exhaust'),
            ('interior', 'Interior Trim'),
        ],
        help_text="3D customizer part slot if applicable"
    )
    
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-rating', 'name']
        indexes = [
            models.Index(fields=['category', 'brand']),
            models.Index(fields=['price', 'rating']),
            models.Index(fields=['sku']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug_cand = base_slug
            idx = 1
            while Product.objects.filter(slug=slug_cand).exclude(id=self.id).exists():
                slug_cand = f"{base_slug}-{idx}"
                idx += 1
            self.slug = slug_cand
            
        # Recalculate discount percentage automatically
        if self.mrp and self.price and self.mrp > 0:
            if self.mrp > self.price:
                diff = self.mrp - self.price
                self.discount_percentage = int(round((diff / self.mrp) * 100))
            else:
                self.discount_percentage = 0
                
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        primary = self.images.filter(image_type='primary').first()
        if primary:
            return primary
        first = self.images.first()
        return first

    def get_primary_image_url(self):
        img = self.primary_image
        if img and img.image:
            try:
                return img.image.url
            except Exception:
                pass
        return '/static/images/placeholder_part.svg'

    @property
    def installed_image(self):
        return self.images.filter(image_type='installed').first()

    @property
    def gallery_images(self):
        return self.images.exclude(image_type='primary').order_by('sort_order', 'id')

    def get_formatted_price(self):
        return f"₹{self.price:,.0f}"

    def get_formatted_mrp(self):
        return f"₹{self.mrp:,.0f}"

    def get_savings(self):
        if self.mrp > self.price:
            return f"₹{(self.mrp - self.price):,.0f}"
        return "₹0"

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductImage(models.Model):
    IMAGE_TYPES = [
        ('primary', 'Primary Display Image'),
        ('front', 'Front Perspective View'),
        ('side', 'Side Profile View'),
        ('detail', 'Detailed Close-up & Texture'),
        ('packaging', 'Genuine OEM Packaging'),
        ('installed', 'Installed on Vehicle Example'),
        ('schematic', 'Technical Blueprint & Schematics'),
        ('gallery', 'General Gallery Image'),
    ]

    LICENSE_STATUS_CHOICES = [
        ('VALID', 'Valid & Cleared'),
        ('LICENSE_REQUIRED', 'License Required'),
        ('PROPRIETARY', 'Proprietary OEM Asset'),
        ('EDITORIAL', 'Editorial Use Only'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    image_type = models.CharField(max_length=30, choices=IMAGE_TYPES, default='gallery')
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    # Real-world Image Source & Licensing tracking
    source = models.CharField(max_length=150, default='Car Delights Automotive Engineering Media', help_text="e.g. Manufacturer Direct, Brembo OEM, Michelin Media Studio")
    source_url = models.URLField(blank=True, null=True, help_text="Official asset repository link")
    license_info = models.CharField(max_length=200, default='Authorized Distributor Cleared License', help_text="Licensing terms or rights status")
    license_status = models.CharField(max_length=30, choices=LICENSE_STATUS_CHOICES, default='VALID')
    
    # Installed vehicle context
    installed_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='installed_product_previews', help_text="Vehicle featured in installed preview")

    class Meta:
        ordering = ['sort_order', 'id']

    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return '/static/images/placeholder_part.svg'

    def save(self, *args, **kwargs):
        if not self.alt_text and self.product:
            self.alt_text = f"{self.product.name} - {self.get_image_type_display()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.get_image_type_display()} ({self.license_status})"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.name} - {self.key}: {self.value}"


class ProductCompatibility(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='compatibilities')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='compatible_parts')
    variant_notes = models.CharField(max_length=200, blank=True, help_text="e.g. All variants or Petrol DCT only")
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Product Compatibilities'
        unique_together = ('product', 'vehicle')

    def __str__(self):
        return f"{self.product.name} -> {self.vehicle.full_name}"
