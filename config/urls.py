from django.contrib import admin
from django.urls import path, include

from dashboard.views import home

from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from accounts.views import custom_login, custom_logout


urlpatterns = [

    # ======================================================
    # ADMIN
    # ======================================================

    path(
        "admin/",
        admin.site.urls
    ),

    # ======================================================
    # GOOGLE / SOCIAL LOGIN
    # ======================================================

    path(
        "accounts/social/",
        include("allauth.urls")
    ),

    # ======================================================
    # HOME
    # ======================================================

    path(
        "",
        home,
        name="home"
    ),

    # ======================================================
    # PRODUCTS
    # ======================================================

    path(
        "products/",
        include("products.urls")
    ),

    # ======================================================
    # CART
    # ======================================================

    path(
        "cart/",
        include("cart.urls")
    ),

    # ======================================================
    # ORDERS
    # ======================================================

    path(
        "orders/",
        include("orders.urls")
    ),

    # ======================================================
    # WISHLIST
    # ======================================================

    path(
        "wishlist/",
        include("wishlist.urls")
    ),

    # ======================================================
    # PRINTING
    # ======================================================

    path(
        "printing/",
        include("printing.urls")
    ),

    # ======================================================
    # ACCOUNTS
    # ======================================================

    path(
        "accounts/",
        include("accounts.urls")
    ),

    # ======================================================
    # LOGOUT
    # ======================================================

    path(
        "logout/",
        custom_logout,
        name="logout"
    ),

    # ======================================================
    # TEST
    # ======================================================

    path(
        "test/",
        home
    ),

    # ======================================================
    # PASSWORD RESET
    # ======================================================

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="registration/password_reset_email.html",
            html_email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset"
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm"
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),

    # ======================================================
    # LOGIN
    # ======================================================

    path(
        "login/",
        custom_login,
        name="login"
    ),
]


# ==========================================================
# MEDIA FILES
# ==========================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )