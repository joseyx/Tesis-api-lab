from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.template.loader import render_to_string

import jwt
import datetime


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            email = serializer.validated_data['email']
            absurl = f'http://localhost:4200/login'
            user = User.objects.get(email=email)

            context = {
                'user': user,
                'login': absurl,
            }
            html_message = render_to_string("welcome.html", context)
            data = {
                'email_body': html_message,
                'to_email': [user.email],
                'email_subject': 'Mensaje de Bienvenida'
            }
            try:
                Util.send_email(data)
                return Response(
                    {
                        'success': 'Se ha enviado el mensaje de bienvenida',
                        'data': serializer.data
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                print(f'Error sending email: {e}')
                return Response(
                    {'error': 'Error al enviar el correo electrónico'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except ValidationError as e:
            if 'email' in e.detail:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'error': 'Email already in use'}
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=e.detail)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            raise AuthenticationFailed('Email and password are required')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'iat': datetime.datetime.now(datetime.UTC)
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        user.last_login = datetime.datetime.now(datetime.UTC)
        user.save()

        response = Response({
            'message': 'login success',
            'jwt': token
        })
        response.set_cookie('jwt', token, httponly=True)
        request.session['user_id'] = user.id
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        request.session.flush()
        response.data = {
            'message': 'logout success'
        }

        return response


class RequestPasswordResetEmail(APIView):
    def post(self, request):
        serializer = ResetPasswordEmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            # current_site = get_current_site(request=request).domain
            # relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = f'http://localhost:4200/reestablecer-clave/{uidb64}/{token}'
            #email_body = f'Hola {user.name},\nUsa este link para reestablecer tu contraseña {absurl}'
            user_name = user.name.capitalize()

            context = {
                'user': user,
                'reset_link': absurl,
                'user_name': user_name
            }
            html_message = render_to_string("reset-password.html", context)
            data = {
                'email_body': html_message,
                'to_email': [user.email],
                'email_subject': 'Reestablecer contraseña'
            }
            try:
                Util.send_email(data)
                return Response(
                    {'success': 'Se ha enviado el link para reestablecer tu contraseña'},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                print(f'Error sending email: {e}')
                return Response(
                    {'error': 'Error al enviar el correo electrónico'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {'error': 'Email not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class PasswordTokenCheck(APIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({
                'success': True,
                'message': 'Credentials valid',
                'uidb64': uidb64,
                'token': token
            }, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({'error': 'Token is not valid, please request a new one'},
                            status=status.HTTP_401_UNAUTHORIZED)


class SetNewPassword(APIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            print('Serializer is valid.')
            return Response(
                {'success': True, 'message': 'Password reset success'
                 }, status=status.HTTP_200_OK)
        else:
            print('Serializer is invalid.')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewApi(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request):
        request.data['role'] = 'cliente'
        serializer = UserSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            if 'email' in e.detail:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'error': 'Email already in use'}
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=e.detail)

        serializer.save()
        response = {
            'message': 'User created successfully',
            'data': serializer.data
        }

        return Response(status=status.HTTP_200_OK, data=response)


class UserViewApiDetail(APIView):
    def get_object(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_object(user_id)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'User not found'})
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        user = self.get_object(user_id)
        data = request.data.copy()  # Hace una copia de los datos

        data.pop('user_image', None)  # Elimina el campo user_image si no está presente o es nulo

        serializer = UserSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response = {
                'message': f'User {user_id} updated successfully',
                'data': serializer.data
            }
            return Response(status=status.HTTP_200_OK, data=response)

        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def delete(self, request, user_id):
        user = self.get_object(user_id)

        if user is None:
            return Response(status=status.HTTP_204_NO_CONTENT, data={'error': 'User not found'})

        if user.user_image and default_storage.exists(user.user_image.path):
            default_storage.delete(user.user_image.path)

        user.delete()

        response = {
            'message': f'User {user_id} deleted'
        }

        return Response(status=status.HTTP_200_OK, data=response)


class UsuarioView(APIView):

    def get(self, request):
        if hasattr(request, 'usuario'):
            user = User.objects.get(id=request.usuario.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class ProtectedView(APIView):

    def get(self, request):
        if not hasattr(request, 'usuario'):
            return Response({'error': 'Unauthenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.usuario
        return Response({'message': f'Hello, {user.email}'})
