from rest_framework import serializers

from .models import *


class ExpertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expertises
        fields = "__all__"

class RequestSerializer(serializers.ModelSerializer):
    expertise = ExpertiseSerializer(read_only=True, many=True)

    class Meta:
        model = Requests
        fields = "__all__"

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'name')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            name=validated_data['name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)