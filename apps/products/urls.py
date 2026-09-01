from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('wheels/', views.wheels_list, name='wheels_list'),
    path('tyres/', views.tyres_list, name='tyres_list'),
    path('api/list/', views.api_product_list, name='api_product_list'),
    path('api/compatibility/', views.api_check_compatibility, name='api_check_compatibility'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
