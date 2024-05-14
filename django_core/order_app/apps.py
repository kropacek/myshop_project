from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrderAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order_app'
    verbose_name = _('order')
