from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='code')

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    discount = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)]
    )

    active = models.BooleanField()

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'