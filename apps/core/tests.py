from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.vehicles.models import Brand, Vehicle, VehicleImage
from apps.products.models import Category, ProductBrand, Product, ProductImage, ProductCompatibility
from apps.customization.models import PaintOption, CustomBuild
from apps.services.models import ServiceCategory, Service, ServiceBooking
from apps.offers.models import Offer
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.garage.models import UserVehicle
from services.image_validator import ImageValidator
import json

User = get_user_model()

class CarDelightsTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        
        # User Setup
        self.user = User.objects.create_user(
            username='shivam',
            email='shivam@example.com',
            password='password123',
            display_name='Shivam',
            first_name='Shivam',
            phone='+91 98765 43210',
            address_line1='Flat 402, Sea Green Apt',
            city='Mumbai',
            state='Maharashtra',
            pincode='400050'
        )

        # Brand & Vehicle Setup
        self.brand_tata = Brand.objects.create(name='Tata', origin_country='India')
        self.vehicle_nexon = Vehicle.objects.create(
            brand=self.brand_tata,
            model='Nexon',
            variant='Fearless Plus S DCA',
            year=2025,
            body_type='SUV',
            fuel_type='Petrol',
            transmission='DCT',
            engine='1.2L Turbo',
            engine_capacity='1199 cc',
            power='120 PS',
            torque='170 Nm',
            price=1500000.00,
            featured=True,
            is_3d_available=True
        )
        VehicleImage.objects.create(
            vehicle=self.vehicle_nexon,
            image='vehicles/gallery/test_nexon.svg',
            is_primary=True
        )

        # Category & Product Setup
        self.cat_brakes = Category.objects.create(name='Brakes', slug='brakes')
        self.p_brand = ProductBrand.objects.create(name='Brembo')
        self.product_caliper = Product.objects.create(
            name='Brembo 6-Piston Caliper Kit',
            brand=self.p_brand,
            category=self.cat_brakes,
            sku='BRK-001',
            mrp=150000.00,
            price=130000.00,
            stock=10,
            part_type='calipers',
            is_universal=False,
            is_3d_part=True
        )
        ProductImage.objects.create(
            product=self.product_caliper,
            image='products/gallery/test_caliper.svg',
            image_type='primary'
        )
        ProductCompatibility.objects.create(
            product=self.product_caliper,
            vehicle=self.vehicle_nexon,
            variant_notes='All variants'
        )

        # Paint Setup
        self.paint = PaintOption.objects.create(
            name='Jet Black',
            finish_type='Solid',
            hex_color='#0A0A0A',
            price=20000.00
        )

        # Service Setup
        self.s_cat = ServiceCategory.objects.create(name='Wash', slug='wash')
        self.service = Service.objects.create(
            category=self.s_cat,
            name='Deluxe Hydrophobic Foam Wash',
            price=899.00,
            duration='45 mins',
            features='Snow Foam\nUnderbody Wash'
        )

        # Offer Setup
        self.offer = Offer.objects.create(
            title='Festival Offer',
            coupon_code='FESTIVE10',
            offer_type='percentage',
            discount_percentage=10,
            minimum_order=1000.00
        )

    def test_dynamic_user_greeting(self):
        self.client.login(username='shivam', password='password123')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi Shivam 👋')

    def test_vehicle_list_and_detail(self):
        response = self.client.get(reverse('vehicles:vehicle_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nexon')

        response = self.client.get(self.vehicle_nexon.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fearless Plus S DCA')

    def test_product_list_and_detail(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brembo 6-Piston Caliper Kit')

        response = self.client.get(self.product_caliper.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BRK-001')

    def test_compatibility_api(self):
        url = f"{reverse('products:api_check_compatibility')}?product_id={self.product_caliper.id}&vehicle_id={self.vehicle_nexon.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['compatible'])

    def test_cart_operations(self):
        self.client.login(username='shivam', password='password123')
        
        # Add to cart AJAX
        payload = json.dumps({
            'item_type': 'product',
            'product_id': self.product_caliper.id,
            'quantity': 1
        })
        response = self.client.post(
            reverse('cart:api_add_to_cart'),
            payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200, msg=f"Error: {response.content.decode('utf-8')}")
        self.assertEqual(response.json()['cart_count'], 1)

        # Apply coupon
        response = self.client.post(reverse('cart:apply_coupon'), {'coupon_code': 'FESTIVE10'}, follow=True)
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.discount_amount, 13000.00) # 10% of 130,000

    def test_checkout_and_order_creation(self):
        self.client.login(username='shivam', password='password123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            item_type='product',
            product=self.product_caliper,
            price=self.product_caliper.price,
            quantity=1
        )

        order_data = {
            'full_name': 'Shivam Sharma',
            'email': 'shivam@example.com',
            'phone': '+91 98765 43210',
            'address_line1': '402 Sea Green Apt',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400050',
            'payment_method': 'UPI'
        }
        response = self.client.post(reverse('orders:place_order'), order_data, follow=True)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertTrue(order.order_id.startswith('CD-'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, 130000.00)

    def test_service_booking(self):
        self.client.login(username='shivam', password='password123')
        booking_data = {
            'vehicle_id': self.vehicle_nexon.id,
            'booking_date': '2026-09-05',
            'time_slot': '10:00 AM - 12:00 PM',
            'address': 'Bandra West, Mumbai',
            'city': 'Mumbai',
            'pincode': '400050',
            'phone': '+91 98765 43210',
            'notes': 'Please inspect water spots'
        }
        response = self.client.post(
            reverse('services:book_service', kwargs={'slug': self.service.slug}),
            booking_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        booking = ServiceBooking.objects.filter(user=self.user).first()
        self.assertIsNotNone(booking)
        self.assertTrue(booking.booking_id.startswith('BK-'))

    def test_customizer_price_calculation_api(self):
        payload = json.dumps({
            'vehicle_id': self.vehicle_nexon.id,
            'paint_id': self.paint.id,
            'part_ids': {'wheel': self.product_caliper.id}
        })
        response = self.client.post(
            reverse('customization:api_calculate_price'),
            payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # 1,500,000 (vehicle) + 20,000 (paint) + 130,000 (part) + 5,000 (installation) = 1,655,000
        self.assertEqual(data['total'], 1655000.00)

    def test_garage_management(self):
        self.client.login(username='shivam', password='password123')
        response = self.client.post(reverse('garage:add_vehicle'), {
            'vehicle_id': self.vehicle_nexon.id,
            'nickname': 'Red Comet',
            'registration_number': 'MH 02 CD 8888',
            'purchase_year': 2025,
            'current_mileage': 5000,
            'is_primary': 'on'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        uv = UserVehicle.objects.filter(user=self.user).first()
        self.assertIsNotNone(uv)
        self.assertTrue(uv.is_primary)
        self.assertEqual(uv.nickname, 'Red Comet')

    def test_all_key_routes(self):
        self.client.login(username='shivam', password='password123')
        # Setup cart item so checkout returns 200
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            item_type='product',
            product=self.product_caliper,
            price=self.product_caliper.price,
            quantity=1
        )

        routes_to_test = [
            '/',
            '/vehicles/',
            '/products/',
            '/products/wheels/',
            '/products/tyres/',
            '/customizer/',
            '/customizer/paint/',
            '/customizer/paint-studio/',
            '/garage/',
            '/garage/builds/',
            '/garage/saved-builds/',
            '/cart/',
            '/orders/',
            '/orders/checkout/',
            '/orders/track/',
            '/services/',
            '/offers/',
            '/tata-zone/',
            '/accounts/',
            '/accounts/profile/',
        ]
        for path in routes_to_test:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, msg=f"Path {path} returned status {res.status_code}")

    def test_theme_switcher_api(self):
        self.client.login(username='shivam', password='password123')
        res = self.client.post(
            reverse('accounts:set_theme'),
            json.dumps({'theme': 'light'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.preferred_theme, 'light')

    def test_wishlist_toggle_api(self):
        self.client.login(username='shivam', password='password123')
        res = self.client.post(
            reverse('core:api_toggle_wishlist'),
            json.dumps({'product_id': self.product_caliper.id}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['added'])
        self.assertEqual(data['wishlist_count'], 1)

    def test_search_suggestions_api(self):
        res = self.client.get(f"{reverse('core:api_search_suggestions')}?q=Nexon")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['results']) > 0)

    def test_health_check_endpoint(self):
        res = self.client.get('/health/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['services']['database'], 'connected')

    def test_custom_404_page(self):
        res = self.client.get('/a-route-that-definitely-does-not-exist-404/')
        self.assertEqual(res.status_code, 404)
        self.assertContains(res, "ENGINE STALL", status_code=404)


