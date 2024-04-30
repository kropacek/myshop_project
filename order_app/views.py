from django.http import HttpResponse
from django.shortcuts import render

from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart_app.cart import Cart


def order_create(request):

    cart = Cart(request)
    if len(cart) == 0:
        # use messages framework and redirect
        return HttpResponse('Empty cart!')
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            context = {
                'order': order
            }
            return render(request, 'orders/order/created.html', context=context)

    else:
        form = OrderCreateForm()

    context = {
        'cart': cart,
        'form': form
    }

    return render(request, 'orders/order/create.html', context = context)