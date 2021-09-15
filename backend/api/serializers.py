from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import Board, List, Favorite


class ListSerializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = ('id', 'name', 'position')


class BoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    is_favored = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'author', 'is_favored',
                  'participants')

    def get_author(self, board):
        return CustomUserSerializer(board.author).data

    def get_is_favored(self, board):
        request = self.context.get('request')
        user = request.user

        if request is None or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(board=board, user=user).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        participants_data = CustomUserSerializer(instance.participants.all(),
                                                 many=True,
                                                 read_only=True).data

        return {**data, 'participants': participants_data}
