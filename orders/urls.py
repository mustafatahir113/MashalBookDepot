from django.urls import path

from .views import (
    checkout,
    my_orders,
    order_detail,
    download_invoice,
    cancel_order
)

urlpatterns = [

    path(
        'checkout/',
        checkout,
        name='checkout'
    ),

    path(
        'my-orders/',
        my_orders,
        name='my_orders'
    ),

    path(
        'detail/<int:order_id>/',
        order_detail,
        name='order_detail'
    ),

    path(
        'invoice/<int:order_id>/',
        download_invoice,
        name='download_invoice'
    ),
    path(
    'cancel/<int:order_id>/',
    cancel_order,
    name='cancel_order'
),

]