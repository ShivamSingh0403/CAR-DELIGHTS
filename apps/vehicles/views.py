from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Vehicle, Brand, VehicleImage, VehicleSpecification

def vehicle_list(request):
    queryset = Vehicle.objects.select_related('brand').prefetch_related('images').all()
    
    # Search Query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(model__icontains=q) |
            Q(brand__name__icontains=q) |
            Q(variant__icontains=q) |
            Q(description__icontains=q)
        )

    # Filters
    brand_slug = request.GET.get('brand')
    if brand_slug:
        queryset = queryset.filter(brand__slug=brand_slug)

    body_type = request.GET.get('body_type')
    if body_type:
        queryset = queryset.filter(body_type=body_type)

    fuel_type = request.GET.get('fuel_type')
    if fuel_type:
        queryset = queryset.filter(fuel_type=fuel_type)

    transmission = request.GET.get('transmission')
    if transmission:
        queryset = queryset.filter(transmission=transmission)

    is_3d = request.GET.get('3d')
    if is_3d == '1' or is_3d == 'true':
        queryset = queryset.filter(is_3d_available=True)

    min_price = request.GET.get('min_price')
    if min_price and min_price.isdigit():
        queryset = queryset.filter(price__gte=int(min_price))

    max_price = request.GET.get('max_price')
    if max_price and max_price.isdigit():
        queryset = queryset.filter(price__lte=int(max_price))

    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        queryset = queryset.order_by('price')
    elif sort == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort == 'name_asc':
        queryset = queryset.order_by('brand__name', 'model')
    elif sort == 'newest':
        queryset = queryset.order_by('-year', '-created_at')
    else:
        queryset = queryset.order_by('-featured', 'brand__name', 'model')

    # Pagination
    paginator = Paginator(queryset, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brands = Brand.objects.all()
    body_types = [bt[0] for bt in Vehicle.BODY_TYPES]
    fuel_types = [ft[0] for ft in Vehicle.FUEL_TYPES]
    transmissions = [tt[0] for tt in Vehicle.TRANSMISSION_TYPES]

    photographed_count = Vehicle.objects.filter(
        images__is_primary=True,
        images__license_status__in=['REAL_PHOTO', 'VALID', 'PROPRIETARY', 'EDITORIAL']
    ).distinct().count()

    context = {
        'vehicles': page_obj,
        'brands': brands,
        'body_types': body_types,
        'fuel_types': fuel_types,
        'transmissions': transmissions,
        'total_count': queryset.count(),
        'total_vehicles_count': Vehicle.objects.count(),
        'photographed_count': photographed_count,
        'current_filters': request.GET,
    }
    return render(request, 'vehicles/vehicle_list.html', context)


def vehicle_detail(request, slug):
    vehicle = get_object_or_404(
        Vehicle.objects.select_related('brand').prefetch_related('images', 'variants', 'specifications'),
        slug=slug
    )
    similar_vehicles = Vehicle.objects.filter(
        body_type=vehicle.body_type
    ).exclude(id=vehicle.id).select_related('brand').prefetch_related('images')[:4]

    # Group specifications by category
    specs_by_category = {}
    for spec in vehicle.specifications.all():
        if spec.category not in specs_by_category:
            specs_by_category[spec.category] = []
        specs_by_category[spec.category].append(spec)

    context = {
        'vehicle': vehicle,
        'similar_vehicles': similar_vehicles,
        'specs_by_category': specs_by_category,
    }
    return render(request, 'vehicles/vehicle_detail.html', context)


def vehicle_compare(request):
    vehicle_ids = request.GET.getlist('id')
    vehicles = Vehicle.objects.filter(id__in=vehicle_ids[:4]).select_related('brand').prefetch_related('specifications', 'images')
    all_vehicles = Vehicle.objects.select_related('brand').order_by('brand__name', 'model')
    
    return render(request, 'vehicles/compare.html', {
        'selected_vehicles': vehicles,
        'all_vehicles': all_vehicles,
    })


# API Endpoints
def api_vehicle_list(request):
    brand = request.GET.get('brand')
    is_3d = request.GET.get('3d')
    
    qs = Vehicle.objects.select_related('brand').all()
    if brand:
        qs = qs.filter(brand__name__iexact=brand)
    if is_3d == '1' or is_3d == 'true':
        qs = qs.filter(is_3d_available=True)
        
    data = []
    for v in qs:
        img_url = v.primary_image.image.url if v.primary_image else '/static/images/placeholder_car.svg'
        data.append({
            'id': v.id,
            'name': v.full_name,
            'brand': v.brand.name,
            'model': v.model,
            'variant': v.variant,
            'year': v.year,
            'body_type': v.body_type,
            'fuel_type': v.fuel_type,
            'transmission': v.transmission,
            'price': float(v.price),
            'formatted_price': v.get_formatted_price(),
            'is_3d_available': v.is_3d_available,
            'model_3d_path': v.model_3d_path or '',
            'image': img_url,
            'slug': v.slug,
        })
    return JsonResponse({'status': 'success', 'vehicles': data})


def api_vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle.objects.select_related('brand'), pk=pk)
    img_url = vehicle.get_primary_image_url()
    
    data = {
        'id': vehicle.id,
        'name': vehicle.full_name,
        'brand': vehicle.brand.name,
        'model': vehicle.model,
        'variant': vehicle.variant,
        'year': vehicle.year,
        'body_type': vehicle.body_type,
        'fuel_type': vehicle.fuel_type,
        'transmission': vehicle.transmission,
        'engine': vehicle.engine,
        'power': vehicle.power,
        'torque': vehicle.torque,
        'price': float(vehicle.price),
        'formatted_price': vehicle.get_formatted_price(),
        'is_3d_available': vehicle.is_3d_available,
        'model_3d_path': vehicle.model_3d_path or '',
        'image': img_url,
        'slug': vehicle.slug,
    }
    return JsonResponse({'status': 'success', 'vehicle': data})


def asset_status(request):
    from apps.products.models import Product
    total_vehicles = Vehicle.objects.count()
    real_photos = Vehicle.objects.filter(images__is_primary=True, images__verified=True).distinct().count()
    total_products = Product.objects.count()
    product_photos = Product.objects.filter(images__isnull=False).distinct().count()
    
    context = {
        'total_vehicles': total_vehicles,
        'real_photos': real_photos,
        'missing_vehicles': total_vehicles - real_photos,
        'total_products': total_products,
        'product_photos': product_photos,
        'verified_count': real_photos,
    }
    return render(request, 'vehicles/asset_status.html', context)
