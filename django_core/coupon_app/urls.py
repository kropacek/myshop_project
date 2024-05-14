from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import coupon_apply, coupon_delete

app_name = 'coupon_app'


urlpatterns = [
    path(_('apply/'), coupon_apply, name='coupon_apply'),
    path(_('delete/'), coupon_delete, name='coupon_delete'),
]