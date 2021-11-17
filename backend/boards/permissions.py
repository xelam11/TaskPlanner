from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import ParticipantInBoard


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.participants.filter(id=request.user.id).exists()


class IsStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsModerator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        participant_in_board = get_object_or_404(ParticipantInBoard,
                                                 board=obj,
                                                 participant=request.user
                                                 )
        return participant_in_board.is_moderator
