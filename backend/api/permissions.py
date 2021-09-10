from rest_framework import permissions


class IsStaffOrAuthorOrAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if (request.method in ['GET', 'PUT', 'PATCH', 'DELETE'] and
                request.user.is_authenticated):
            return (request.user == obj.author or
                    request.user.is_superuser or
                    request.user.is_staff
                    )
