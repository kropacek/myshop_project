from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'second_name', 'email', 'address', 'postal_code', 'city'
        ]
        labels = {
            'first_name': _('First name'),
            'second_name': _('Second name'),
            'email': _('Email'),
            'city': _('City'),
            'address': _('Address'),
            'postal_code': _('Postal code'),
        }
