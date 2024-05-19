from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name=_("email"))

    first_name = models.CharField(max_length=30, null=False, verbose_name=_("first name"))
    second_name = models.CharField(max_length=30, null=True, verbose_name=_("second name"))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("date of birth"))

    city = models.CharField(blank=True, max_length=256, null=True, verbose_name=_('City'))
    address = models.CharField(blank=True, max_length=256, null=True, verbose_name=_('Address'))
    postal_code = models.CharField(blank=True, max_length=9, null=True, verbose_name=_('Postal code'))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
