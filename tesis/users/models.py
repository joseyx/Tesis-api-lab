from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ('cliente', 'User'),
        ('admin', 'Administrator'),
        ('médico', 'Médico')
        # Add more roles as needed
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    username = None

    phone = models.CharField(max_length=13, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='cliente')
    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True, default='default_user_image.png')

    updated_at = models.DateTimeField(auto_now=True)

    # New: related_name for ManyToMany fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='tesis_user_groups',  # Custom related_name for groups
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='tesis_user_permissions',  # Custom related_name for permissions
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
