from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import CardFilter
from .models import Card, FileInCard, Comment, CheckList
from .permissions import (IsAuthor, IsParticipant, IsStaff,
                          IsAuthorOrParticipantOrAdminForCreateCard,
                          IsAuthorOrParticipantOrAdminForCommentAndCheckList,
                          IsAuthorOfComment)
from .serializers import (CardSerializer, CardListOrCreateSerializer,
                          FileInCardSerializer, CommentSerializer,
                          IdSerializer, CheckListSerializer,
                          ChangeListOfCardSerializer, SwapCardsSerializer)
from boards.models import Tag
from boards.tag_serializer import TagSerializer
from users.models import CustomUser
from lists.models import List


class CardViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, ]
    filter_class = CardFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Card.objects.all()

        return Card.objects.filter(
            list__board__participants__id=self.request.user.id)

    def get_serializer_class(self):

        if self.action in ('list', 'create'):
            return CardListOrCreateSerializer

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return CardSerializer

    def perform_create(self, serializer):
        list_ = get_object_or_404(List, id=self.request.data['list'])
        count_of_cards = list_.cards.count()
        serializer.save(list=list_,
                        position=count_of_cards + 1)

    def perform_destroy(self, instance):
        position = instance.position
        queryset_of_cards = instance.list.cards

        for card in queryset_of_cards.all()[position:]:
            card.position -= 1
            card.save()

        instance.delete()

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]

        if self.action == 'create':
            return [IsAuthorOrParticipantOrAdminForCreateCard()]

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy',
                           'change_list', 'swap', 'tag', 'file',
                           'participant'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

    @action(detail=True, methods=['post'])
    def change_list(self, request, **kwargs):
        serializer = ChangeListOfCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card = get_object_or_404(Card, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, card)

        new_list_id = request.data['id']
        new_list = get_object_or_404(List, id=new_list_id)
        new_position = request.data['position']

        if card.list.board != new_list.board:
            return Response({
                'status': 'error',
                'message':
                    'Нельзя переместить карточку в лист из другой доски!'},
                status=status.HTTP_400_BAD_REQUEST)

        if new_position < 1:
            return Response({
                'status': 'error',
                'message':
                    "Значение поля 'position' не может быть меньше 1!"},
                status=status.HTTP_400_BAD_REQUEST)

        if new_position > new_list.cards.count() + 1:
            return Response({
                'status': 'error',
                'message': "Значение поля 'position' не может "
                           "превышать количество карточек в новом списке!"},
                status=status.HTTP_400_BAD_REQUEST)

        for card_ in new_list.cards.all()[new_position - 1:]:
            card_.position += 1
            card_.save()

        for card__ in card.list.cards.all()[new_position:]:
            card__.position -= 1
            card__.save()

        card.list, card.position = new_list, new_position
        card.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def swap(self, request, **kwargs):
        serializer = SwapCardsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_1 = get_object_or_404(Card, id=request.data['card_1'])
        card_2 = get_object_or_404(Card, id=request.data['card_2'])
        self.check_object_permissions(self.request, card_1)

        if card_1 == card_2:
            return Response({
                'status': 'error',
                'message': 'Нельзя менять местами карточку с самой собой!'},
                status=status.HTTP_400_BAD_REQUEST)

        if card_1.list != card_2.list:
            return Response({
                'status': 'error',
                'message':
                    'Нельзя менять местами карточки из разных листов!'},
                status=status.HTTP_400_BAD_REQUEST)

        card_1.position, card_2.position = card_2.position, card_1.position
        card_1.save()
        card_2.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def tag(self, request, **kwargs):
        serializer = IdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card = get_object_or_404(Card, id=kwargs.get('pk'))
        board = card.list.board
        tag = get_object_or_404(Tag, id=request.data['id'])
        self.check_object_permissions(self.request, card)

        if not board.tags.filter(id=request.data['id']).exists():
            return Response({
                'status': 'error',
                'message': 'Такого тега нет в данной доске!'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            card.tags.add(tag)
            serializer = TagSerializer(card.tags.all(), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            card.tags.remove(tag)
            serializer = TagSerializer(card.tags.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def file(self, request, **kwargs):
        card = get_object_or_404(Card, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, card)

        if request.method == 'POST':
            serializer = FileInCardSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            file = self.request.data['file']
            FileInCard.objects.create(card=card, file=file)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            file_in_card = get_object_or_404(FileInCard,
                                             id=self.request.data['id']
                                             )
            file_in_card.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def participant(self, request, **kwargs):
        # serializer = ParticipantInCardSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        card = get_object_or_404(Card, id=kwargs.get('pk'))
        board = card.list.board
        self.check_object_permissions(self.request, card)
        participant = get_object_or_404(CustomUser, id=request.data['id'])

        if request.method == 'POST':

            if card.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message':
                        'Данный пользователь уже является участником карточки!'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not board.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message':
                        'Данный пользователь не является участникм доски!'},
                    status=status.HTTP_400_BAD_REQUEST)

            card.participants.add(participant)
            return Response(status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if not card.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message':
                        'Данный пользователь не является участникм карточки!'},
                    status=status.HTTP_400_BAD_REQUEST)

            card.participants.remove(participant)

            return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        user = self.request.user
        card = get_object_or_404(Card, id=self.kwargs.get('card_id'))

        if user.is_superuser or user.is_staff:
            return Comment.objects.all()

        return card.comments

    def perform_create(self, serializer):
        card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        serializer.save(author=self.request.user, card=card)

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthorOrParticipantOrAdminForCommentAndCheckList()]

        if self.action == 'retrieve':
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthorOfComment()]


class CheckListViewSet(viewsets.ModelViewSet):
    serializer_class = CheckListSerializer

    def get_queryset(self):
        user = self.request.user
        card = get_object_or_404(Card, id=self.kwargs.get('card_id'))

        if user.is_superuser or user.is_staff:
            return CheckList.objects.all()

        return card.check_lists

    def perform_create(self, serializer):
        card = get_object_or_404(Card, id=self.kwargs.get('card_id'))
        serializer.save(card=card)

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthorOrParticipantOrAdminForCommentAndCheckList()]

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy',
                           'switch_is_active'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

    @action(detail=True, methods=['post'])
    def switch_is_active(self, request, **kwargs):
        check_list = get_object_or_404(CheckList, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, check_list)

        if check_list.is_active:
            check_list.is_active = False
            check_list.save()

            return Response(
                {'status': 'success',
                 'message': 'Выполнено!'}, status=status.HTTP_200_OK)

        check_list.is_active = True
        check_list.save()

        return Response(
            {'status': 'success',
             'message': 'Не выполнено!'}, status=status.HTTP_200_OK)
