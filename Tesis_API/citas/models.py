from django.db import models
from users.models import User


# Create your models here.
class Citas(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas')
    date = models.DateTimeField()
    description = models.TextField()
