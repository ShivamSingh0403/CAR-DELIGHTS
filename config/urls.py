from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from apps.core.views import health_check_view

urlpatterns = [
    # Production Health Check (Load Balancers & Monitoring)
    path('health/', health_check_view, name='health_check'),

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

# Media and Static asset routing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Standalone container fallback for media files
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Custom Error Handlers (404 & 500)
handler404 = 'apps.core.views.error_404_view'
handler500 = 'apps.core.views.error_500_view'

# Customize Admin Site Headers
admin.site.site_header = "CAR DELIGHTS — Master Admin Control"
admin.site.site_title = "Car Delights Admin"
admin.site.index_title = "Automotive Marketplace & 3D Customizer Management"
