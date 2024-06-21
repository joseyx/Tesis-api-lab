from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    username = None

    phone = models.CharField(max_length=13, null=True)
    role = models.CharField(default='user')

    updated_at = models.DateTimeField(auto_now=True)

    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
