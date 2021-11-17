from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Request
from .permissions import (IsAuthor, IsModerator, IsStaff, IsRecipient,
                          IsAuthorOrModeratorOrStaffForListOrCreateRequest)
from .serializers import (BoardRequestSerializer, SendRequestSerializer,
                          UserRequestSerializer)
from boards.models import Board


class BoardRequestViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):

    def get_queryset(self):
        board = get_object_or_404(Board, id=self.kwargs.get('board_id'))

        return Request.objects.filter(board=board)

    def get_serializer_class(self):

        if self.action in ('list', 'retrieve'):
            return BoardRequestSerializer

        if self.action in ('create', 'destroy'):
            return SendRequestSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'board_id': self.kwargs.get('board_id')
        }

    def get_permissions(self):

        if self.action in ('list', 'create'):
            return [IsAuthorOrModeratorOrStaffForListOrCreateRequest()]

        if self.action in ('retrieve', 'destroy'):
            return [(IsAuthor | IsModerator | IsStaff)()]


class UserRequestViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin):
    serializer_class = UserRequestSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Request.objects.all()

        return Request.objects.filter(user=user)

    @action(detail=True, methods=['post'], permission_classes=[IsRecipient])
    def accept(self, request, **kwargs):
        request_ = get_object_or_404(Request, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, request_)
        user = request_.user

        request_.board.participants.add(user)
        request_.delete()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsRecipient])
    def refuse(self, request, **kwargs):
        request_ = get_object_or_404(Request, id=kwargs.get('pk'))
        self.check_object_permissions(self.request, request_)

        request_.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
