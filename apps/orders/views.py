from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import uuid

from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.core.models import Notification

@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is empty. Add products before checking out!")
        return redirect('products:product_list')

    # Pre-fill user data
    user = request.user
    initial_data = {
        'full_name': f"{user.first_name} {user.last_name}".strip() or user.get_greeting_name(),
        'email': user.email,
        'phone': user.phone or '',
        'address_line1': user.address_line1 or '',
        'address_line2': user.address_line2 or '',
        'city': user.city or 'Mumbai',
        'state': user.state or 'Maharashtra',
        'pincode': user.pincode or '400001',
    }

    context = {
        'cart': cart,
        'initial_data': initial_data,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@transaction.atomic
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('products:product_list')

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    address_line1 = request.POST.get('address_line1', '').strip()
    address_line2 = request.POST.get('address_line2', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    payment_method = request.POST.get('payment_method', 'UPI')
    customer_notes = request.POST.get('customer_notes', '').strip()

    if not (full_name and email and phone and address_line1 and city and state and pincode):
        messages.error(request, "Please fill in all required shipping details.")
        return redirect('orders:checkout')

    # Recalculate totals server-side
    subtotal = cart.get_subtotal()
    discount = cart.discount_amount
    total = max(0, subtotal - discount)

    # Create Order
    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        email=email,
        phone=phone,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        pincode=pincode,
        subtotal=subtotal,
        discount_amount=discount,
        shipping_fee=0.00,
        total_amount=total,
        payment_method=payment_method,
        payment_status='Paid' if payment_method in ['UPI', 'Card'] else 'Pending',
        transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
        status='Confirmed',
        tracking_number=f"EXP{uuid.uuid4().hex[:10].upper()}",
        customer_notes=customer_notes
    )

    # Create OrderItems
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            item_type=item.item_type,
            product=item.product,
            custom_build=item.custom_build,
            service=item.service,
            item_name=item.get_name(),
            item_sku=item.product.sku if item.product else 'CUSTOM-BUILD',
            price=item.price,
            quantity=item.quantity,
            total_price=item.get_total_price()
        )
        # Deduct stock for physical products
        if item.product and item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.product.save(update_fields=['stock'])

    # Clear Cart
    cart.items.all().delete()
    cart.coupon_code = None
    cart.discount_amount = 0
    cart.save()

    # Create in-app Notification
    Notification.objects.create(
        user=request.user,
        title=f"Order Confirmed #{order.order_id}",
        message=f"Thank you for ordering with Car Delights! Total: {order.get_formatted_total()}. Track your order with ID {order.order_id}.",
        link=f"/orders/{order.order_id}/"
    )

    messages.success(request, f"Order #{order.order_id} placed successfully!")
    return redirect('orders:order_success', order_id=order.order_id)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def track_order(request):
    order = None
    searched = False
    order_id = request.GET.get('order_id', '').strip()
    phone = request.GET.get('phone', '').strip()

    if order_id:
        searched = True
        qs = Order.objects.filter(order_id__iexact=order_id)
        if phone:
            qs = qs.filter(phone__icontains=phone)
        order = qs.prefetch_related('items').first()

    return render(request, 'orders/track.html', {
        'order': order,
        'searched': searched,
        'order_id': order_id,
        'phone': phone,
    })
