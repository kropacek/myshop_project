from django.test import TestCase

from .models import Product, Category


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Электроника', slug='Электроника')
        self.product = Product.objects.create(name='Ноутбук', slug='Ноутбук', category=self.category, price=100000)

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Ноутбук')
        self.assertEqual(self.product.price, 100000)
        self.assertEqual(self.product.category.name, 'Электроника')