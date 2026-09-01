from django.urls import path
from . import views

app_name = 'garage'

urlpatterns = [
    path('', views.my_garage_view, name='my_garage'),
    path('dashboard/', views.my_garage_view, name='garage_dashboard'),
    path('add/', views.add_vehicle_to_garage, name='add_vehicle'),
    path('set-primary/<int:pk>/', views.set_primary_vehicle, name='set_primary'),
    path('delete/<int:pk>/', views.delete_garage_vehicle, name='delete_vehicle'),
    path('saved-builds/', views.saved_builds_view, name='saved_builds'),
    path('builds/', views.saved_builds_view, name='builds'),
    path('saved-builds/duplicate/<int:pk>/', views.duplicate_build, name='duplicate_build'),
    path('saved-builds/delete/<int:pk>/', views.delete_build, name='delete_build'),
    path('saved-builds/add-to-cart/<int:pk>/', views.add_build_to_cart, name='add_build_to_cart'),
]
