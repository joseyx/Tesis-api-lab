from rest_framework import serializers
from .models import User
from .validators import validate_image_file_extension


class UserSerializer(serializers.ModelSerializer):
    user_image = serializers.ImageField(validators=[validate_image_file_extension], required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'phone', 'user_image', 'apt', 'apt_type', 'apt_results']
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
