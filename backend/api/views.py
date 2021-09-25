from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework_bulk import BulkModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import BoardFilter
from .models import Board, Favorite, List
from .permissions import (IsAuthor, IsParticipant, IsStaff,
                          IsAuthorOrParticipantOrAdminForCreateList)
from .serializers import BoardSerializer, ListSerializer


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

    def destroy(self, request, *args, **kwargs):
        current_list = get_object_or_404(List, id=kwargs.get('pk'))
        pos = current_list.position
        queryset_of_lists = current_list.board.lists

        for list_ in queryset_of_lists.all()[pos:]:
            list_.position -= 1
            list_.save()

        return super().destroy(request, *args, **kwargs)

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

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthenticated()]

        if self.action in ('retrieve', 'favorite'):
            return [(IsAuthor | IsParticipant | IsStaff)()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [(IsAuthor | IsStaff)()]
