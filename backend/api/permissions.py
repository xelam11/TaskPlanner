from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Board, List


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Board:
            return obj.author == request.user

        elif type(obj) is List:
            return obj.board.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if type(obj) is Board:
            return obj.participants.filter(id=request.user.id).exists()

        if type(obj) is List:
            return obj.board.participants.filter(id=request.user.id).exists()


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
