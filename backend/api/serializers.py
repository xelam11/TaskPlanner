from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import Board, List, Favorite


class ListSerializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = ('id', 'name', 'board', 'position')


class BoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    lists = ListSerializer(many=True)
    is_favored = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'author', 'is_favored',
                  'is_author', 'is_participant', 'participants', 'lists')
        read_only_fields = ('lists', )

    def get_author(self, board):
        return CustomUserSerializer(board.author).data

    def get_is_favored(self, board):
        request = self.context.get('request')
        user = request.user

        if request is None or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(board=board, user=user).exists()

    def get_is_author(self, board):
        request = self.context.get('request')
        user = request.user
        if request is None or request.user.is_anonymous:
            return False

        return bool(board.author == user)

    def get_is_participant(self, board):
        request = self.context.get('request')
        user = request.user

        if request is None or request.user.is_anonymous:
            return False

        return board.participants.filter(id=user.id).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        participants_data = CustomUserSerializer(instance.participants.all(),
                                                 many=True,
                                                 read_only=True).data

        return {**data, 'participants': participants_data}
