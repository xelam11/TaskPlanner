from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Request
from boards.models import Board, ParticipantInBoard
from boards.serializers import BoardListOrCreateSerializer
from users.models import CustomUser
from users.serializers import CustomUserSerializer


class BoardRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Request
        fields = ('id', 'board', 'user')
        read_only_fields = ('board', )


class SendRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        board = get_object_or_404(Board, id=self.context.get('board_id'))
        user = get_object_or_404(CustomUser, email=validated_data.get('email'))
        Request.objects.create(board=board, user=user)
        return user

    def validate_email(self, email):
        board = get_object_or_404(Board, id=self.context.get('board_id'))
        user = get_object_or_404(CustomUser, email=email)
        request = self.context.get('request')

        if user == request.user:
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Вы не можете отправить запрос самому себе!'
            })

        if ParticipantInBoard.objects.filter(board=board,
                                             participant=user).exists():
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Данный пользователь уже является участником доски'
            })

        if Request.objects.filter(board=board, user=user).exists():
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Вы уже отправили запрос данному пользователю!'
            })

        return email


class UserRequestSerializer(serializers.ModelSerializer):
    board = BoardListOrCreateSerializer(read_only=True)

    class Meta:
        model = Request
        fields = ('id', 'board', 'user')
        read_only_fields = ('user', )
