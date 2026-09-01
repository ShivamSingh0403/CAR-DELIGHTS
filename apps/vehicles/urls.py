from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list, name='vehicle_list'),
    path('compare/', views.vehicle_compare, name='vehicle_compare'),
    path('compare/direct/', views.vehicle_compare, name='compare'),
    path('asset-status/', views.asset_status, name='asset_status'),
    path('api/list/', views.api_vehicle_list, name='api_vehicle_list'),
    path('api/<int:pk>/', views.api_vehicle_detail, name='api_vehicle_detail'),
    path('<slug:slug>/', views.vehicle_detail, name='vehicle_detail'),
]
