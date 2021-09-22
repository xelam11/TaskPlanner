from django.db.models import Q
import django_filters as filters

from .models import Board


class BoardFilter(filters.FilterSet):
    is_favored = filters.BooleanFilter(method='get_is_favored')
    is_author = filters.BooleanFilter(method='get_is_author')
    is_participant = filters.BooleanFilter(method='get_is_participant')

    class Meta:
        model = Board
        fields = ('is_favored', 'is_author', 'is_participant')

    def get_is_favored(self, queryset, name, value):
        user = self.request.user

        if value:
            return Board.objects.filter(favorite_board__user=user)

        return Board.objects.filter(
            Q(author=user) | Q(participants__id=user.id))

    def get_is_author(self, queryset, name, value):
        user = self.request.user

        if value:
            return Board.objects.filter(author=user)

        return Board.objects.filter(
            Q(author=user) | Q(participants__id=user.id))

    def get_is_participant(self, queryset, name, value):
        user = self.request.user

        if value:
            return Board.objects.filter(participants__id=user.id)

        return Board.objects.filter(
            Q(author=user) | Q(participants__id=user.id))
