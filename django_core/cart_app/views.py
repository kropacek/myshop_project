from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from shop_app.models import Product
from coupon_app.forms import CouponApplyForm
from shop_app.recommender import Recommender

from .forms import CartAddProductForm
from .cart import Cart


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])

    return redirect('cart_app:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_app:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True,
        })
    coupon_apply_form = CouponApplyForm()

    r = Recommender()
    cart_products = [item['product'] for item in cart]

    if cart_products:
        recommended_products = r.suggest_products_for(cart_products, 4)
    else:
        recommended_products = []

    context = {
        'cart': cart,
        'coupon_apply_form': coupon_apply_form,
        'recommended_products': recommended_products,
    }

    return render(request, 'cart/detail.html', context=context)