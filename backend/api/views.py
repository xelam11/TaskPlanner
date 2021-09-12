from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Board, List, Favorite
from .permissions import IsStaffOrAuthorOrAuthenticated
from .serializers import BoardSerializer, ListSerializer


class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer

    def perform_create(self, serializer):
        count_of_lists = List.objects.count()
        serializer.save(position=count_of_lists + 1)


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsStaffOrAuthorOrAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        current_user = self.request.user

        if current_user.is_superuser or current_user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(author=current_user)

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
