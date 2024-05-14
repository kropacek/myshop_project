from django import forms
from .enums import PRODUCT_QUANTITY_CHOICES
from django.utils.translation import gettext_lazy as _


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int, label=_('quantity'))
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput, label=_('override'))
