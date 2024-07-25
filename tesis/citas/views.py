from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Citas
from .serializers import CitasSerializer
from tesis.users.models import User

from rest_framework.permissions import IsAuthenticated

import jwt
import datetime


# Create your views here.
class CitasAllView(APIView):

    def get(self, request):
        serializer = CitasSerializer(Citas.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CitasListView(APIView):
    def get(self, request):
        """
        if hasattr(request, 'usuario'):
            citas = Citas.objects.filter(paciente=request.usuario.id)
            serializer = CitasSerializer(citas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        """
        user_id = request.session.get('user_id')

        if user_id is None:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(id=user_id).first()

        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        citas = Citas.objects.filter(paciente=user_id)
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CitasCreateView(APIView):
    def post(self, request):
        """
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        serializer = CitasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(paciente=user)

        response = {
            'message': 'Appointment created successfully',
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)
        """
        user_id = request.session.get('user_id')

        if user_id is None:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(id=user_id).first()

        if user is None:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Crea el serializador con los datos de la solicitud
        serializer = CitasSerializer(data=request.data)
        if serializer.is_valid():
            # Asigna el paciente al usuario autenticado
            serializer.save(paciente=user)
            response = {
                'message': 'Appointment created successfully',
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CitasDetailView(APIView):
    def get_object(self, id):
        try:
            return Citas.objects.get(pk=id)
        except Citas.DoesNotExist:
            return None

    def get(self, request, id):
        cita = self.get_object(id)

        if cita is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found'})

        serializer = CitasSerializer(cita)
        response = {
            'message': f'Cita {id}',
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, id):
        """
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        cita = self.get_object(id)

        if cita is None or cita.paciente.id != payload['id']:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found'})

        serializer = CitasSerializer(cita, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                'message': f'Cita {id} updated successfully',
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        """
        cita = self.get_object(id)
        if cita is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found'})

        serializer = CitasSerializer(cita, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                'message': f'Cita {id} updated successfully',
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        cita = self.get_object(id)

        if cita is None or cita.paciente.id != payload['id']:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found'})

        cita.delete()
        response = {
            'message': f'Cita {id} deleted successfully',
        }
        return Response(response, status=status.HTTP_200_OK)
        """
        cita = self.get_object(id)
        if cita is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found'})

        cita.delete()
        response = {
            'message': f'Cita {id} deleted successfully',
        }
        return Response(response, status=status.HTTP_200_OK)
