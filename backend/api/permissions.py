from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Board, List, ParticipantInBoard, Card, Comment


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Board:
            return obj.author == request.user

        elif type(obj) is List:
            return obj.board.author == request.user

        elif type(obj) is Card:
            return obj.list.board.author == request.user

        elif type(obj) is Comment:
            return obj.card.list.board.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Board:
            return obj.participants.filter(id=request.user.id).exists()

        if type(obj) is List:
            return obj.board.participants.filter(id=request.user.id).exists()

        if type(obj) is Card:
            return obj.list.board.participants.filter(
                id=request.user.id).exists()

        if type(obj) is Comment:
            return obj.card.list.board.participants.filter(
                id=request.user.id).exists()


class IsStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsAuthorOrParticipantOrAdminForCreateList(permissions.BasePermission):

    def has_permission(self, request, view):
        board = get_object_or_404(Board, id=request.data['board'])

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists() or
                    request.user.is_staff)


class IsRecipient(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.participant


class IsModerator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=obj,
                                                 participant=request.user
                                                 )
        return participant_in_board.is_moderator


class IsAuthorOrParticipantOrAdminForCreateCard(permissions.BasePermission):

    def has_permission(self, request, view):
        list_ = get_object_or_404(List, id=request.data['list'])
        board = list_.board

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists() or
                    request.user.is_staff)


class IsAuthorOrParticipantOrAdminForCreateComment(permissions.BasePermission):

    def has_permission(self, request, view):
        card = get_object_or_404(Card, id=view.kwargs.get('card_id'))
        board = card.list.board

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists() or
                    request.user.is_staff)


# class IsAuthorOfComment(permissions.BasePermission):
#
#     def has_object_permission(self, request, view, obj):
#         breakpoint()
#         comment = get_object_or_404(Comment, id=view.kwargs.get('comment_id'))
#
#         return request.user == comment.author
