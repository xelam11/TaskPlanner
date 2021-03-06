from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .filters import BoardFilter, CardFilter, ParticipantsFilter
from .models import (Board, Favorite, List, ParticipantRequest,
                     ParticipantInBoard, Card, FileInCard, Comment, CheckList,
                     Tag)
from .permissions import (IsAuthor, IsParticipant, IsStaff, IsRecipient,
                          IsModerator,
                          IsAuthorOrParticipantOrAdminForCreateList,
                          IsAuthorOrParticipantOrAdminForCreateCard,
                          IsAuthorOrParticipantOrAdminForCommentAndCheckList,
                          IsAuthorOfComment)
from .paginators import ParticipantsInBoardPaginator
from .serializers import (BoardListOrCreateSerializer, BoardSerializer,
                          ListSerializer,
                          ParticipantRequestSerializer,
                          CardSerializer, CardListOrCreateSerializer,
                          ParticipantInBoardSerializer,
                          FileInCardSerializer, CommentSerializer,
                          ParticipantInCardSerializer,
                          CheckListSerializer, SwapListsSerializer,
                          SendRequestSerializer, ChangeListOfCardSerializer,
                          SwitchModeratorSerializer, SwapCardsSerializer,
                          DeleteParticipantSerializer,
                          SearchBoardSerializer, SearchCardSerializer,
                          TagSerializer)
from users.models import CustomUser


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class BoardViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, ]
    filter_class = BoardFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(participants__id=self.request.user.id)

    def get_serializer_class(self):

        if self.action in ('list', 'create'):
            return BoardListOrCreateSerializer

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return BoardSerializer

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthenticated()]

        if self.action in ('retrieve', 'favorite', 'leave', 'participants'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy',
                           'switch_moderator'):
            return [(IsAuthor | IsStaff)()]

        if self.action in ('send_request', 'delete_participant', 'edit_tag'):
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
                    'message': '???? ?????? ???????????????? ???????????? ?????????? ?? ??????????????????!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = Favorite.objects.filter(
                user=user,
                board=board).delete()

            if count == 0:
                return Response({
                    'status': 'error',
                    'message': '???????????? ?????????? ?????? ?? ???????????? ??????????????????!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def send_request(self, request, **kwargs):
        serializer = SendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = request.data['email']
        participant = get_object_or_404(CustomUser, email=user_email)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.method == 'POST':

            if self.request.user == participant:
                return Response({
                    'status': 'error',
                    'message': '???? ???? ???????????? ?????????????????? ???????????? ???????????? ????????!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if board.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message': '???? ???? ???????????? ?????????????????? ???????????? ?????????????????? ??????????!'
                }, status=status.HTTP_400_BAD_REQUEST
                )

            _, is_created = ParticipantRequest.objects.get_or_create(
                participant=participant,
                board=board)

            if not is_created:
                return Response({
                    'status': 'error',
                    'message': '???? ?????? ???????????????????? ?????????? ????????????????????????!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            count, _ = ParticipantRequest.objects.filter(
                participant=participant,
                board=board).delete()

            if count == 0:
                return Response({
                    'status': 'error',
                    'message': '?????????????? ?????????????????????? ?????? ?? ???????????? ????????????????????????!'
                },
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def switch_moderator(self, request, **kwargs):
        serializer = SwitchModeratorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.data['id']
        participant = get_object_or_404(CustomUser, id=user_id)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant=participant,
                                                 )

        if request.user == participant:
            return Response({
                'status': 'error',
                'message': '?????????? ?????????? ???????????? ???????????? ???????? ????????????????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        if participant_in_board.is_moderator:
            participant_in_board.is_moderator = False
            participant_in_board.save()

            return Response(
                {'status': 'success',
                 'message': '???????????? ???????????????????????? ???????????? ???? ??????????????????!'},
                status=status.HTTP_200_OK)

        participant_in_board.is_moderator = True
        participant_in_board.save()

        return Response({'status': 'success',
                         'message': '???????????? ???????????????????????? ???????????? ??????????????????!'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def delete_participant(self, request, **kwargs):
        serializer = DeleteParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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
                'message': '???????????? ?????????? ???????????? ?????????????????? ???? ????????????????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.user == board.author:
            board.participants.remove(participant)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if participant_in_board.is_moderator:
            return Response({
                'status': 'error',
                'message': '?????????????????? ???????????????????? ?????????? ???????????? ?????????? ??????????!'},
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
                'message': '?????????? ?????????? ???? ?????????? ???????????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        board.participants.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def edit_tag(self, request, **kwargs):
        serializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)
        tag_id = request.data['id']

        if tag_id not in range(1, Tag.objects.count() + 1):
            return Response({
                'status': 'error',
                'message': '???????????? ???????? ???? ????????????????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        tag = board.tags.get(id=tag_id)
        name = request.data['name']
        tag.name = name
        tag.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, filter_class=ParticipantsFilter)
    def participants(self, request, **kwargs):
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        qs_participants = self.filter_queryset(
            ParticipantInBoard.objects.filter(board=board))

        paginator = ParticipantsInBoardPaginator()
        page = paginator.paginate_queryset(qs_participants, request)
        serializer = ParticipantInBoardSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


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

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsRecipient])
    def refuse(self, request, **kwargs):
        request_ = get_object_or_404(ParticipantRequest, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, request_)

        request_.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['board']

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return List.objects.all()

        return List.objects.filter(
            board__participants__id=self.request.user.id)

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

        if self.action == 'create':
            return [IsAuthorOrParticipantOrAdminForCreateList()]

        if self.action == 'list':
            return [IsAuthenticated()]

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy',
                           'swap'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

    @action(detail=False, methods=['post'])
    def swap(self, request, **kwargs):
        serializer = SwapListsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        list_1 = get_object_or_404(List, id=request.data['list_1'])
        list_2 = get_object_or_404(List, id=request.data['list_2'])
        self.check_object_permissions(request, list_1)

        if list_1 == list_2:
            return Response({
                'status': 'error',
                'message': '???????????? ???????????? ?????????????? ???????? ?? ?????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        if list_1.board != list_2.board:
            return Response({
                'status': 'error',
                'message': '???????????? ???????????? ?????????????? ?????????? ???? ???????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        list_1.position, list_2.position = list_2.position, list_1.position
        list_1.save()
        list_2.save()

        return Response(status=status.HTTP_200_OK)


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
                           'change_list', 'swap', 'file', 'participant'):
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
                    '???????????? ?????????????????????? ???????????????? ?? ???????? ???? ???????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        if type(new_position) != int:
            return Response({
                'status': 'error',
                'message':
                    "???????????????? ???????? 'position' ???????????? ???????? ??????????????????????????!"},
                status=status.HTTP_400_BAD_REQUEST)

        if new_position < 1:
            return Response({
                'status': 'error',
                'message':
                    "???????????????? ???????? 'position' ???? ?????????? ???????? ???????????? 1!"},
                status=status.HTTP_400_BAD_REQUEST)

        if new_position > new_list.cards.count() + 1:
            return Response({
                'status': 'error',
                'message': "???????????????? ???????? 'position' ???? ?????????? "
                           "?????????????????? ???????????????????? ???????????????? ?? ?????????? ????????????!"},
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
                'message': '???????????? ???????????? ?????????????? ???????????????? ?? ?????????? ??????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        if card_1.list != card_2.list:
            return Response({
                'status': 'error',
                'message':
                    '???????????? ???????????? ?????????????? ???????????????? ???? ???????????? ????????????!'},
                status=status.HTTP_400_BAD_REQUEST)

        card_1.position, card_2.position = card_2.position, card_1.position
        card_1.save()
        card_2.save()

        return Response(status=status.HTTP_200_OK)

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
        serializer = ParticipantInCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card = get_object_or_404(Card, id=kwargs.get('pk'))
        board = card.list.board
        self.check_object_permissions(self.request, card)
        participant = get_object_or_404(CustomUser, id=request.data['id'])

        if request.method == 'POST':

            if card.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message':
                        '???????????? ???????????????????????? ?????? ???????????????? ???????????????????? ????????????????!'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not board.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message':
                        '???????????? ???????????????????????? ???? ???????????????? ?????????????????? ??????????!'},
                    status=status.HTTP_400_BAD_REQUEST)

            card.participants.add(participant)
            return Response(status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if not card.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message':
                        '???????????? ???????????????????????? ???? ???????????????? ?????????????????? ????????????????!'},
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
                 'message': '??????????????????!'}, status=status.HTTP_200_OK)

        check_list.is_active = True
        check_list.save()

        return Response(
            {'status': 'success',
             'message': '???? ??????????????????!'}, status=status.HTTP_200_OK)


class SearchAPIView(APIView):

    def get(self, request):
        name = request.GET.get('name', None)
        boards = Board.objects.filter(participants__id=self.request.user.id)
        cards = Card.objects.filter(
            list__board__participants__id=self.request.user.id)

        if name:
            boards = boards.filter(name__icontains=name)
            cards = cards.filter(name__icontains=name)

            return JsonResponse({
                'boards': SearchBoardSerializer(instance=boards,
                                                many=True).data,
                'cards': SearchCardSerializer(instance=cards,
                                              many=True).data
            })

        return JsonResponse({'boards': [], 'cards': []})
