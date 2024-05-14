import os
from io import BytesIO

import weasyprint
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from order_app.models import Order


@shared_task
def payment_completed(order_id):
    order = Order.objects.get(id=order_id)

    subject = _(f'My Shop – Invoice no. {order.id}')
    message = _('Please, find attached the invoice for your recent purchase.')
    email = EmailMessage(subject,
                         message,
                         f'{settings.EMAIL_HOST_USER}',
                         [order.email])

    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(os.path.join(settings.STATICFILES_DIRS[0], 'css/pdf.css'))]
    weasyprint.HTML(string=html).write_pdf(out,
                                           stylesheets=stylesheets)

    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')

    email.send()
