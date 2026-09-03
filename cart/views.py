from django.http import JsonResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.contrib import messages

from .models import Cart, CartItem
from products.models import Product


# =========================================================
# ADD TO CART
# =========================================================

def add_to_cart(request, product_id):

    if not request.user.is_authenticated:

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'login_required': True
            })

        messages.error(
            request,
            'Please login first.'
        )

        return redirect('login')

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # =====================================================
    # STOCK CHECK
    # =====================================================

    if product.stock <= 0:

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'out_of_stock': True,
                'message': 'Product is out of stock.'
            })

        messages.error(
            request,
            'Product is out of stock.'
        )

        return redirect('home')

    # =====================================================
    # GET / CREATE CART
    # =====================================================

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    # =====================================================
    # GET / CREATE CART ITEM
    # =====================================================

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # =====================================================
    # ITEM ALREADY EXISTS
    # =====================================================

    if not item_created:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1
            cart_item.save()

            message = 'Cart quantity updated.'

        else:

            message = 'Maximum stock reached.'

    else:

        message = 'Product added to cart.'

    # =====================================================
    # CART COUNT
    # =====================================================

    cart_count = sum(
        item.quantity
        for item in cart.items.all()
    )

    # =====================================================
    # AJAX RESPONSE
    # =====================================================

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'product_id': product.id,
            'added': True,
            'message': message
        })

    # =====================================================
    # NORMAL REQUEST
    # =====================================================

    messages.success(
        request,
        message
    )

    # =====================================================
    # PRODUCT DETAIL REDIRECT
    # =====================================================

    if request.GET.get('next') == 'detail':

        return redirect(
            'product_detail',
            pk=product.id
        )

    # =====================================================
    # DEFAULT CART REDIRECT
    # =====================================================

    return redirect('view_cart')


# =========================================================
# VIEW CART
# =========================================================

def view_cart(request):

    if not request.user.is_authenticated:

        messages.error(
            request,
            'Please login first.'
        )

        return redirect('login')

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = CartItem.objects.filter(
        cart=cart
    ).select_related('product')

    total = sum(
        item.total_price
        for item in items
    )

    return render(
        request,
        'cart.html',
        {
            'items': items,
            'total': total
        }
    )


# =========================================================
# REMOVE FROM CART
# =========================================================

def remove_from_cart(request, item_id):

    if not request.user.is_authenticated:

        return redirect('login')

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    messages.success(
        request,
        'Item removed from cart.'
    )

    return redirect('view_cart')


# =========================================================
# INCREASE QUANTITY
# =========================================================

def increase_quantity(request, item_id):

    if not request.user.is_authenticated:

        return redirect('login')

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity < item.product.stock:

        item.quantity += 1
        item.save()

        messages.success(
            request,
            'Quantity increased.'
        )

    else:

        messages.error(
            request,
            'No more stock available.'
        )

    return redirect('view_cart')


# =========================================================
# DECREASE QUANTITY
# =========================================================

def decrease_quantity(request, item_id):

    if not request.user.is_authenticated:

        return redirect('login')

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity > 1:

        item.quantity -= 1
        item.save()

        messages.success(
            request,
            'Quantity decreased.'
        )

    else:

        item.delete()

        messages.success(
            request,
            'Item removed from cart.'
        )

    return redirect('view_cart')