from rest_framework import serializers
from .models import Citas
from users.serializers import SimpleUserSerializer


class CitasSerializer(serializers.ModelSerializer):
    paciente = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Citas
        fields = '__all__'
        read_only_fields = ['paciente']
