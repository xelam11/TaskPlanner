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
            return queryset.filter(favorite_board__user=user)

        return queryset.exclude(favorite_board__user=user)

    def get_is_author(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(author=user)

        return queryset.exclude(author=user)

    def get_is_participant(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(participants__id=user.id)

        return queryset.exclude(participants__id=user.id)
