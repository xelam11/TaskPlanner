from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import (Board, List, Favorite, ParticipantRequest,
                     ParticipantInBoard, Card, FileInCard, Comment, CheckList)

from users.models import CustomUser


# class TagSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Tag
#         fields = ('id', 'name', 'color')

class CheckListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckList
        fields = ('id', 'text', 'card', 'is_active')
        read_only_fields = ('card', 'is_active')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'card', 'pub_date')
        read_only_fields = ('card', 'pub_date')

    def get_author(self, comment):
        return CustomUserSerializer(comment.author).data


class FileInCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileInCard
        fields = ('id', 'card', 'file')
        read_only_fields = ('card', )


class CardSerializer(serializers.ModelSerializer):
    files = FileInCardSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    participants = CustomUserSerializer(many=True, read_only=True)
    check_lists = CheckListSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = ('id', 'name', 'description', 'list', 'position',
                  'participants', 'files', 'comments', 'check_lists')
        read_only_fields = ('list', 'position')


class AddParticipantToCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, participant_id):
        participant = get_object_or_404(CustomUser, id=participant_id)
        card = get_object_or_404(Card, id=self.context['card_id'])
        board = card.list.board

        if card.participants.filter(id=participant.id).exists():
            msg = f"Пользователя '{participant}' нельзя добавить в "\
                  f"карточку, т.к. он уже является ее участником!"
            raise serializers.ValidationError(msg)

        if not board.participants.filter(id=participant.id).exists():
            msg = f"Пользователя '{participant}' нельзя добавить в " \
                  f"карточку, т.к. он не является участником доски!"
            raise serializers.ValidationError(msg)


class RemoveParticipantFromCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate_id(self, participant_id):
        participant = get_object_or_404(CustomUser, id=participant_id)
        card = get_object_or_404(Card, id=self.context['card_id'])

        if not card.participants.filter(id=participant.id).exists():
            msg = f"Пользователя '{participant}' нельзя удалить из "\
                  f"карточки, т.к. он не является ее участником!"
            raise serializers.ValidationError(msg)


class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ('id', 'name', 'board', 'position', 'cards')
        read_only_fields = ('board', 'position')


class SwapListsSerializer(serializers.Serializer):
    list_1 = serializers.IntegerField()
    list_2 = serializers.IntegerField()

    def validate(self, data):
        list_1 = get_object_or_404(List, id=data.get('list_1'))
        list_2 = get_object_or_404(List, id=data.get('list_2'))

        if list_1.board != list_2.board:
            msg = 'Нельзя менять местами листы из разных досок!'
            raise serializers.ValidationError(msg)

        return data


class ParticipantInBoardSerializer(serializers.ModelSerializer):
    participant = CustomUserSerializer(read_only=True)

    class Meta:
        model = ParticipantInBoard
        fields = ('id', 'board', 'participant', 'is_moderator')


class ParticipantRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipantRequest
        fields = ('id', 'board', 'participant')


# class TagInBoardSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = TagInBoard
#         fields = ('id', 'tag', 'board', 'content')


class BoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    lists = ListSerializer(many=True, read_only=True)
    is_favored = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'author', 'is_favored',
                  'is_author', 'is_participant', 'participants', 'lists')
        read_only_fields = ('participants', 'tags')

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

    def create(self, validated_data):
        current_user = self.context.get('request').user

        board = Board.objects.create_board(author=current_user,
                                           **validated_data)

        return board
