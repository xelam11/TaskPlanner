import django_filters as filters
from django.db.models import Q

from .models import Card
from boards.models import Tag


class CardFilter(filters.FilterSet):
    board = filters.CharFilter(field_name='list__board')
    tag = filters.CharFilter(field_name='tags')
    is_participant = filters.BooleanFilter(method='get_is_participant')
    search = filters.CharFilter(method='get_search')

    class Meta:
        model = Card
        fields = ('name', )

    dict_of_colors = {
        'красный': Tag.Color.RED,
        'оранжевый': Tag.Color.ORANGE,
        'желтый': Tag.Color.YELLOW,
        'зеленый': Tag.Color.GREEN,
        'голубой': Tag.Color.BLUE,
        'фиолетовый': Tag.Color.PURPLE
    }

    def get_search(self, queryset, name, value):
        query = Q()

        for field in [
            'name',
            'tags__name',
            'participants__first_name',
            'participants__last_name',
            'participants__username'
        ]:
            lookup = {field + '__icontains': value}
            query |= Q(**lookup)

        if value in CardFilter.dict_of_colors:
            tag_id = CardFilter.dict_of_colors[value]

            return queryset.filter(Q(tags__id=tag_id) | Q(query)).distinct()

        return queryset.filter(query).distinct()

    def get_is_participant(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(participants__id=user.id)

        return queryset.exclude(participants__id=user.id)
