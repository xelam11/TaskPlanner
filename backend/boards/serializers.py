from rest_framework import serializers

from .models import Board, Favorite, ParticipantInBoard
from .tag_serializer import TagSerializer
from lists.serializers import ListSerializer
from users.serializers import CustomUserSerializer


class BoardSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(max_length=None,
                                    allow_empty_file=True,
                                    allow_null=True,
                                    required=False)
    author = serializers.SerializerMethodField(read_only=True)
    lists = ListSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favored = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'avatar', 'author',
                  'is_favored', 'participants', 'lists', 'tags')
        read_only_fields = ('participants', )

    def get_author(self, board):
        return CustomUserSerializer(board.author).data

    def get_is_favored(self, board):
        request = self.context.get('request')
        user = request.user

        if request is None or request.user.is_anonymous:
            return False

        return Favorite.objects.filter(board=board, user=user).exists()


class BoardListOrCreateSerializer(serializers.ModelSerializer):
    is_favored = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'avatar', 'is_favored', 'is_author',
                  'is_participant')

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

    def create(self, validated_data):
        current_user = self.context.get('request').user

        board = Board.objects.create_board(author=current_user,
                                           **validated_data)

        return board


class ParticipantInBoardSerializer(serializers.ModelSerializer):
    participant = CustomUserSerializer(read_only=True)

    class Meta:
        model = ParticipantInBoard
        fields = ('id', 'board', 'participant', 'is_moderator')


class SwitchModeratorSerializer(serializers.Serializer):
    id = serializers.IntegerField()
