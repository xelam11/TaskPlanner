from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(max_length=None,
                                    allow_empty_file=True,
                                    allow_null=True,
                                    required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'bio', 'password',
                  'username', 'email', 'avatar', 'is_staff', 'created_at')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, data):
        return CustomUser.objects.create_user(**data)
