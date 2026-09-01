from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json

from apps.vehicles.models import Vehicle, Brand
from apps.products.models import Product, Category, ProductBrand
from apps.services.models import Service
from apps.offers.models import Offer
from apps.customization.models import PaintOption
from .models import Notification, Wishlist

def home(request):
    featured_vehicles = Vehicle.objects.filter(featured=True).select_related('brand').prefetch_related('images')[:8]
    if not featured_vehicles.exists():
        featured_vehicles = Vehicle.objects.select_related('brand').prefetch_related('images')[:8]

    popular_vehicles = Vehicle.objects.filter(is_3d_available=True).select_related('brand').prefetch_related('images')[:6]
    if not popular_vehicles.exists():
        popular_vehicles = Vehicle.objects.select_related('brand').prefetch_related('images')[:6]

    trending_products = Product.objects.filter(featured=True, is_active=True).select_related('brand', 'category').prefetch_related('images')[:8]
    if not trending_products.exists():
        trending_products = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images')[:8]

    wheels = Product.objects.filter(
        Q(category__slug='wheels') | Q(category__parent__slug='wheels') | Q(part_type='wheels'),
        is_active=True
    ).select_related('brand').prefetch_related('images')[:6]

    tyres = Product.objects.filter(
        Q(category__slug='tyres') | Q(category__parent__slug='tyres') | Q(part_type='tyres'),
        is_active=True
    ).select_related('brand').prefetch_related('images')[:6]

    accessories = Product.objects.filter(
        Q(category__slug='accessories') | Q(category__parent__slug='accessories'),
        is_active=True
    ).select_related('brand').prefetch_related('images')[:6]

    services = Service.objects.filter(is_featured=True, is_active=True).select_related('category')[:6]
    if not services.exists():
        services = Service.objects.filter(is_active=True).select_related('category')[:6]

    paints = PaintOption.objects.filter(is_featured=True)[:8]
    if not paints.exists():
        paints = PaintOption.objects.all()[:8]

    offers = Offer.objects.filter(is_active=True)[:4]

    # Tata Zone preview
    tata_cars = Vehicle.objects.filter(brand__name__iexact='Tata').prefetch_related('images')[:4]

    context = {
        'featured_vehicles': featured_vehicles,
        'popular_vehicles': popular_vehicles,
        'trending_products': trending_products,
        'wheels': wheels,
        'tyres': tyres,
        'accessories': accessories,
        'services': services,
        'paints': paints,
        'offers': offers,
        'tata_cars': tata_cars,
    }
    return render(request, 'core/home.html', context)


def tata_owners_zone(request):
    tata_brand = Brand.objects.filter(name__iexact='Tata').first()
    tata_vehicles = Vehicle.objects.filter(brand__name__iexact='Tata').prefetch_related('images')
    
    tata_parts = Product.objects.filter(
        Q(compatibilities__vehicle__brand__name__iexact='Tata') | Q(is_universal=True),
        is_active=True
    ).distinct().select_related('brand', 'category').prefetch_related('images')[:12]

    tata_offers = Offer.objects.filter(
        Q(section='tata') | Q(coupon_code__icontains='TATA'),
        is_active=True
    )

    tata_services = Service.objects.filter(is_active=True)[:4]

    context = {
        'brand': tata_brand,
        'vehicles': tata_vehicles,
        'products': tata_parts,
        'offers': tata_offers,
        'services': tata_services,
    }
    return render(request, 'core/tata_zone.html', context)


def global_search(request):
    q = request.GET.get('q', '').strip()
    vehicles = []
    products = []
    services = []
    brands = []

    if q:
        vehicles = Vehicle.objects.filter(
            Q(model__icontains=q) | Q(brand__name__icontains=q) | Q(variant__icontains=q)
        ).select_related('brand').prefetch_related('images')[:12]

        products = Product.objects.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__name__icontains=q) | Q(category__name__icontains=q)
        ).select_related('brand', 'category').prefetch_related('images')[:16]

        services = Service.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q)
        ).select_related('category')[:6]

        brands = Brand.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )[:6]

    total_results = len(vehicles) + len(products) + len(services) + len(brands)

    context = {
        'query': q,
        'vehicles': vehicles,
        'products': products,
        'services': services,
        'brands': brands,
        'total_results': total_results,
    }
    return render(request, 'core/search_results.html', context)


def api_search_suggestions(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'status': 'success', 'results': []})

    results = []
    
    # Search Vehicles
    for v in Vehicle.objects.filter(Q(model__icontains=q) | Q(brand__name__icontains=q))[:4]:
        results.append({
            'type': 'Vehicle',
            'title': v.full_name,
            'subtitle': f"{v.body_type} • {v.get_formatted_price()}",
            'url': v.get_absolute_url(),
            'icon': 'bi-car-front-fill'
        })

    # Search Products
    for p in Product.objects.filter(Q(name__icontains=q) | Q(brand__name__icontains=q))[:5]:
        results.append({
            'type': 'Product',
            'title': p.name,
            'subtitle': f"{p.category.name} • {p.get_formatted_price()}",
            'url': p.get_absolute_url(),
            'icon': 'bi-box-seam'
        })

    # Search Services
    for s in Service.objects.filter(Q(name__icontains=q))[:3]:
        results.append({
            'type': 'Service',
            'title': s.name,
            'subtitle': f"{s.category.name} • {s.get_formatted_price()}",
            'url': f"/services/{s.slug}/",
            'icon': 'bi-wrench'
        })

    return JsonResponse({'status': 'success', 'results': results})


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related(
        'product__brand', 'product__category', 'vehicle__brand'
    ).prefetch_related('product__images', 'vehicle__images')
    return render(request, 'core/wishlist.html', {'wishlist_items': wishlist_items})


@require_POST
@login_required
def api_toggle_wishlist(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_id = data.get('product_id')
        vehicle_id = data.get('vehicle_id')

        product = Product.objects.filter(id=product_id).first() if product_id else None
        vehicle = Vehicle.objects.filter(id=vehicle_id).first() if vehicle_id else None

        if product:
            w_item = Wishlist.objects.filter(user=request.user, product=product).first()
            if w_item:
                w_item.delete()
                added = False
                msg = f"{product.name} removed from your wishlist."
            else:
                Wishlist.objects.create(user=request.user, product=product)
                added = True
                msg = f"{product.name} saved to your wishlist!"
        elif vehicle:
            w_item = Wishlist.objects.filter(user=request.user, vehicle=vehicle).first()
            if w_item:
                w_item.delete()
                added = False
                msg = f"{vehicle.full_name} removed from your wishlist."
            else:
                Wishlist.objects.create(user=request.user, vehicle=vehicle)
                added = True
                msg = f"{vehicle.full_name} saved to your wishlist!"
        else:
            return JsonResponse({'status': 'error', 'message': 'No valid item specified'}, status=400)

        total_count = Wishlist.objects.filter(user=request.user).count()

        return JsonResponse({
            'status': 'success',
            'added': added,
            'message': msg,
            'wishlist_count': total_count
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark all as read
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifs})


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        messages.success(request, "Thank you for reaching out to Car Delights! Our automotive concierge team will contact you shortly.")
        return redirect('core:contact')
    return render(request, 'core/contact.html')
