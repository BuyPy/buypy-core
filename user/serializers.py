from rest_framework.serializers import ModelSerializer

from user.models import User


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}, "id": {"read_only": True}}


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "date_joined", "last_login")
