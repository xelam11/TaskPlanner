from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import Board


class BoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'author', 'participants')

    def get_author(self, board):
        return CustomUserSerializer(board.author).data
