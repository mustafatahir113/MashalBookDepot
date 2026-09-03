from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import logout
from django.contrib.messages import get_messages

import random
from datetime import timedelta

from django.utils import timezone

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)
from django.utils.encoding import force_bytes

from .forms import RegisterForm, ProfileUpdateForm
from .models import CustomUser


User = get_user_model()


# ==========================================================
# Register
# ==========================================================

def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # Account remains inactive until email verification
            user.is_active = False
            user.email_verified = False

            user.save()

            # --------------------------------------------------
            # Create verification UID and token
            # --------------------------------------------------

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(user)

            verification_link = (
                f"http://127.0.0.1:8000/"
                f"accounts/verify/{uid}/{token}/"
            )

            # --------------------------------------------------
            # Email content
            # --------------------------------------------------

            email_subject = (
                "Mashal Book Depot - Verify Your Email"
            )

            email_text = f"""
Welcome to Mashal Book Depot.

Thank you for creating your account.

Please verify your email by opening the link below:

{verification_link}

If you did not create this account, you can safely ignore this email.

Mashal Book Depot
"""

            # --------------------------------------------------
            # Beautiful HTML email
            # --------------------------------------------------

            email_html = render_to_string(
                "accounts/email_verification.html",
                {
                    "verification_link": verification_link,
                }
            )

            # --------------------------------------------------
            # Send HTML + plain text email
            # --------------------------------------------------

            email = EmailMultiAlternatives(
                subject=email_subject,
                body=email_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )

            email.attach_alternative(
                email_html,
                "text/html"
            )

            email.send(
                fail_silently=False
            )

            # --------------------------------------------------
            # Show verification sent page
            # --------------------------------------------------

            return render(
                request,
                "verification_sent.html",
                {
                    "email": user.email
                }
            )

    else:

        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


# ==========================================================
# Verify Email
# ==========================================================

def verify_email(request, uidb64, token):

    try:

        uid = urlsafe_base64_decode(
            uidb64
        ).decode()

        user = CustomUser.objects.get(
            pk=uid
        )

    except Exception:

        user = None

    if user and default_token_generator.check_token(
        user,
        token
    ):

        user.is_active = True
        user.email_verified = True

        user.save(
            update_fields=[
                "is_active",
                "email_verified"
            ]
        )

        messages.success(
            request,
            "Email verified successfully. Please login."
        )

        return redirect("login")

    messages.error(
        request,
        "Verification link is invalid or expired."
    )

    return render(
        request,
        "invalid_verification.html"
    )


# ==========================================================
# Login
# Username OR Email
# ==========================================================

def custom_login(request):

    if request.user.is_authenticated:

        return redirect("home")

    if request.method == "POST":

        identifier = request.POST.get(
            "identifier",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # --------------------------------------------------
        # Empty field validation
        # --------------------------------------------------

        if not identifier and not password:

            messages.error(
                request,
                "Please enter your username/email and password."
            )

            return render(
                request,
                "registration/login.html"
            )

        if not identifier:

            messages.error(
                request,
                "Please enter your username or email."
            )

            return render(
                request,
                "registration/login.html"
            )

        if not password:

            messages.error(
                request,
                "Please enter your password."
            )

            return render(
                request,
                "registration/login.html"
            )

        # --------------------------------------------------
        # Find account by username OR email
        # --------------------------------------------------

        user = User.objects.filter(
            Q(username__iexact=identifier) |
            Q(email__iexact=identifier)
        ).first()

        # --------------------------------------------------
        # Account not found
        # --------------------------------------------------

        if user is None:

            messages.error(
                request,
                "Invalid username/email or password."
            )

            return render(
                request,
                "registration/login.html"
            )

        # --------------------------------------------------
        # Password check
        # --------------------------------------------------

        if not user.check_password(password):

            messages.error(
                request,
                "Invalid username/email or password."
            )

            return render(
                request,
                "registration/login.html"
            )

        # --------------------------------------------------
        # Email verification check
        # --------------------------------------------------

        if not user.email_verified:

            messages.error(
                request,
                "Please verify your email before logging in."
            )

            return render(
                request,
                "registration/login.html"
            )

        # --------------------------------------------------
        # Account active check
        # --------------------------------------------------

        if not user.is_active:

            messages.error(
                request,
                "Your account is inactive. Please contact support."
            )

            return render(
                request,
                "registration/login.html"
            )

        # --------------------------------------------------
        # Login successful
        # --------------------------------------------------

        login(
            request,
            user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

        return redirect("home")

    return render(
        request,
        "registration/login.html"
    )


# ==========================================================
# Profile
# ==========================================================

@login_required
def profile(request):

    return render(
        request,
        "profile.html",
        {
            "user": request.user
        }
    )


# ==========================================================
# Edit Profile
# ==========================================================

@login_required
def edit_profile(request):

    if request.method == "POST":

        form = ProfileUpdateForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect(
                "profile"
            )

    else:

        form = ProfileUpdateForm(
            instance=request.user
        )

    return render(
        request,
        "edit_profile.html",
        {
            "form": form
        }
    )


# ==========================================================
# Logout
# ==========================================================

def custom_logout(request):

    # ------------------------------------------------------
    # Clear all pending Django messages
    # ------------------------------------------------------

    storage = get_messages(request)

    for message in storage:
        pass

    # ------------------------------------------------------
    # Logout user
    # ------------------------------------------------------

    logout(request)

    # ------------------------------------------------------
    # Go to login page
    # ------------------------------------------------------

    return redirect("login")