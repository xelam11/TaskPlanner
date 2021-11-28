from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Card, FileInCard, Comment, CheckList
from boards.models import Tag
from lists.models import List
from users.models import CustomUser


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Card:
            return obj.list.board.author == request.user

        if type(obj) is Tag:
            return obj.board.author == request.user

        if type(obj) is CustomUser or type(obj) is FileInCard:
            card = get_object_or_404(Card, id=view.kwargs.get('card_id'))
            board = card.list.board
            return board.author == request.user

        elif type(obj) is Comment:
            return obj.card.list.board.author == request.user

        elif type(obj) is CheckList:
            return obj.card.list.board.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Card:
            return obj.list.board.participants.filter(
                id=request.user.id).exists()

        if type(obj) is Tag:
            return obj.board.participants.filter(
                id=request.user.id).exists()

        if type(obj) is CustomUser or type(obj) is FileInCard:
            card = get_object_or_404(Card, id=view.kwargs.get('card_id'))
            board = card.list.board
            return board.participants.filter(id=request.user.id).exists()

        elif type(obj) is Comment:
            return obj.card.list.board.participants.filter(
                id=request.user.id).exists()

        elif type(obj) is CheckList:
            return obj.card.list.board.participants.filter(
                id=request.user.id).exists()


class IsStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsAuthorOrParticipantOrAdminForCreateCard(permissions.BasePermission):

    def has_permission(self, request, view):
        list_ = get_object_or_404(List, id=request.data['list'])
        board = list_.board

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists() or
                    request.user.is_staff)


class IsAuthorOrParticipantOrAdminOfBoardForActionWithCard(permissions.
                                                           BasePermission):
    """Данное разрешение распространяется на создание, удаление
    и просмотр всех:
    - файлов в карточке;
    - участников в карточке;
    - тегов в карточке;
    - комментариев;
    - чек-листов."""

    def has_permission(self, request, view):
        card = get_object_or_404(Card, id=view.kwargs.get('card_id'))
        board = card.list.board

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists() or
                    request.user.is_staff)


class IsAuthorOfComment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
