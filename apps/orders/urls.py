from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_index'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('success/<str:order_id>/', views.order_success, name='order_success'),
    path('history/', views.order_list, name='order_list'),
    path('track/', views.track_order, name='track_order'),
    path('<str:order_id>/', views.order_detail, name='order_detail'),
]
