from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('tata-zone/', views.tata_owners_zone, name='tata_zone'),
    path('search/', views.global_search, name='search'),
    path('api/search/suggestions/', views.api_search_suggestions, name='api_search_suggestions'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('api/wishlist/toggle/', views.api_toggle_wishlist, name='api_toggle_wishlist'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
