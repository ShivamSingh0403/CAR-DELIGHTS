from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
from decimal import Decimal

from .models import Cart, CartItem
from apps.products.models import Product
from apps.customization.models import CustomBuild
from apps.services.models import Service
from apps.offers.models import Offer

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Migrate any anonymous session cart
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    item.cart = cart
                    item.save()
                session_cart.delete()
        return cart
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart


def cart_detail(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def add_to_cart_ajax(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_type = data.get('item_type', 'product')
        product_id = data.get('product_id')
        build_id = data.get('build_id')
        service_id = data.get('service_id')
        quantity = int(data.get('quantity', 1))

        cart = get_or_create_cart(request)

        if item_type == 'product' and product_id:
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='product',
                product=product,
                defaults={'price': product.price, 'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            item_name = product.name

        elif item_type == 'custom_build' and build_id:
            build = get_object_or_404(CustomBuild, id=build_id)
            cart_item = CartItem.objects.create(
                cart=cart,
                item_type='custom_build',
                custom_build=build,
                price=build.total_price,
                quantity=1
            )
            item_name = f"Custom Build: {build.name}"

        elif item_type == 'service' and service_id:
            service = get_object_or_404(Service, id=service_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='service',
                service=service,
                defaults={'price': service.price, 'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            item_name = service.name
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid item data'}, status=400)

        return JsonResponse({
            'status': 'success',
            'message': f'"{item_name}" added to your cart!',
            'cart_count': cart.get_item_count(),
            'cart_total': cart.get_formatted_total(),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def update_quantity_ajax(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_id = data.get('item_id')
        action = data.get('action') # 'increase', 'decrease', or 'set'
        value = data.get('value')

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        elif action == 'set' and value:
            qty = int(value)
            if qty > 0:
                cart_item.quantity = qty
                cart_item.save()
            else:
                cart_item.delete()

        return JsonResponse({
            'status': 'success',
            'cart_count': cart.get_item_count(),
            'cart_subtotal': cart.get_formatted_subtotal(),
            'cart_total': cart.get_formatted_total(),
            'cart_savings': cart.get_formatted_savings(),
            'item_total': cart_item.get_formatted_total() if cart_item.pk else '₹0',
            'item_qty': cart_item.quantity if cart_item.pk else 0,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def remove_from_cart_ajax(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_id = data.get('item_id')

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        name = cart_item.get_name()
        cart_item.delete()

        return JsonResponse({
            'status': 'success',
            'message': f'"{name}" removed from cart.',
            'cart_count': cart.get_item_count(),
            'cart_subtotal': cart.get_formatted_subtotal(),
            'cart_total': cart.get_formatted_total(),
            'cart_savings': cart.get_formatted_savings(),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def apply_coupon(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = get_or_create_cart(request)

    if not code:
        messages.error(request, "Please enter a valid coupon code.")
        return redirect('cart:cart_detail')

    offer = Offer.objects.filter(coupon_code__iexact=code, is_active=True).first()
    if not offer:
        messages.error(request, f'Coupon code "{code}" is invalid or expired.')
        cart.coupon_code = None
        cart.discount_amount = 0
        cart.save()
        return redirect('cart:cart_detail')

    subtotal = cart.get_subtotal()
    if subtotal < offer.minimum_order:
        messages.error(request, f'Coupon "{code}" requires a minimum order of ₹{offer.minimum_order:,.0f}.')
        return redirect('cart:cart_detail')

    # Calculate discount
    if offer.discount_percentage > 0:
        discount = (subtotal * Decimal(str(offer.discount_percentage))) / Decimal('100')
        if offer.max_discount_amount:
            discount = min(discount, Decimal(str(offer.max_discount_amount)))
    else:
        discount = Decimal(str(offer.fixed_discount or '0.00'))

    cart.coupon_code = offer.coupon_code
    cart.discount_amount = discount
    cart.save()
    messages.success(request, f'Coupon "{offer.coupon_code}" applied! You saved ₹{discount:,.0f}.')
    return redirect('cart:cart_detail')


def clear_cart(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    cart.coupon_code = None
    cart.discount_amount = 0
    cart.save()
    messages.info(request, "Your cart has been cleared.")
    return redirect('cart:cart_detail')
