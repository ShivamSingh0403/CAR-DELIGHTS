from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    display_name = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="What should we call you? (e.g. Shivam)"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    
    # Address details
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Theme preferences
    THEME_CHOICES = [
        ('dark', 'Midnight Black'),
        ('light', 'Clean White'),
    ]
    preferred_theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')

    def get_greeting_name(self):
        if self.display_name:
            return self.display_name.strip()
        if self.first_name:
            return self.first_name.strip()
        return self.username

    def __str__(self):
        return f"{self.get_greeting_name()} ({self.username})"
