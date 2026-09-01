from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import json

from apps.vehicles.models import Vehicle, Brand
from apps.products.models import Product
from .models import PaintOption, CustomBuild
from apps.cart.models import Cart, CartItem

def customizer_view(request):
    vehicle_id = request.GET.get('vehicle')
    selected_vehicle = None
    
    # Priority: 1. requested vehicle 2. user's primary vehicle 3. first 3D available vehicle 4. first vehicle
    if vehicle_id and vehicle_id.isdigit():
        selected_vehicle = Vehicle.objects.filter(id=int(vehicle_id)).select_related('brand').first()
    elif request.user.is_authenticated and hasattr(request.user, 'garage_vehicles'):
        primary_uv = request.user.garage_vehicles.filter(is_primary=True).first()
        if primary_uv:
            selected_vehicle = primary_uv.vehicle

    if not selected_vehicle:
        selected_vehicle = Vehicle.objects.filter(is_3d_available=True).select_related('brand').first()
        if not selected_vehicle:
            selected_vehicle = Vehicle.objects.select_related('brand').first()

    paints = PaintOption.objects.all()
    all_vehicles = Vehicle.objects.select_related('brand').order_by('-is_3d_available', 'brand__name', 'model')
    brands = Brand.objects.all()

    context = {
        'selected_vehicle': selected_vehicle,
        'all_vehicles': all_vehicles,
        'brands': brands,
        'paints': paints,
    }
    return render(request, 'customization/customizer.html', context)


def paint_studio_view(request):
    paints = PaintOption.objects.all()
    finish_types = [f[0] for f in PaintOption.FINISH_TYPES]
    
    selected_finish = request.GET.get('finish')
    if selected_finish:
        paints = paints.filter(finish_type=selected_finish)
        
    return render(request, 'customization/paint_studio.html', {
        'paints': paints,
        'finish_types': finish_types,
        'selected_finish': selected_finish,
    })


# API Endpoints
def api_customizer_config(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle.objects.select_related('brand'), id=vehicle_id)
    paints = PaintOption.objects.all()

    # Get compatible parts for this vehicle
    compatible_products = Product.objects.filter(
        Q(is_universal=True) | Q(compatibilities__vehicle=vehicle),
        is_active=True
    ).select_related('brand', 'category').prefetch_related('images')

    def serialize_product(p):
        return {
            'id': p.id,
            'name': p.name,
            'brand': p.brand.name if p.brand else 'OEM Car Delights',
            'part_type': p.part_type,
            'price': float(p.price),
            'formatted_price': p.get_formatted_price(),
            'image': p.get_primary_image_url(),
        }

    parts_by_slot = {
        'wheels': [serialize_product(p) for p in compatible_products.filter(part_type='wheels')],
        'tyres': [serialize_product(p) for p in compatible_products.filter(part_type='tyres')],
        'bumper_front': [serialize_product(p) for p in compatible_products.filter(part_type='bumper_front')],
        'bumper_rear': [serialize_product(p) for p in compatible_products.filter(part_type='bumper_rear')],
        'spoiler': [serialize_product(p) for p in compatible_products.filter(part_type='spoiler')],
        'side_skirt': [serialize_product(p) for p in compatible_products.filter(part_type='side_skirt')],
        'diffuser': [serialize_product(p) for p in compatible_products.filter(part_type='diffuser')],
        'grille': [serialize_product(p) for p in compatible_products.filter(part_type='grille')],
        'headlights': [serialize_product(p) for p in compatible_products.filter(part_type='headlight')],
        'taillights': [serialize_product(p) for p in compatible_products.filter(part_type='taillight')],
        'exhaust': [serialize_product(p) for p in compatible_products.filter(part_type='exhaust')],
        'interior': [serialize_product(p) for p in compatible_products.filter(part_type='interior')],
    }

    paint_data = [{
        'id': p.id,
        'name': p.name,
        'finish_type': p.finish_type,
        'hex_color': p.hex_color,
        'secondary_hex_color': p.secondary_hex_color or '',
        'roughness': p.roughness,
        'metalness': p.metalness,
        'clearcoat': p.clearcoat,
        'price': float(p.price),
        'formatted_price': p.get_formatted_price(),
    } for p in paints]

    return JsonResponse({
        'status': 'success',
        'vehicle': {
            'id': vehicle.id,
            'name': vehicle.full_name,
            'brand': vehicle.brand.name,
            'model': vehicle.model,
            'variant': vehicle.variant,
            'year': vehicle.year,
            'price': float(vehicle.price),
            'formatted_price': vehicle.get_formatted_price(),
            'is_3d_available': vehicle.is_3d_available,
            'model_3d_path': vehicle.model_3d_path or '',
            'image': vehicle.get_primary_image_url(),
        },
        'paints': paint_data,
        'parts': parts_by_slot,
    })


@require_POST
def api_calculate_price(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        vehicle_id = data.get('vehicle_id')
        paint_id = data.get('paint_id')
        part_ids = data.get('part_ids', {})

        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        total = float(vehicle.price)
        breakdown = [{'label': f'Base Vehicle ({vehicle.full_name})', 'amount': float(vehicle.price)}]

        if paint_id:
            paint = PaintOption.objects.filter(id=paint_id).first()
            if paint:
                total += float(paint.price)
                breakdown.append({'label': f'Paint: {paint.name} ({paint.finish_type})', 'amount': float(paint.price)})

        for slot, pid in part_ids.items():
            if pid:
                part = Product.objects.filter(id=pid).first()
                if part:
                    total += float(part.price)
                    breakdown.append({'label': f'{part.get_part_type_display() if hasattr(part, "get_part_type_display") else slot.title()}: {part.name}', 'amount': float(part.price)})

        installation = 5000.00
        total += installation
        breakdown.append({'label': 'Professional Studio Installation & Calibration', 'amount': installation})

        return JsonResponse({
            'status': 'success',
            'total': total,
            'formatted_total': f"₹{total:,.0f}",
            'breakdown': breakdown,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def api_save_build(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        vehicle_id = data.get('vehicle_id')
        name = data.get('name', 'My Custom Build').strip() or 'My Custom Build'
        paint_id = data.get('paint_id')
        part_ids = data.get('part_ids', {})
        snapshot = data.get('snapshot_image', '')

        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        paint = PaintOption.objects.filter(id=paint_id).first() if paint_id else None

        build = CustomBuild(
            vehicle=vehicle,
            name=name,
            paint=paint,
            snapshot_image=snapshot,
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key or '',
        )

        for slot in ['wheel', 'tyre', 'bumper_front', 'bumper_rear', 'spoiler', 'side_skirt', 'diffuser', 'grille', 'headlights', 'taillights', 'exhaust', 'interior']:
            pid = part_ids.get(slot) or part_ids.get(f'{slot}s')
            if pid:
                prod = Product.objects.filter(id=pid).first()
                setattr(build, slot, prod)

        build.save()

        # If add_to_cart requested
        add_to_cart = data.get('add_to_cart', False)
        if add_to_cart:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key if not request.user.is_authenticated else None
            )
            CartItem.objects.create(
                cart=cart,
                custom_build=build,
                item_type='custom_build',
                quantity=1,
                price=build.total_price
            )

        return JsonResponse({
            'status': 'success',
            'build_id': build.id,
            'total_price': float(build.total_price),
            'formatted_total': build.get_formatted_total(),
            'message': f'Build "{build.name}" saved successfully!'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
