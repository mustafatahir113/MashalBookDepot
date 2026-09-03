from django.urls import path

from .views import product_detail


urlpatterns = [

    path(
        '<int:pk>/',
        product_detail,
        name='product_detail'
    ),

]