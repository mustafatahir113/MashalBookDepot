from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import PrintingOrderForm
from .models import PrintingOrder, PrintingFile


@login_required
def create_printing_order(request):

    if request.method == "POST":

        form = PrintingOrderForm(request.POST)

        uploaded_files = request.FILES.getlist("files")

        if form.is_valid():

            if not uploaded_files:

                form.add_error(
                    None,
                    "Kam az kam 1 file upload karna zaroori hai."
                )

            else:

                copies = form.cleaned_data["copies"]
                side = form.cleaned_data["side"]
                print_type = form.cleaned_data["print_type"]

                # =============================================
                # PRICE CALCULATION
                # =============================================

                if print_type == "color":

                    price_per_page = Decimal("40")

                else:

                    if copies <= 10:

                        price_per_page = Decimal("20")

                    else:

                        price_per_page = Decimal("15")

                # =============================================
                # TOTAL PRICE
                # =============================================

                calculated_price = (
                    price_per_page * Decimal(copies)
                )

                # =============================================
                # CREATE PRINTING ORDER
                # =============================================

                with transaction.atomic():

                    printing_order = form.save(
                        commit=False
                    )

                    printing_order.user = request.user

                    printing_order.calculated_price = (
                        calculated_price
                    )

                    printing_order.final_price = (
                        calculated_price
                    )

                    printing_order.save()

                    # =========================================
                    # SAVE UPLOADED FILES
                    # =========================================

                    for uploaded_file in uploaded_files:

                        PrintingFile.objects.create(
                            order=printing_order,
                            file=uploaded_file
                        )

                # =============================================
                # REDIRECT TO SUCCESS PAGE
                # =============================================

                return redirect(
                    "printing_order_success",
                    order_id=printing_order.id
                )

    else:

        form = PrintingOrderForm()

    return render(
        request,
        "printing/create_order.html",
        {
            "form": form,
        }
    )


# ==========================================================
# PRINTING ORDER SUCCESS
# ==========================================================

@login_required
def printing_order_success(request, order_id):

    printing_order = get_object_or_404(
        PrintingOrder,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "printing/order_success.html",
        {
            "printing_order": printing_order,
        }
    )