from django.urls import path
from . import views

app_name = 'customization'

urlpatterns = [
    path('', views.customizer_view, name='customizer'),
    path('paint-studio/', views.paint_studio_view, name='paint_studio'),
    path('paint/', views.paint_studio_view, name='paint_studio_alt'),
    path('api/config/<int:vehicle_id>/', views.api_customizer_config, name='api_customizer_config'),
    path('api/calculate-price/', views.api_calculate_price, name='api_calculate_price'),
    path('api/save-build/', views.api_save_build, name='api_save_build'),
]
