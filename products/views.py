from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import ReviewForm
from .models import Product


def product_detail(request, pk):

    product = get_object_or_404(
        Product.objects
        .select_related('category')
        .prefetch_related(
            'additional_images',
            'reviews__user'
        ),
        pk=pk
    )

    # =========================================
    # GALLERY IMAGES
    # =========================================

    gallery_images = product.additional_images.all()

    image_count = gallery_images.count()

    if product.image:
        image_count += 1

    # =========================================
    # REVIEWS
    # =========================================

    reviews = (
        product.reviews
        .select_related('user')
        .all()
    )

    # =========================================
    # REVIEW FORM
    # =========================================

    if request.method == 'POST':

        if not request.user.is_authenticated:
            return redirect('login')

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.product = product
            review.user = request.user

            review.save()

            return redirect(
                'product_detail',
                pk=product.pk
            )

    else:

        form = ReviewForm()

    # =========================================
    # CART CHECK
    # =========================================

    is_in_cart = False

    if request.user.is_authenticated:

        try:

            from cart.models import CartItem

            is_in_cart = CartItem.objects.filter(
                cart__user=request.user,
                product=product
            ).exists()

        except Exception:

            is_in_cart = False

    # =========================================
    # CART COUNT
    # =========================================

    cart_count = 0

    if request.user.is_authenticated:

        try:

            from cart.models import Cart

            cart, created = Cart.objects.get_or_create(
                user=request.user
            )

            cart_count = sum(
                item.quantity
                for item in cart.items.all()
            )

        except Exception:

            cart_count = 0

    # =========================================
    # RELATED PRODUCTS
    # =========================================

    related_products = (
        Product.objects
        .select_related('category')
        .exclude(pk=product.pk)
    )

    if product.category:

        related_products = (
            related_products
            .filter(
                category=product.category
            )
        )

    related_products = (
        related_products
        .order_by('-created_at')[:6]
    )

    # =========================================
    # CONTEXT
    # =========================================

    context = {

        'product': product,

        'gallery_images': gallery_images,

        'image_count': image_count,

        'reviews': reviews,

        'form': form,

        'related_products': related_products,

        'is_in_cart': is_in_cart,

        'cart_count': cart_count,
    }

    return render(
        request,
        'products/product_detail.html',
        context
    )