from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings

import jwt
import datetime


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
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
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=360),
            'iat': datetime.datetime.now(datetime.UTC)
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        user.last_login = datetime.datetime.now(datetime.UTC)
        user.save()

        return Response({
            'message': 'login success',
            'jwt': token
        })


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
        response.data = {
            'message': 'logout success'
        }

        return response


class UserViewApi(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        serializer = UserSerializer(User.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

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
    def get_object(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_object(user_id)

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        if user is None:
            return Response(status=status.HTTP_204_NO_CONTENT, data={'error': 'User not found'})

        serializer = UserSerializer(user)

        response = {
            'message': f'User {user_id}',
            'data': serializer.data
        }

        return Response(status=status.HTTP_200_OK, data=response)

    def put(self, request, id):
        user = self.get_object(id)

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        if user is None:
            return Response(status=status.HTTP_204_NO_CONTENT, data={'error': 'User not found'})

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            phone_number = request.data.get('phone', None)
            if phone_number:
                if len(phone_number) < 10 or len(phone_number) > 13:
                    raise ValidationError({'error': 'Phone number must be greater than 10 and lesser than 13'})

            user_image = request.FILES.get('user_image', None)
            if user_image:
                if user.user_image:
                    if default_storage.exists(user.user_image.path):
                        default_storage.delete(user.user_image.path)

                user.user_image = user_image

            serializer.save()

            response = {
                'message': f'User {id} updated successfully',
                'data': serializer.data
            }

            return Response(status=status.HTTP_200_OK, data=response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = self.get_object(id)

        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        if user is None:
            return Response(status=status.HTTP_204_NO_CONTENT, data={'error': 'User not found'})

        if user.user_image and default_storage.exists(user.user_image.path):
            default_storage.delete(user.user_image.path)

        user.delete()

        response = {
            'message': f'User {id} deleted'
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
