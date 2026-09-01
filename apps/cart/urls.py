from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('api/add/', views.add_to_cart_ajax, name='api_add_to_cart'),
    path('api/update/', views.update_quantity_ajax, name='api_update_quantity'),
    path('api/remove/', views.remove_from_cart_ajax, name='api_remove_item'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('clear/', views.clear_cart, name='clear_cart'),
]
