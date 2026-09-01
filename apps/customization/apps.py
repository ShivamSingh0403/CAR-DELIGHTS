from django.apps import AppConfig

class CustomizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customization'
    verbose_name = '3D Customization Studio & Paint'
