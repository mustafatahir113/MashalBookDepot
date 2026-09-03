from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Product,
    ProductImage,
    Review,
)


class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 3

    fields = [
        'image',
    ]

    show_change_link = True


@admin.register(Product)
class ProductAdmin(ModelAdmin):

    list_display = [
        'name',
        'category',
        'price',
        'discount_price',
        'stock',
        'average_rating',
        'total_reviews',
        'created_at',
    ]

    list_filter = [
        'category',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    list_editable = [
        'price',
        'discount_price',
        'stock',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    inlines = [
        ProductImageInline,
    ]

    ordering = [
        '-created_at',
    ]


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):

    list_display = [
        'product',
        'image',
        'created_at',
    ]

    list_filter = [
        'created_at',
    ]

    search_fields = [
        'product__name',
    ]


@admin.register(Review)
class ReviewAdmin(ModelAdmin):

    list_display = [
        'product',
        'user',
        'rating',
        'created_at',
    ]

    list_filter = [
        'rating',
        'created_at',
    ]

    search_fields = [
        'product__name',
        'user__username',
        'comment',
    ]

    readonly_fields = [
        'created_at',
    ]