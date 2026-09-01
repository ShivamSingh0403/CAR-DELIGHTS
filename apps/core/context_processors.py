from apps.cart.models import Cart
from apps.core.models import Wishlist, Notification
from apps.products.models import Category
from apps.vehicles.models import Brand
from apps.garage.models import UserVehicle

def global_context(request):
    cart_count = 0
    wishlist_count = 0
    primary_vehicle = None
    notifications = []
    unread_notifs_count = 0
    greeting_name = "Guest"

    # Theme resolution
    theme = 'dark'
    if request.user.is_authenticated:
        greeting_name = request.user.get_greeting_name()
        theme = request.user.preferred_theme or request.session.get('theme', 'dark')
        
        # User Cart
        user_cart = Cart.objects.filter(user=request.user).first()
        if user_cart:
            cart_count = user_cart.get_item_count()

        # Wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

        # Primary Garage Vehicle
        primary_vehicle = UserVehicle.objects.filter(user=request.user, is_primary=True).select_related('vehicle__brand').first()
        if not primary_vehicle:
            primary_vehicle = UserVehicle.objects.filter(user=request.user).select_related('vehicle__brand').first()

        # Notifications
        notifs_qs = Notification.objects.filter(user=request.user)
        unread_notifs_count = notifs_qs.filter(is_read=False).count()
        notifications = notifs_qs[:5]
    else:
        theme = request.session.get('theme', 'dark')
        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if session_cart:
                cart_count = session_cart.get_item_count()

    nav_categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')[:10]
    nav_brands = Brand.objects.all()[:15]

    return {
        'greeting_name': greeting_name,
        'greeting_full': f"Hi {greeting_name} 👋" if request.user.is_authenticated else "Welcome to Car Delights 👋",
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'primary_garage_vehicle': primary_vehicle,
        'active_theme': theme,
        'nav_categories': nav_categories,
        'nav_brands': nav_brands,
        'notifications': notifications,
        'unread_notifs_count': unread_notifs_count,
    }
