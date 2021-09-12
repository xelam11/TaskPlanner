from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import Board, List


class ListSerializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = ('id', 'name', 'position')


class BoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'author', 'participants')

    def get_author(self, board):
        return CustomUserSerializer(board.author).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        participants_data = CustomUserSerializer(instance.participants.all(),
                                                 many=True,
                                                 read_only=True).data

        return {**data, 'participants': participants_data}
