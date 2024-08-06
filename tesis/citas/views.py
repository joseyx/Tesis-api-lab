from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.core.files.storage import default_storage
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Citas
from .serializers import CitasSerializer
from tesis.users.models import User

from django.template.loader import render_to_string

from datetime import datetime
from django.utils.dateformat import format
from django.utils.translation import gettext as _

from babel.dates import format_datetime

from rest_framework.permissions import IsAuthenticated

from .utils import Util

import jwt
import datetime


# Create your views here.
class CitasAllView(APIView):

    def get(self, request):
        serializer = CitasSerializer(Citas.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CitasListView(APIView):
    def get(self, request):
        # token = request.COOKIES.get('jwt')
        #
        # if not token:
        #     raise AuthenticationFailed('Unauthenticated')
        #
        # try:
        #     payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        # except jwt.ExpiredSignatureError:
        #     raise AuthenticationFailed('Unauthenticated')
        if not hasattr(request, 'usuario'):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        citas = Citas.objects.filter(paciente_id=request.usuario.id).order_by('date')
        serializer = CitasSerializer(citas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CitasCreateView(APIView):
    def post(self, request):
        if not hasattr(request, 'usuario'):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(id=request.usuario.id).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        serializer = CitasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cita = serializer.save(paciente=user)

        fecha_formateada = format_datetime(cita.date, format='EEEE, d MMMM yyyy, H:mm:ss', locale='es_ES')

        absurl = 'http://localhost:4200/perfil'
        #email_body = (f'Hola {user.name}, este es un mensaje para confirmarte que tu '
                      #f'cita ha sido agendada con exito!\nPuedes revisarla aquí {absurl}')
        user_name = user.name.capitalize()

        context = {
            'user': user,
            'perfil': absurl,
            'user_name': user_name,
            'cita': serializer.data,
            'fecha_formateada': fecha_formateada
        }
        html_message = render_to_string("cita-confirmation.html", context)
        data = {
            'email_body': html_message,
            'to_email': [user.email],
            'email_subject': 'Cita agendada'
        }

        try:
            Util.send_email(data)
            return Response(
                {'success': 'Se ha enviado a su correo la confirmación de la cita'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Error al enviar el correo electrónico'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CitasDetailView(APIView):
    def get_object(self, id):
        try:
            return Citas.objects.get(pk=id)
        except Citas.DoesNotExist:
            return None

    def get(self, request, id):
        if not hasattr(request, 'usuario'):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        cita = self.get_object(id)

        if cita is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found'})

        serializer = CitasSerializer(cita)
        response = {
            'message': f'Cita {id}',
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    def patch(self, request, id):
        cita = self.get_object(id)
        data = request.data.copy()

        serializer = CitasSerializer(cita, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = {
                'message': f'Cita {id} updated successfully',
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        if not hasattr(request, 'usuario'):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        cita = self.get_object(id)

        # Verificar si el usuario es administrador o la cita pertenece al usuario
        if cita is None or (cita.paciente.id != request.usuario.id and not request.usuario.role == 'admin'):
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Cita not found or not authorized'})

        cita.delete()
        response = {
            'message': f'Cita {id} deleted successfully',
        }
        return Response(response, status=status.HTTP_200_OK)
