from rest_framework import permissions


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.participants.filter(id=request.user.id).exists()
