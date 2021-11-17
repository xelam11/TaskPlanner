from django.shortcuts import get_object_or_404
from rest_framework import permissions

from boards.models import Board


class IsAuthorOrParticipantOrAdminForCreateList(permissions.BasePermission):

    def has_permission(self, request, view):
        board = get_object_or_404(Board, id=request.data['board'])

        if request.user.is_authenticated:
            return (request.user == board.author or
                    board.participants.filter(id=request.user.id).exists()
                    or request.user.is_staff)


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.board.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.board.participants.filter(id=request.user.id).exists()


class IsStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff
