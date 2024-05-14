from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import payment_process, payment_canceled, payment_completed
from .webhooks import stripe_webhook

app_name = 'payment_app'

urlpatterns = [
    path(_('process/'), payment_process, name='process'),
    path(_('canceled/'), payment_canceled, name='canceled'),
    path(_('completed/'), payment_completed, name='completed'),
]