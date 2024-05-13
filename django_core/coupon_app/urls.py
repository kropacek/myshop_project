from django.urls import path

from .views import coupon_apply, coupon_delete

app_name = 'coupon_app'


urlpatterns = [
    path('apply/', coupon_apply, name='coupon_apply'),
    path('delete/', coupon_delete, name='coupon_delete'),
]