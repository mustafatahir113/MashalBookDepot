from django.conf import settings
from django.db import models


class PrintingOrder(models.Model):

    SIDE_CHOICES = [
        ("single", "Single Side"),
        ("double", "Double Side"),
    ]

    PRINT_TYPE_CHOICES = [
        ("bw", "Black & White"),
        ("color", "Color"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    description = models.TextField(
        blank=True
    )

    copies = models.PositiveIntegerField(
        default=1
    )

    side = models.CharField(
        max_length=10,
        choices=SIDE_CHOICES,
        default="single"
    )

    print_type = models.CharField(
        max_length=10,
        choices=PRINT_TYPE_CHOICES,
        default="bw"
    )

    calculated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Printing Order #{self.id} - {self.user}"



class PrintingFile(models.Model):

    order = models.ForeignKey(
        PrintingOrder,
        on_delete=models.CASCADE,
        related_name="files"
    )

    file = models.FileField(
        upload_to="printing/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"File for Printing Order #{self.order.id}"