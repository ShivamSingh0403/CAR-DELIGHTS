from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Category, ProductBrand, ProductImage, ProductSpecification, ProductCompatibility
from apps.vehicles.models import Vehicle

def product_list(request):
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images').all()
    
    # Search Query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(sku__icontains=q) |
            Q(brand__name__icontains=q) |
            Q(category__name__icontains=q)
        )

    # Category filter (handles parent and subcategories)
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            # Include child categories if any
            sub_ids = list(current_category.subcategories.values_list('id', flat=True))
            cat_ids = [current_category.id] + sub_ids
            queryset = queryset.filter(category_id__in=cat_ids)

    # Brand filter
    brand_slug = request.GET.get('brand')
    if brand_slug:
        queryset = queryset.filter(brand__slug=brand_slug)

    # Vehicle compatibility filter
    vehicle_id = request.GET.get('vehicle')
    selected_vehicle = None
    if vehicle_id and vehicle_id.isdigit():
        selected_vehicle = Vehicle.objects.filter(id=int(vehicle_id)).first()
        if selected_vehicle:
            queryset = queryset.filter(
                Q(is_universal=True) |
                Q(compatibilities__vehicle=selected_vehicle)
            ).distinct()

    # Part type filter (for 3D studio parts)
    part_type = request.GET.get('part_type')
    if part_type:
        queryset = queryset.filter(part_type=part_type)

    # Price range filter
    min_price = request.GET.get('min_price')
    if min_price and min_price.isdigit():
        queryset = queryset.filter(price__gte=int(min_price))

    max_price = request.GET.get('max_price')
    if max_price and max_price.isdigit():
        queryset = queryset.filter(price__lte=int(max_price))

    # Rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        queryset = queryset.filter(rating__gte=float(min_rating))

    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        queryset = queryset.order_by('price')
    elif sort == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort == 'discount':
        queryset = queryset.order_by('-discount_percentage')
    elif sort == 'rating':
        queryset = queryset.order_by('-rating')
    elif sort == 'newest':
        queryset = queryset.order_by('-created_at')
    else:
        queryset = queryset.order_by('-featured', '-rating', 'name')

    # Pagination
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    brands = ProductBrand.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'current_category': current_category,
        'selected_vehicle': selected_vehicle,
        'total_count': queryset.count(),
        'current_filters': request.GET,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related('images', 'specifications', 'compatibilities__vehicle__brand'),
        slug=slug,
        is_active=True
    )
    
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('brand').prefetch_related('images')[:4]

    reviews = product.reviews.filter(is_approved=True).select_related('user')[:10] if hasattr(product, 'reviews') else []

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    }
    return render(request, 'products/product_detail.html', context)


def wheels_list(request):
    """Dedicated wheels showcase with filters for rim size and finish."""
    wheel_cat = Category.objects.filter(slug='wheels').first()
    queryset = Product.objects.filter(
        Q(category__slug='wheels') | Q(category__parent__slug='wheels') | Q(part_type='wheels'),
        is_active=True
    ).select_related('brand').prefetch_related('images')

    paginator = Paginator(queryset, 16)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'products/wheels.html', {
        'products': page_obj,
        'category': wheel_cat,
        'total_count': queryset.count(),
    })


def tyres_list(request):
    """Dedicated tyres showcase with tyre size, brand, and type filters."""
    tyre_cat = Category.objects.filter(slug='tyres').first()
    queryset = Product.objects.filter(
        Q(category__slug='tyres') | Q(category__parent__slug='tyres') | Q(part_type='tyres'),
        is_active=True
    ).select_related('brand').prefetch_related('images')

    paginator = Paginator(queryset, 16)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'products/tyres.html', {
        'products': page_obj,
        'category': tyre_cat,
        'total_count': queryset.count(),
    })


# API Endpoints
def api_product_list(request):
    category = request.GET.get('category')
    part_type = request.GET.get('part_type')
    vehicle_id = request.GET.get('vehicle_id')

    qs = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images')
    if category:
        qs = qs.filter(Q(category__slug=category) | Q(category__parent__slug=category))
    if part_type:
        qs = qs.filter(part_type=part_type)
    if vehicle_id and vehicle_id.isdigit():
        vehicle = Vehicle.objects.filter(id=int(vehicle_id)).first()
        if vehicle:
            qs = qs.filter(Q(is_universal=True) | Q(compatibilities__vehicle=vehicle)).distinct()

    data = []
    for p in qs:
        img_url = p.primary_image.image.url if p.primary_image else '/static/images/placeholder_part.svg'
        data.append({
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name if p.brand else 'OEM Car Delights',
            'category': p.category.name,
            'part_type': p.part_type,
            'price': float(p.price),
            'mrp': float(p.mrp),
            'discount': p.discount_percentage,
            'formatted_price': p.get_formatted_price(),
            'formatted_mrp': p.get_formatted_mrp(),
            'image': img_url,
            'slug': p.slug,
            'stock': p.stock,
            'rating': float(p.rating),
        })
    return JsonResponse({'status': 'success', 'products': data})


def api_check_compatibility(request):
    product_id = request.GET.get('product_id')
    vehicle_id = request.GET.get('vehicle_id')

    if not product_id or not vehicle_id:
        return JsonResponse({'status': 'error', 'message': 'Missing product_id or vehicle_id'}, status=400)

    product = get_object_or_404(Product, id=product_id)
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if product.is_universal:
        return JsonResponse({
            'status': 'success',
            'compatible': True,
            'is_universal': True,
            'message': f'{product.name} is universal and fully compatible with {vehicle.full_name}.'
        })

    compat = ProductCompatibility.objects.filter(product=product, vehicle=vehicle).first()
    if compat:
        notes = f" ({compat.variant_notes})" if compat.variant_notes else ""
        return JsonResponse({
            'status': 'success',
            'compatible': True,
            'is_universal': False,
            'message': f'Verified 100% Compatible with {vehicle.full_name}{notes}.'
        })

    return JsonResponse({
        'status': 'success',
        'compatible': False,
        'is_universal': False,
        'message': f'This part is not certified compatible with {vehicle.full_name}.'
    })
