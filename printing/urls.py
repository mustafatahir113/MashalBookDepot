from django.urls import path

from .views import (
    create_printing_order,
    printing_order_success,
)


urlpatterns = [

    # ======================================================
    # CREATE PRINTING ORDER
    # ======================================================

    path(
        "",
        create_printing_order,
        name="create_printing_order"
    ),

    # ======================================================
    # PRINTING ORDER SUCCESS
    # ======================================================

    path(
        "success/<int:order_id>/",
        printing_order_success,
        name="printing_order_success"
    ),

]