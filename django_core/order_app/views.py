import datetime
import os
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import weasyprint

from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart_app.cart import Cart
from .tasks import order_created


@login_required()
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, _('Your cart is empty.'))
        return redirect('/')
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()

            order_created.delay(order.id)

            request.session['order_id'] = order.id

            return redirect(reverse('payment_app:process'))

    else:
        user = request.user
        form = OrderCreateForm(initial={"first_name": user.first_name,
                                        "second_name": user.second_name,
                                        "email": user.email,
                                        "city": user.city,
                                        "address": user.address,
                                        "postal_code": user.postal_code})

    context = {
        'cart': cart,
        'form': form
    }

    return render(request, 'orders/order/create.html', context=context)


@login_required()
def order_list(request):
    user = request.user

    orders = Order.objects.filter(email__iexact=user.email)

    context = {
        'orders': orders,
    }

    return render(request, 'orders/order/list.html', context=context)


@login_required()
def order_detail(request, order_id):
    now = timezone.now()
    order = Order.objects.get(id=order_id)

    if not order.paid:
        if (now - order.created).seconds // 60 <= 10:
            return redirect(reverse('payment_app:process'))

    request.session['order_id'] = None

    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets=[os.path.join(settings.STATICFILES_DIRS[0], 'css/pdf.css')])
    print('RESPONSE:', response)

    return response


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
    }

    return render(request, 'admin/orders/order/detail.html', context=context)


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets=[os.path.join(settings.STATICFILES_DIRS[0], 'css/pdf.css')])
    return response
