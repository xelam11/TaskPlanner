from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'bio',
                  'username', 'email', 'password', 'created_at')

    def validate_password(self, password):
        return make_password(password)
