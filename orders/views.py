from django.shortcuts import render, redirect, get_object_or_404
from .forms import CheckoutForm
from .models import Order, OrderItem
from django.contrib import messages
from cart.models import Cart
from printing.models import PrintingOrder
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from reportlab.pdfgen import canvas


@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'order_detail.html', {
        'order': order
    })


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    printing_orders = PrintingOrder.objects.filter(
        user=request.user
    ).order_by('-created_at')

    print("================================")
    print("CURRENT USER:", request.user)
    print("CURRENT USER ID:", request.user.id)
    print("NORMAL ORDERS:", orders.count())
    print("PRINTING ORDERS:", printing_orders.count())

    for order in orders:
        print(
            "NORMAL ORDER:",
            order.id,
            "| USER:",
            order.user_id,
            "| STATUS:",
            order.status
        )

    for printing_order in printing_orders:
        print(
            "PRINTING ORDER:",
            printing_order.id,
            "| USER:",
            printing_order.user_id,
            "| STATUS:",
            printing_order.status
        )

    print("================================")

    return render(
        request,
        'my_orders.html',
        {
            'orders': orders,
            'printing_orders': printing_orders,
        }
    )

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    printing_orders = PrintingOrder.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'my_orders.html', {
        'orders': orders,
        'printing_orders': printing_orders,
    })
def checkout(request):

    if not request.user.is_authenticated:
        return redirect('/admin/login/')

    cart = Cart.objects.get(
        user=request.user
    )

    if request.method == 'POST':

        form = CheckoutForm(
            request.POST
        )

        if form.is_valid():

            order = form.save(
                commit=False
            )

            order.user = request.user

            total = 0

            for item in cart.items.all():

                total += item.total_price

            order.total_amount = total

            order.save()

            for item in cart.items.all():

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

                # STOCK MINUS

                product = item.product

                if product.stock >= item.quantity:

                    product.stock -= item.quantity

                else:

                    product.stock = 0

                product.save()

            cart.items.all().delete()

            return redirect('home')

    else:

        form = CheckoutForm(
            initial={
                'full_name': request.user.username,
                'phone': request.user.phone,
            }
        )

    return render(request, 'checkout.html', {
        'form': form,
        'items': cart.items.all(),
        'total': sum(
            item.total_price
            for item in cart.items.all()
        )
    })


@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)

    y = 800

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        100,
        y,
        "Mashal Book Depot"
    )

    y -= 40

    p.setFont(
        "Helvetica",
        12
    )

    p.drawString(
        100,
        y,
        f"Order #{order.id}"
    )

    y -= 25

    p.drawString(
        100,
        y,
        f"Customer: {order.full_name}"
    )

    y -= 25

    p.drawString(
        100,
        y,
        f"Phone: {order.phone}"
    )

    y -= 40

    p.drawString(
        100,
        y,
        "Products:"
    )

    y -= 30

    for item in order.items.all():

        p.drawString(
            120,
            y,
            f"{item.product.name} x {item.quantity}"
        )

        y -= 20

    y -= 20

    p.drawString(
        100,
        y,
        f"Total: Rs {order.total_amount}"
    )

    p.save()

    return response
@login_required
def cancel_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status in ['Pending', 'Processing']:

        order.status = 'Cancelled'
        order.save()

        messages.success(
            request,
            'Order cancelled successfully.'
        )

    else:

        messages.error(
            request,
            'This order cannot be cancelled.'
        )

    return redirect('my_orders')