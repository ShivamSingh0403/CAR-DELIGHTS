from django.urls import path
from . import views

app_name = 'offers'

urlpatterns = [
    path('', views.offer_list, name='offer_list'),
    path('api/active/', views.api_active_offers, name='api_active_offers'),
]
