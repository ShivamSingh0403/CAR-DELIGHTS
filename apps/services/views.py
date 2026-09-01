from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Service, ServiceCategory, ServiceBooking
from apps.vehicles.models import Vehicle
from apps.garage.models import UserVehicle
from apps.core.models import Notification

def service_list(request):
    categories = ServiceCategory.objects.prefetch_related('services').all()
    selected_cat_slug = request.GET.get('category')
    
    queryset = Service.objects.filter(is_active=True).select_related('category')
    if selected_cat_slug:
        queryset = queryset.filter(category__slug=selected_cat_slug)

    context = {
        'services': queryset,
        'categories': categories,
        'selected_category': selected_cat_slug,
    }
    return render(request, 'services/service_list.html', context)


def service_detail(request, slug):
    service = get_object_or_404(Service.objects.select_related('category'), slug=slug, is_active=True)
    related_services = Service.objects.filter(category=service.category, is_active=True).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'services/service_detail.html', context)


@login_required
def book_service(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    user_vehicles = UserVehicle.objects.filter(user=request.user).select_related('vehicle')
    all_vehicles = Vehicle.objects.select_related('brand').order_by('brand__name', 'model')

    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        custom_vehicle = request.POST.get('custom_vehicle', '').strip()
        booking_date = request.POST.get('booking_date')
        time_slot = request.POST.get('time_slot')
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        phone = request.POST.get('phone', '').strip()
        notes = request.POST.get('notes', '').strip()

        if not (booking_date and time_slot and address and phone):
            messages.error(request, "Please provide all required appointment details.")
            return render(request, 'services/book_service.html', {
                'service': service,
                'user_vehicles': user_vehicles,
                'all_vehicles': all_vehicles,
            })

        vehicle_obj = Vehicle.objects.filter(id=vehicle_id).first() if vehicle_id and vehicle_id.isdigit() else None
        
        booking = ServiceBooking.objects.create(
            user=request.user,
            service=service,
            vehicle=vehicle_obj,
            vehicle_custom_name=custom_vehicle or (vehicle_obj.full_name if vehicle_obj else 'General Vehicle'),
            booking_date=booking_date,
            time_slot=time_slot,
            address=address,
            city=city or 'Mumbai',
            pincode=pincode or '400001',
            phone=phone,
            notes=notes,
            status='Confirmed'
        )

        Notification.objects.create(
            user=request.user,
            title=f"Service Appointment Booked #{booking.booking_id}",
            message=f"Your appointment for {service.name} on {booking.booking_date} ({booking.time_slot}) has been confirmed!",
            link="/services/my-bookings/"
        )

        messages.success(request, f"Appointment #{booking.booking_id} confirmed for {service.name}!")
        return redirect('services:my_bookings')

    tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    max_date = (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    context = {
        'service': service,
        'user_vehicles': user_vehicles,
        'all_vehicles': all_vehicles,
        'min_date': tomorrow,
        'max_date': max_date,
    }
    return render(request, 'services/book_service.html', context)


@login_required
def my_bookings(request):
    bookings = ServiceBooking.objects.filter(user=request.user).select_related('service', 'vehicle__brand').order_by('-booking_date', '-created_at')
    return render(request, 'services/my_bookings.html', {'bookings': bookings})
