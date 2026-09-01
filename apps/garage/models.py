from django.db import models
from django.conf import settings
from apps.vehicles.models import Vehicle

class UserVehicle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='garage_vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='owned_by_users')
    nickname = models.CharField(max_length=100, blank=True, help_text="e.g. Daily Commuter, Weekend Rocket")
    registration_number = models.CharField(max_length=20, blank=True, help_text="e.g. MH 02 CD 9999")
    purchase_year = models.PositiveIntegerField(default=2024)
    current_mileage = models.PositiveIntegerField(default=15000, help_text="Mileage in km")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_primary:
            UserVehicle.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        # If this is the user's only car, make it primary automatically
        elif not UserVehicle.objects.filter(user=self.user).exclude(id=self.id).exists():
            self.is_primary = True
        super().save(*args, **kwargs)

    @property
    def display_title(self):
        if self.nickname:
            return f"{self.nickname} ({self.vehicle.full_name})"
        return self.vehicle.full_name

    def __str__(self):
        return f"{self.user.username}'s {self.vehicle.full_name}"
