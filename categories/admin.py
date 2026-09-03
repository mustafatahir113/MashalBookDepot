from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):

    list_display = (
        'name',
    )

    search_fields = (
        'name',
    )

    ordering = (
        'name',
    )

    actions = [
        'delete_selected',
    ]