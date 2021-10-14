from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(max_length=None,
                                    allow_empty_file=True,
                                    allow_null=True,
                                    required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'bio',
                  'username', 'email', 'avatar', 'is_staff', 'created_at')
