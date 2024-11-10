import json
from unittest.mock import patch
from types import SimpleNamespace

from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse

from shop_app.models import Product, Category
from order_app.models import Order
from coupon_app.models import Coupon
from user_app.models import CustomUser
from .cart import Cart


class CartTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Электроника', slug='Электроника')
        self.product = Product.objects.create(name='Iphone', price=70000, category=self.category)
        self.coupon = Coupon.objects.create(code="SUMMER10",
                                            discount=10,
                                            active=True,
                                            valid_from=timezone.now(),
                                            valid_to=timezone.now() + timezone.timedelta(days=10))
        self.cart = Cart(self.client)

    def test_add_to_cart(self):
        self.cart.add(self.product)
        self.assertEqual(len(self.cart), 1)

    def test_remove_from_cart(self):
        self.cart.add(self.product)
        self.cart.remove(self.product)
        self.assertEqual(len(self.cart), 0)

    def test_get_total_price(self):
        self.cart.add(self.product, quantity=5)
        self.assertEqual(self.cart.get_total_price(), 350000)

    def test_get_total_price_after_discount(self):
        self.cart.coupon_id = self.coupon.id
        self.cart.add(self.product)
        self.assertEqual(self.cart.get_total_price_after_discount(), 63000)


class IntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test category', slug='test-category')
        self.product = Product.objects.create(name='Test product', price=100, category=self.category)
        self.cart_url = reverse('cart_app:cart_detail')
        self.order_url = reverse('orders_app:order_create')

        self.user = CustomUser.objects.create_user(email='test@test.test', password='test_password')

        self.session = self.client.session
        self.cart = Cart(self.client)
        self.session.save()

    def test_add_product_to_cart(self):
        request = self.client.post(reverse('cart_app:cart_add', args=[self.product.id]), {'quantity': 1})
        cart = Cart(self.client)
        cart_product_ids = list(cart.cart.keys())
        self.assertIn(str(self.product.id), cart_product_ids)
        self.assertEqual(cart.cart[str(self.product.id)]['quantity'], 1)

    def test_change_product_quantity_in_cart(self):
        request = self.client.post(reverse('cart_app:cart_add', args=[self.product.id]), {'quantity': 3,
                                                                                                        'override': True})
        cart = Cart(self.client)

        cart_product = cart.cart[str(self.product.id)]
        self.assertEqual(cart_product['quantity'], 3)

    def test_order_creation(self):
        self.client.login(email='test@test.test', password='test_password')

        self.client.post(reverse('cart_app:cart_add', args=[self.product.id]), {'quantity': 1})
        cart = Cart(self.client)
        response = self.client.post(self.order_url, {'first_name': "Test name",
                                                          'second_name': "Test second name",
                                                          'email': "test@test.test",
                                                          'address': "Test address",
                                                          'postal_code': "Test postal code",
                                                          'city': "Test city"})
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.get_total_cost(), self.product.price)

    @patch("stripe.Webhook.construct_event")
    def test_order_payment(self, mock_construct_event):
        self.client.login(email='test@test.test', password='test_password')

        self.client.post(reverse('cart_app:cart_add', args=[self.product.id]), {'quantity': 1})
        order_response = self.client.post(self.order_url, {'first_name': "Test name",
                                                           'second_name': "Test second name",
                                                           'email': "test@test.test",
                                                           'address': "Test address",
                                                           'postal_code': "Test postal code",
                                                           'city': "Test city"})
        order = Order.objects.get()

        # Mock Stripe
        fake_event = SimpleNamespace(
            type="checkout.session.completed",
            data=SimpleNamespace(
                object=SimpleNamespace(
                    client_reference_id=order.id,
                    mode="payment",
                    payment_status="paid",
                    payment_intent="pi_fake_intent"
                )
            )
        )

        # Настройка mock для возврата подготовленного события
        mock_construct_event.return_value = fake_event

        # Заголовок Stripe подписи
        sig_header = "fake_signature"

        # Выполнение POST-запроса к вебхуку
        response = self.client.post(
            reverse('stripe-webhook'),
            data=fake_event,
            content_type="application/json",
            **{"HTTP_STRIPE_SIGNATURE": sig_header}
        )
        # End mock Stripe
        order.refresh_from_db()

        self.assertTrue(order.paid)

    def test_user_order_history_access(self):
        self.client.login(email='test@test.test', password='test_password')

        self.client.post(reverse('cart_app:cart_add', args=[self.product.id]), {'quantity': 1})
        self.client.post(self.order_url, {'first_name': "Test name",
                                              'second_name': "Test second name",
                                              'email': "test@test.test",
                                              'address': "Test address",
                                              'postal_code': "Test postal code",
                                              'city': "Test city"})

        response = self.client.get(reverse('orders_app:order_list'))
        self.assertIn('orders', response.context)
