from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, mixins
from rest_framework_bulk import BulkModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import BoardFilter
from .models import Board, Favorite, List, ParticipantRequest
from .permissions import (IsAuthor, IsParticipant, IsStaff, IsRecipient,
                          IsAuthorOrParticipantOrAdminForCreateList)
from .serializers import (BoardSerializer, ListSerializer,
                          ParticipantRequestSerializer)
from users.models import CustomUser


# class ListViewSet(viewsets.ModelViewSet):
#     queryset = List.objects.all()
#     serializer_class = ListSerializer
#
#     def perform_create(self, serializer):
#         board = get_object_or_404(Board, id=self.request.data['board'])
#         count_of_lists = board.lists.count()
#         serializer.save(board=board,
#                         position=count_of_lists + 1)
#
#     def get_permissions(self):
#
#         if self.action == 'list':
#             return [IsAuthenticated()]
#
#         if self.action == 'create':
#             return [IsAuthorOrParticipantOrAdminForCreateList()]
#
#         if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
#             return [(IsAuthor | IsParticipant | IsStaff)()]


class ListViewSet(BulkModelViewSet):
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

        if self.action in ('retrieve', 'update', 'partial_update', 'destroy'):
            return [(IsAuthor | IsParticipant | IsStaff)()]


class BoardViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, ]
    filter_class = BoardFilter
    serializer_class = BoardSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Board.objects.all()

        # return Board.objects.filter(
        #     Q(author=user) | Q(participants__id=user.id))
        return Board.objects.all()

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
        user_email = request.data['participant']
        participant = get_object_or_404(CustomUser, email=user_email)
        board = get_object_or_404(Board, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, board)

        if request.method == 'POST':
            _, is_created = ParticipantRequest.objects.get_or_create(
                participant=participant,
                board=board)

            if request.user == participant:
                return Response({
                    'status': 'error',
                    'message': 'Вы не можете отправить запрос самому себе!'},
                    status=status.HTTP_400_BAD_REQUEST)

            if board.participants.filter(id=participant.id).exists():
                return Response({
                    'status': 'error',
                    'message': 'Вы не можете отправить запрос участнику доски!'},
                    status=status.HTTP_400_BAD_REQUEST)

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

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthenticated()]

        if self.action in ('retrieve', 'favorite'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy',
                           'send_request'):
            return [(IsAuthor | IsStaff)()]


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
