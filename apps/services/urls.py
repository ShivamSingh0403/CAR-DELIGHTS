from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
    path('<slug:slug>/book/', views.book_service, name='book_service'),
]
