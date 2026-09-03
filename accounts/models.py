from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('manager', 'Manager'),
    )
    GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
)

    gender = models.CharField(
    max_length=10,
    choices=GENDER_CHOICES,
    default='male'
)

    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(
    upload_to='profile_pics/',
    default='profile_pics/default.png',
    blank=True
)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    email_verified = models.BooleanField(
    default=False
)

    def __str__(self):
        return self.username