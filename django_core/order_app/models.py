from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

from shop_app.models import Product
from coupon_app.models import Coupon


class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=_('first_name'))
    second_name = models.CharField(max_length=50, verbose_name=_('second_name'))
    email = models.EmailField(verbose_name=_('email'))
    address = models.CharField(max_length=250, verbose_name=_('address'))
    postal_code = models.CharField(max_length=20, verbose_name=_('postal_code'))
    city = models.CharField(max_length=100, verbose_name=_('city'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('updated'))
    paid = models.BooleanField(default=False, verbose_name=_('paid'))

    stripe_id = models.CharField(max_length=250, blank=True, verbose_name=_('stripe_id'))

    coupon = models.ForeignKey(Coupon,
                               related_name='orders',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE,
                               verbose_name=_('coupon'))

    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                   verbose_name=_('discount'))

    class Meta:
        ordering = ['-created']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    indexes = [
        models.Index(fields=['-created']),
    ]

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        if self.discount:
            return self.get_total_cost_before_discount()  * (self.discount / Decimal(100))
        return Decimal(0)

    def get_total_cost(self):
        return self.get_total_cost_before_discount() - self.get_discount()

    def get_stripe_url(self):
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path = '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_('orders'))
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name=_('product'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_('quantity'))

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
