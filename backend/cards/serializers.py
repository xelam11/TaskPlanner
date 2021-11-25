from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Card, FileInCard, Comment, CheckList
from boards.models import Tag
from boards.tag_serializer import TagSerializer
from users.serializers import CustomUserSerializer


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
    tags = TagSerializer(many=True)
    files = FileInCardSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    participants = CustomUserSerializer(many=True, read_only=True)
    check_lists = CheckListSerializer(many=True, read_only=True)
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ('id', 'name', 'description', 'list', 'position', 'tags',
                  'is_participant', 'participants', 'files', 'comments',
                  'check_lists')
        read_only_fields = ('list', 'position')

    def get_is_participant(self, card):
        request = self.context.get('request')
        user = request.user

        if request is None or request.user.is_anonymous:
            return False

        return card.participants.filter(id=user.id).exists()


class CardListOrCreateSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ('id', 'name', 'is_participant', 'position', 'list',
                  'participants', 'tags', 'files', 'comments', 'check_lists')
        read_only_fields = ('position', 'files', 'comments', 'check_lists')

    def get_is_participant(self, card):
        request = self.context.get('request')
        user = request.user

        if request is None or request.user.is_anonymous:
            return False

        return card.participants.filter(id=user.id).exists()


class AddOrRemoveParticipantInCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        card = get_object_or_404(Card, id=self.context.get('card_id'))
        user_id = validated_data['id']
        card.participants.add(user_id)

        return card

    def validate_id(self, id_):
        card = get_object_or_404(Card, id=self.context.get('card_id'))
        board = card.list.board

        if card.participants.filter(id=id_).exists():
            raise serializers.ValidationError({
                'status': 'error',
                'message':
                    'Данный пользователь уже является участником карточки!'
            })

        if not board.participants.filter(id=id_).exists():
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Данный пользователь не является участникм доски!'
            })

        return id_


class AddOrRemoveTagInCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        card = get_object_or_404(Card, id=self.context.get('card_id'))
        tag_id = validated_data['id']
        card.tags.add(tag_id)

        return card

    def validate_id(self, id_):
        card = get_object_or_404(Card, id=self.context.get('card_id'))
        board = card.list.board

        if not board.tags.filter(id=id_).exists():
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Такого тега нет в данной доске!'
            })

        if card.tags.filter(id=id_).exists():
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Такой тег уже применен в данной карточке!'
            })

        return id_


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ChangeListOfCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    position = serializers.IntegerField()


class SwapCardsSerializer(serializers.Serializer):
    card_1 = serializers.IntegerField()
    card_2 = serializers.IntegerField()


# class ParticipantInCardSerializer(serializers.Serializer):
#     id = serializers.IntegerField()