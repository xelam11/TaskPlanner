from rest_framework import viewsets

from .models import Board
from .permissions import IsStaffOrAuthorOrAuthenticated
from .serializers import BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsStaffOrAuthorOrAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        current_user = self.request.user

        if current_user.is_superuser or current_user.is_staff:
            return Board.objects.all()

        return Board.objects.filter(author=current_user)
