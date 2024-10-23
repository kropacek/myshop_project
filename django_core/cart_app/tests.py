from django.utils import timezone
from django.test import TestCase

from shop_app.models import Product, Category
from coupon_app.models import Coupon
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