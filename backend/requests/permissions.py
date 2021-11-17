from django.shortcuts import get_object_or_404
from rest_framework import permissions

from boards.models import Board, ParticipantInBoard


class IsAuthorOrModeratorOrStaffForListOrCreateRequest(
    permissions.BasePermission):

    def has_permission(self, request, view):
        board_id = request.parser_context.get('kwargs').get('board_id')
        board = get_object_or_404(Board, id=board_id)

        if request.user.is_authenticated:
            return (request.user == board.author or
                    ParticipantInBoard.objects.filter(
                        board=board,
                        participant=request.user,
                        is_moderator=True).exists() or
                    request.user.is_staff)


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.board.author == request.user


class IsModerator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=obj.board,
                                                 participant=request.user
                                                 )
        return participant_in_board.is_moderator


class IsStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsRecipient(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
