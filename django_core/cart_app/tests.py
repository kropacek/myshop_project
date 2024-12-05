import json
from unittest.mock import patch
from types import SimpleNamespace

from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from playwright.sync_api import sync_playwright

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


class EndToEndTests(TestCase):

    # noinspection PyMethodMayBeStatic
    def test_pdf_order(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Открыть сайт
            page.goto("http://localhost:8000/en/user/login/")

            page.fill('input[name="email"]', "test@test.test")
            page.fill('input[name="password"]', "test_password")
            page.click('input[type="submit"][value="Log in"]')

            page.click('a#order-a')
            page.goto("http://127.0.0.1:8000/en/orders/1/")

            assert "/en/orders/1/" in page.url

            browser.close()

    # noinspection PyMethodMayBeStatic
    def test_order_payment(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Открыть сайт
            page.goto("http://localhost:8000/en/user/login/")

            # Авторизация
            page.fill('input[name="email"]', "test@test.test")
            page.fill('input[name="password"]', "test_password")
            page.click('input[type="submit"][value="Log in"]')

            # Добавить товар в корзину
            page.goto("http://localhost:8000/en/1/product-1/")
            page.select_option('select[name="quantity"]', "1")
            # Нажатие на кнопку "Add to cart"
            page.click('input[type="submit"][value="Add to cart"]')

            # Перейти к оформлению заказа
            page.goto("http://localhost:8000/en/orders/create/")
            page.fill('input[name="first_name"]', "TEST")
            page.fill('input[name="second_name"]', "TESTTEST")
            page.fill('input[name="email"]', "test@test.test")
            page.fill('input[name="address"]', "Test Address")
            page.fill('input[name="postal_code"]', "12345")
            page.fill('input[name="city"]', "Test City")
            page.click('input[type="submit"][value="Place order"]')

            # Успешная оплата через Stripe
            with page.expect_navigation():
                page.click('input[type="submit"][value="Pay now"]')

            page.locator('input#email').fill("test@test.test")
            page.evaluate("document.querySelector('button[data-testid=\"card-accordion-item-button\"]').click()")


            # Заполняем номер карты
            page.locator("input#cardNumber").fill("4242424242424242")

            # Заполняем дату истечения карты
            page.locator("input#cardExpiry").fill("1234")

            # Заполняем CVC
            page.locator("input#cardCvc").fill("123")

            # Заполняем Имя, фамилия
            page.locator("input#billingName").fill("Test Test")


            page.evaluate("document.querySelector('button[data-testid=\"hosted-payment-submit-button\"]').click()")
            page.wait_for_timeout(10000)

            assert "completed" in page.url


            browser.close()
