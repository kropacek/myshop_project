from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CouponAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coupon_app'
    verbose_name = _('coupon')
