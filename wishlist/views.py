from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Wishlist
from products.models import Product



@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:

        wishlist_item.delete()

        added = False

    else:

        Wishlist.objects.create(
            user=request.user,
            product=product
        )

        added = True

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        return JsonResponse({
            'success': True,
            'added': added,
            'wishlist_count': wishlist_count,
            'product_id': product.id
        })

    return redirect('my_wishlist') 

@login_required
def my_wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'wishlist.html',
        {
            'wishlist_items': wishlist_items
        }
    )


@login_required
def remove_from_wishlist(request, item_id):

    item = get_object_or_404(
        Wishlist,
        id=item_id,
        user=request.user
    )

    item.delete()

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    # AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        return JsonResponse({
            'success': True,
            'wishlist_count': wishlist_count
        })

    return redirect('my_wishlist')