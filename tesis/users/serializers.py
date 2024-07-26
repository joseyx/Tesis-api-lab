from rest_framework import serializers
from .models import User
from .validators import validate_image_file_extension

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework.exceptions import AuthenticationFailed


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    user_image = serializers.ImageField(validators=[validate_image_file_extension], required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'phone', 'user_image']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        if password is not None:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


"""
    def validate(self, attrs):
        email = attrs['data'].get('email', '')
        

        return super().validate(attrs)
"""


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=20, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)