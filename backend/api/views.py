from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import BoardFilter
from .models import (Board, Favorite, List, ParticipantRequest,
                     ParticipantInBoard, Card, FileInCard)
from .permissions import (IsAuthor, IsParticipant, IsStaff, IsRecipient,
                          IsAuthorOrParticipantOrAdminForCreateList,
                          IsModerator,
                          IsAuthorOrParticipantOrAdminForCreateCard)
from .serializers import (BoardSerializer, ListSerializer,
                          ParticipantRequestSerializer,
                          CardSerializer, ParticipantInBoardSerializer,
                          FileInCardSerializer)
from users.models import CustomUser


# class TagViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer

    def perform_create(self, serializer):
        board = get_object_or_404(Board, id=self.request.data['board'])
        count_of_lists = board.lists.count()
        serializer.save(board=board,
                        position=count_of_lists + 1)

    def perform_destroy(self, instance):
        position = instance.position
        queryset_of_lists = instance.board.lists

        for list_ in queryset_of_lists.all()[position:]:
            list_.position -= 1
            list_.save()

        instance.delete()

    def get_permissions(self):

        if self.action == 'list':
            return [IsAuthenticated()]

        if self.action == 'create':
            return [IsAuthorOrParticipantOrAdminForCreateList()]

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy',
                           'swap'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

    @action(detail=False, methods=['post'])
    def swap(self, request, **kwargs):
        list_1_id = request.data['list_1_id']
        list_2_id = request.data['list_2_id']

        list_1 = get_object_or_404(List, id=list_1_id)
        list_2 = get_object_or_404(List, id=list_2_id)
        self.check_object_permissions(request, list_1)

        if list_1.board != list_2.board:
            return Response({
                'status': 'error',
                'message': 'Нельзя менять местами листы из разных досок!'},
                status=status.HTTP_400_BAD_REQUEST)

        list_1.position, list_2.position = list_2.position, list_1.position
        list_1.save()
        list_2.save()

        return Response(status=status.HTTP_202_ACCEPTED)


class BoardViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, ]
    filter_class = BoardFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Board.objects.all()

        return Board.objects.all()

    def get_serializer_class(self):

        if self.action == 'participants':
            return ParticipantInBoardSerializer

        else:
            return BoardSerializer

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthenticated()]

        if self.action in ('retrieve', 'favorite', 'leave', 'participants'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy',
                           'switch_moderator'):
            return [(IsAuthor | IsStaff)()]

        if self.action in ('send_request', 'delete_participant'):
            return [(IsAuthor | IsModerator | IsStaff)()]

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        user = request.user
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.method == 'POST':
            _, is_created = Favorite.objects.get_or_create(user=user,
                                                           board=board)

            if not is_created:
                return Response({
                    'status': 'error',
                    'message': 'Вы уже добавили данную доску в избранное!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = Favorite.objects.filter(
                user=user,
                board=board).delete()

            if count == 0:
                return Response({
                    'status': 'error',
                    'message': 'Данной доски нет в списке избранных!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def send_request(self, request, **kwargs):
        user_email = request.data['email']
        participant = get_object_or_404(CustomUser, email=user_email)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.method == 'POST':

            if request.user == participant:
                return Response({
                    'status': 'error',
                    'message': 'Вы не можете отправить запрос самому себе!'},
                    status=status.HTTP_400_BAD_REQUEST)

            if board.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message': 'Вы не можете отправить запрос участнику доски!'
                },
                    status=status.HTTP_400_BAD_REQUEST)

            _, is_created = ParticipantRequest.objects.get_or_create(
                participant=participant,
                board=board)

            if not is_created:
                return Response({
                    'status': 'error',
                    'message': 'Вы уже пригласили этого пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = ParticipantRequest.objects.filter(
                participant=participant,
                board=board).delete()

            if count == 0:
                return Response({
                    'status': 'error',
                    'message': 'Данного пользоателя нет в списке приглашенных!'
                },
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def switch_moderator(self, request, **kwargs):
        user_id = request.data['id']
        participant = get_object_or_404(CustomUser, id=user_id)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant=participant,
                                                 )

        if participant_in_board.is_moderator:
            participant_in_board.is_moderator = False
            participant_in_board.save()

            return Response(
                {'status': 'success',
                 'message': 'Данный пользователь больше не модератор!'},
                status=status.HTTP_202_ACCEPTED)

        participant_in_board.is_moderator = True
        participant_in_board.save()

        return Response({'status': 'success',
                         'message': 'Данный пользователь теперь модератор!'},
                        status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'])
    def delete_participant(self, request, **kwargs):
        user_id = request.data['id']
        participant = get_object_or_404(CustomUser, id=user_id)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant=participant,
                                                 )
        if participant == board.author:
            return Response({
                'status': 'error',
                'message': 'Автора доски нельзя исключить из участников!'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.user == board.author:
            board.participants.remove(participant)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if participant_in_board.is_moderator:
            return Response({
                'status': 'error',
                'message': 'Исключить модератора может только автор доски!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(participant)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def leave(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.user == board.author:
            return Response({
                'status': 'error',
                'message': 'Автор доски не может покинуть доску!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(detail=True, methods=['put', 'patch'])
    # def edit_tag(self, request, **kwargs):
    #     tag_id = request.data['id']
    #     tag = get_object_or_404(Tag, id=tag_id)
    #     board = get_object_or_404(Board, id=kwargs.get('pk'))
    #     self.check_object_permissions(self.request, board)
    #     tag_in_board = get_object_or_404(TagInBoard,
    #                                      board=board,
    #                                      tag=tag)
    #     content = request.data['content']
    #
    #     tag_in_board.content = content
    #     tag_in_board.save()
    #
    #     return Response(status=status.HTTP_200_OK)

    @action(detail=True)
    def participants(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        qs_participants = ParticipantInBoard.objects.filter(board=board)

        serializer = self.get_serializer(qs_participants, many=True)

        return Response(serializer.data)


class RequestViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin):
    serializer_class = ParticipantRequestSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return ParticipantRequest.objects.all()

        return ParticipantRequest.objects.filter(participant=user)

    @action(detail=True, methods=['post'], permission_classes=[IsRecipient])
    def accept(self, request, **kwargs):
        request_ = get_object_or_404(ParticipantRequest, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, request_)
        user = request_.participant

        request_.board.participants.add(user)
        request_.delete()

        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'], permission_classes=[IsRecipient])
    def refuse(self, request, **kwargs):
        request_ = get_object_or_404(ParticipantRequest, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, request_)

        request_.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()

    def get_serializer_class(self):

        if self.action == 'file':
            return FileInCardSerializer

        else:
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

    def get_serializer_context(self):
        return {'card_id': self.kwargs.get('pk')}

    def get_permissions(self):

        if self.action == 'list':
            return [IsAuthenticated()]

        if self.action == 'create':
            return [IsAuthorOrParticipantOrAdminForCreateCard()]

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy',
                           'change_list', 'swap', 'file'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

    # @action(detail=True)
    # def participants(self, request, **kwargs):
    #     card = get_object_or_404(Card, id=kwargs.get('pk'))
    #     self.check_object_permissions(self.request, card)
    #     qs_participants = card.participants.all()
    #
    #     serializer = self.get_serializer(qs_participants, many=True)
    #
    #     return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_list(self, request, **kwargs):
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

        if type(new_position) != int:
            return Response({
                'status': 'error',
                'message':
                    "Значения поля 'position' должно быть целочисленным!"},
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
        card_1 = get_object_or_404(Card, id=request.data['card_1_id'])
        card_2 = get_object_or_404(Card, id=request.data['card_2_id'])
        self.check_object_permissions(self.request, card_1)

        if card_1.list != card_2.list:
            return Response({
                'status': 'error',
                'message':
                    'Нельзя менять местами карточки из разных листов!'},
                status=status.HTTP_400_BAD_REQUEST)

        card_1.position, card_2.position = card_2.position, card_1.position
        card_1.save()
        card_2.save()

        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post', 'delete'])
    def file(self, request, **kwargs):
        card = get_object_or_404(Card, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, card)

        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data)
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
