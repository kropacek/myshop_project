from django.urls import path

from .views import payment_process, payment_canceled, payment_completed
from .webhooks import stripe_webhook

app_name = 'payment_app'

urlpatterns = [
    path('process/', payment_process, name='process'),
    path('canceled/', payment_canceled, name='canceled'),
    path('completed/', payment_completed, name='completed'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]