from django.urls import path

from .views import order_create, admin_order_detail, admin_order_pdf, order_list, order_detail
from django.utils.translation import gettext_lazy as _

app_name = 'orders_app'

urlpatterns = [
    path(_('create/'), order_create, name='order_create'),
    path(_('list/'), order_list, name='order_list'),
    path(_('<int:order_id>/'), order_detail, name='order_detail'),
    path('admin/order/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/pdf/', admin_order_pdf, name='admin_order_pdf'),
]
