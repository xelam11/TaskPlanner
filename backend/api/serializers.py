from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin

from users.serializers import CustomUserSerializer

from .models import (Board, List, Favorite, ParticipantRequest,
                     ParticipantInBoard, Tag, TagInBoard)


# class ListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = List
#         fields = ('id', 'name', 'board', 'position')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')


class ListSerializer(BulkSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = List
        list_serializer_class = BulkListSerializer
        fields = ('id', 'name', 'board', 'position')


class ParticipantInBoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipantInBoard
        fields = ('id', 'board', 'participant', 'is_moderator')


class ParticipantRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParticipantRequest
        fields = ('id', 'board', 'participant')


class TagInBoardSerializer(serializers.ModelSerializer):

    class Meta:
        model = TagInBoard
        fields = ('id', 'tag', 'board', 'content')


class BoardSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    lists = ListSerializer(many=True, read_only=True)
    is_favored = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    is_participant = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'author', 'is_favored',
                  'is_author', 'is_participant', 'participants', 'lists',
                  'tags')
        read_only_fields = ('participants', )

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

        board = Board.objects.create(author=current_user, **validated_data)
        # board.save()
        board.participants.add(current_user)

        participant_in_board = ParticipantInBoard.objects.get(
            board=board,
            participant=current_user)
        participant_in_board.is_moderator = True
        participant_in_board.save()

        for tag in Tag.objects.all():
            TagInBoard.objects.create(board=board, tag=tag)

        return board

    def to_representation(self, instance):
        data = super().to_representation(instance)
        participants = instance.participantinboard_set.prefetch_related(
            'participant').all()
        tags = instance.taginboard_set.prefetch_related('tag').all()

        participants_data = [
            {
                **CustomUserSerializer(participant_in_board.participant).data,
                'is_moderator': participant_in_board.is_moderator
            } for participant_in_board in participants
        ]

        tags_data = [
            {
                **TagSerializer(tag_in_board.tag).data,
                'content': tag_in_board.content
            } for tag_in_board in tags
        ]

        return {**data, 'participants': participants_data, 'tags': tags_data}
