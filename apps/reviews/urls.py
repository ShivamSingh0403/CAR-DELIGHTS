from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('product/<int:product_id>/add/', views.add_product_review, name='add_product_review'),
]
