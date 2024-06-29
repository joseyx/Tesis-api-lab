import jwt

from tesis.users.models import User
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload['id']
                request.usuario = User.objects.get(id=user_id)

            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Token is expired')
            except jwt.InvalidTokenError:
                raise AuthenticationFailed('Invalid token')
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found')

        response = self.get_response(request)
        return response
