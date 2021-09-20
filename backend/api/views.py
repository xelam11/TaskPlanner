from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .filters import BoardFilter
from .models import Board, Favorite
from .permissions import IsAuthor, IsParticipant
from .serializers import BoardSerializer, ListSerializer


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

        return Board.objects.filter(
            Q(author=user) | Q(participants__id=user.id))

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, **kwargs):
        user = request.user
        board = get_object_or_404(Board, id=kwargs.get('pk'))

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
                    'message': 'Вы уже далили данную доску из избранных!'},
                    status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):

        if self.action == 'create':
            return [(IsAdminUser | IsAuthenticated)()]

        if self.action in ('list', 'retrieve', 'favorite'):
            return [(IsAuthenticated &
                     (IsAuthor | IsParticipant | IsAdminUser))()]

        if self.action in ('update', 'partial_update', 'destroy'):
            return [(IsAuthenticated & (IsAuthor | IsAdminUser))()]


class ListViewSet(viewsets.ModelViewSet):
    serializer_class = ListSerializer

    def perform_create(self, serializer):
        board = get_object_or_404(Board, id=self.kwargs.get('board_id'))
        count_of_lists = board.lists.count()
        serializer.save(board=board,
                        position=count_of_lists + 1)

    def get_queryset(self):
        board = get_object_or_404(Board, id=self.kwargs.get('board_id'))
        return board.lists
