from django.urls import path

from .views import (
    register,
    profile,
    edit_profile,
    verify_email,
    custom_login,
    custom_logout,
)


urlpatterns = [

    path(
        'register/',
        register,
        name='register'
    ),

    path(
        'profile/',
        profile,
        name='profile'
    ),

    path(
        'edit-profile/',
        edit_profile,
        name='edit_profile'
    ),

    path(
        'custom-login/',
        custom_login,
        name='custom_login'
    ),

    path(
        'verify/<uidb64>/<token>/',
        verify_email,
        name='verify_email'
    ),

    path(
        'logout/',
        custom_logout,
        name='custom_logout'
    ),
]