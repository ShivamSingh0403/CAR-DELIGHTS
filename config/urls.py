from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('vehicles/', include('apps.vehicles.urls', namespace='vehicles')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('customizer/', include('apps.customization.urls', namespace='customization')),
    path('garage/', include('apps.garage.urls', namespace='garage')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('services/', include('apps.services.urls', namespace='services')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('offers/', include('apps.offers.urls', namespace='offers')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize Admin Site Headers
admin.site.site_header = "CAR DELIGHTS — Master Admin Control"
admin.site.site_title = "Car Delights Admin"
admin.site.index_title = "Automotive Marketplace & 3D Customizer Management"
