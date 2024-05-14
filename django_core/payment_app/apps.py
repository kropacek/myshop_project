from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PaymentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment_app'
    verbose_name = _('payment')
