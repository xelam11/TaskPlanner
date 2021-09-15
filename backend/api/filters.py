import django_filters as filters

from .models import Board


class BoardFilter(filters.FilterSet):
    is_favored = filters.BooleanFilter(method='get_is_favored')

    class Meta:
        model = Board
        fields = ('is_favored', )

    def get_is_favored(self, queryset, name, value):
        user = self.request.user

        if value:
            return Board.objects.filter(favorite_board__user=user)

        return Board.objects.filter(author=user)
