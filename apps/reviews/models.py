from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.services.models import Service

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, f"{i} Stars") for i in range(1, 6)])
    title = models.CharField(max_length=150)
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/uploads/', blank=True, null=True)
    
    is_verified_purchase = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.product.name if self.product else (self.service.name if self.service else 'Item')
        return f"{self.user.username}'s {self.rating}★ Review for {target}"
