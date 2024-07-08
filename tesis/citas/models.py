from django.db import models
from tesis.users.models import User


# Create your models here.
class Citas(models.Model):
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
    ]

    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas')
    medico = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas_medico', limit_choices_to={'role': 'medico'})
    date = models.DateTimeField()
    description = models.TextField()
    resultado = models.TextField(default='')
    estado = models.CharField(max_length=10, choices=ESTADOS_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.paciente.email} - {self.date}"
