from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import List
from .permissions import (IsAuthor, IsParticipant, IsStaff,
                          IsAuthorOrParticipantOrAdminForCreateList)

from .serializers import ListSerializer, SwapListsSerializer
from boards.models import Board


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
        list_1 = get_object_or_404(List, id=request.data['list_1'])
        list_2 = get_object_or_404(List, id=request.data['list_2'])
        self.check_object_permissions(request, list_1)

        serializer = SwapListsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        list_1.position, list_2.position = list_2.position, list_1.position
        list_1.save()
        list_2.save()

        return Response(status=status.HTTP_200_OK)
