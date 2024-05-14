from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name=_('code'))

    valid_from = models.DateTimeField(verbose_name=_('valid from'))
    valid_to = models.DateTimeField(verbose_name=_('valid to'))

    discount = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)],
        verbose_name=_('discount')
    )

    active = models.BooleanField(verbose_name=_('active'))

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
