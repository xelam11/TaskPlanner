from rest_framework import serializers

from users.serializers import CustomUserSerializer

from .models import (Board, List, Favorite, ParticipantRequest,
                     ParticipantInBoard, Tag, TagInBoard, Card)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')


class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = ('id', 'name', 'description', 'list', 'position',
                  'participants', 'files')
        read_only_fields = ('list', 'position')

    def validate(self, data):
        participants = data.get('participants')

        if participants is None:
            return data

        card = Card.objects.get(id=self.context['card_id'])
        board = card.list.board

        for participant in participants:
            if not board.participants.filter(id=participant.id).exists():
                msg = f"Пользователя '{participant}' нельзя добавить в " \
                      f"карточку, т.к. он не является участником доски!"
                raise serializers.ValidationError(msg)

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        participants_data = CustomUserSerializer(
            instance.participants.all(), many=True).data

        return {**data, 'participants': participants_data}


class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ('id', 'name', 'board', 'position', 'cards')
        read_only_fields = ('board', 'position')


class ParticipantInBoardSerializer(serializers.ModelSerializer):
    participant = CustomUserSerializer(read_only=True)

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

        board = Board.objects.create(author=current_user, **validated_data)
        board.participants.add(current_user)

        participant_in_board = ParticipantInBoard.objects.get(
            board=board,
            participant=current_user)
        participant_in_board.is_moderator = True
        participant_in_board.save()

        for tag in Tag.objects.all():
            TagInBoard.objects.create(board=board, tag=tag)

        return board
