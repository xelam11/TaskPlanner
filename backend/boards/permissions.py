from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Board, ParticipantInBoard, Tag


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Board:
            return obj.author == request.user

        if type(obj) is ParticipantInBoard:
            return obj.board.author == request.user

        if type(obj) is Tag:
            return obj.board.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Board:
            return obj.participants.filter(id=request.user.id).exists()

        if type(obj) is ParticipantInBoard:
            return obj.board.participants.filter(id=request.user.id).exists()

        if type(obj) is Tag:
            return obj.board.participants.filter(id=request.user.id).exists()


class IsStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsAuthorOrParticipantOrAdminListParticipantsAndTags(permissions.
                                                          BasePermission):

    def has_permission(self, request, view):
        board = get_object_or_404(Board, id=view.kwargs.get('board_id'))

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists() or
                    request.user.is_staff)


class IsAuthorOrModeratorOrAdminDelParticipantsPutTags(permissions.
                                                       BasePermission):

    def has_permission(self, request, view):
        board = get_object_or_404(Board, id=view.kwargs.get('board_id'))
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=board,
                                                 participant=request.user
                                                 )

        if request.user.is_authenticated:
            return (request.user == board.author or
                    participant_in_board.is_moderator or
                    request.user.is_staff)
