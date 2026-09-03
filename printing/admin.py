from django.contrib import admin

from .models import PrintingOrder, PrintingFile


class PrintingFileInline(admin.TabularInline):

    model = PrintingFile

    extra = 0

    readonly_fields = (
        "uploaded_at",
    )


@admin.register(PrintingOrder)
class PrintingOrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "copies",
        "side",
        "print_type",
        "calculated_price",
        "final_price",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "side",
        "print_type",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "description",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "user",
        "calculated_price",
        "created_at",
        "updated_at",
    )

    inlines = (
        PrintingFileInline,
    )


@admin.register(PrintingFile)
class PrintingFileAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "file",
        "uploaded_at",
    )

    list_filter = (
        "uploaded_at",
    )

    search_fields = (
        "order__user__username",
        "order__user__email",
    )

    ordering = (
        "-uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
    )