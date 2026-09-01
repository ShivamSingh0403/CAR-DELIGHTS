from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import UserVehicle
from apps.vehicles.models import Vehicle, Brand
from apps.products.models import Product
from apps.customization.models import CustomBuild
from apps.cart.models import Cart, CartItem

@login_required
def my_garage_view(request):
    user_vehicles = UserVehicle.objects.filter(user=request.user).select_related('vehicle__brand').prefetch_related('vehicle__images')
    primary_vehicle = user_vehicles.filter(is_primary=True).first() or user_vehicles.first()
    
    compatible_products = []
    if primary_vehicle:
        compatible_products = Product.objects.filter(
            Q(is_universal=True) | Q(compatibilities__vehicle=primary_vehicle.vehicle),
            is_active=True
        ).select_related('brand', 'category').prefetch_related('images')[:8]

    all_vehicles = Vehicle.objects.select_related('brand').order_by('brand__name', 'model')
    brands = Brand.objects.all()

    context = {
        'user_vehicles': user_vehicles,
        'primary_vehicle': primary_vehicle,
        'compatible_products': compatible_products,
        'all_vehicles': all_vehicles,
        'brands': brands,
    }
    return render(request, 'garage/my_garage.html', context)


@login_required
@require_POST
def add_vehicle_to_garage(request):
    vehicle_id = request.POST.get('vehicle_id')
    nickname = request.POST.get('nickname', '').strip()
    registration = request.POST.get('registration_number', '').strip()
    year = request.POST.get('purchase_year') or 2024
    mileage = request.POST.get('current_mileage') or 15000
    is_primary = request.POST.get('is_primary') == 'on'

    if not vehicle_id:
        messages.error(request, "Please select a vehicle to add to your garage.")
        return redirect('garage:my_garage')

    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    uv = UserVehicle.objects.create(
        user=request.user,
        vehicle=vehicle,
        nickname=nickname,
        registration_number=registration,
        purchase_year=int(year),
        current_mileage=int(mileage),
        is_primary=is_primary
    )
    messages.success(request, f"{vehicle.full_name} added to your Garage!")
    return redirect('garage:my_garage')


@login_required
def set_primary_vehicle(request, pk):
    uv = get_object_or_404(UserVehicle, id=pk, user=request.user)
    uv.is_primary = True
    uv.save()
    messages.success(request, f"{uv.vehicle.full_name} is now your primary garage vehicle.")
    return redirect('garage:my_garage')


@login_required
def delete_garage_vehicle(request, pk):
    uv = get_object_or_404(UserVehicle, id=pk, user=request.user)
    name = uv.vehicle.full_name
    uv.delete()
    messages.info(request, f"{name} removed from your garage.")
    return redirect('garage:my_garage')


@login_required
def saved_builds_view(request):
    builds = CustomBuild.objects.filter(user=request.user).select_related(
        'vehicle__brand', 'paint', 'wheel', 'tyre', 'spoiler'
    ).order_by('-created_at')
    
    return render(request, 'garage/saved_builds.html', {'builds': builds})


@login_required
def duplicate_build(request, pk):
    build = get_object_or_404(CustomBuild, id=pk, user=request.user)
    build.pk = None
    build.id = None
    build.name = f"{build.name} (Copy)"
    build.save()
    messages.success(request, f'Build duplicated as "{build.name}"')
    return redirect('garage:saved_builds')


@login_required
def delete_build(request, pk):
    build = get_object_or_404(CustomBuild, id=pk, user=request.user)
    name = build.name
    build.delete()
    messages.info(request, f'Build "{name}" deleted.')
    return redirect('garage:saved_builds')


@login_required
def add_build_to_cart(request, pk):
    build = get_object_or_404(CustomBuild, id=pk, user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    CartItem.objects.create(
        cart=cart,
        custom_build=build,
        item_type='custom_build',
        quantity=1,
        price=build.total_price
    )
    messages.success(request, f'Custom build "{build.name}" added to your cart!')
    return redirect('cart:cart_detail')
