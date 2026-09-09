from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehicle
from apps.products.models import Product

class PaintOption(models.Model):
    FINISH_TYPES = [
        ('Solid', 'Solid Finish'),
        ('Metallic', 'Metallic High-Gloss'),
        ('Pearl', 'Deep Pearl Coat'),
        ('Matte', 'Matte Stealth Finish'),
        ('Satin', 'Satin Silk Finish'),
        ('Gloss', 'Ultra Gloss'),
        ('Chrome', 'Mirror Chrome / Liquid Metal'),
        ('Two-tone', 'Two-Tone Dual Coat'),
    ]

    name = models.CharField(max_length=100, unique=True)
    finish_type = models.CharField(max_length=50, choices=FINISH_TYPES, default='Metallic')
    hex_color = models.CharField(max_length=7, help_text="e.g. #0B192C")
    secondary_hex_color = models.CharField(max_length=7, blank=True, null=True, help_text="For two-tone paints e.g. #111111")
    
    # 3D PBR Shader properties
    roughness = models.FloatField(default=0.2, help_text="0.0 (smooth) to 1.0 (rough)")
    metalness = models.FloatField(default=0.8, help_text="0.0 (dielectric) to 1.0 (metal)")
    clearcoat = models.FloatField(default=1.0, help_text="Clearcoat intensity")
    clearcoat_roughness = models.FloatField(default=0.05)
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=25000.00, help_text="Custom paint job price (₹)")
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='customization/paints/', blank=True, null=True)

    class Meta:
        ordering = ['finish_type', 'name']

    def get_formatted_price(self):
        from apps.core.utils import format_inr
        return format_inr(self.price)

    def __str__(self):
        return f"{self.name} ({self.finish_type}) - {self.get_formatted_price()}"


class CustomBuild(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_builds', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='custom_builds')
    name = models.CharField(max_length=150, default='Custom Dream Build')
    
    paint = models.ForeignKey(PaintOption, on_delete=models.SET_NULL, null=True, blank=True)
    wheel = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_wheel')
    tyre = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_tyre')
    bumper_front = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_bumper_front')
    bumper_rear = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_bumper_rear')
    spoiler = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_spoiler')
    side_skirt = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_side_skirt')
    diffuser = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_diffuser')
    grille = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_grille')
    headlights = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_headlights')
    taillights = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_taillights')
    exhaust = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_exhaust')
    interior = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='builds_interior')
    
    installation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    snapshot_image = models.TextField(blank=True, help_text="Base64 or image URL thumbnail of build")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_price(self):
        total = self.vehicle.price if self.vehicle else 0
        if self.paint:
            total += self.paint.price
        for part in [
            self.wheel, self.tyre, self.bumper_front, self.bumper_rear,
            self.spoiler, self.side_skirt, self.diffuser, self.grille,
            self.headlights, self.taillights, self.exhaust, self.interior
        ]:
            if part:
                total += part.price
        total += self.installation_fee
        self.total_price = total
        return total

    def save(self, *args, **kwargs):
        self.calculate_total_price()
        super().save(*args, **kwargs)

    def get_formatted_total(self):
        from apps.core.utils import format_inr
        return format_inr(self.total_price)

    def __str__(self):
        return f"{self.name} - {self.vehicle.full_name} ({self.get_formatted_total()})"
