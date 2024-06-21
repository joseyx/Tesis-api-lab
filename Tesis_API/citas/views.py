from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Citas
from .serializers import CitasSerializer
from users.models import User

import jwt
import datetime


# Create your views here.
class CitasAllView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        serializer = CitasSerializer(Citas.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CitasListView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        citas = Citas.objects.filter(paciente_id=payload['id'])
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CitasCreateView(APIView):
    def post(self, request):
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


class CitasDetailView(APIView):
    def get_object(self, id):
        try:
            return Citas.objects.get(pk=id)
        except Citas.DoesNotExist:
            return None

    def get(self, request, id):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

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

    def delete(self, request, id):
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