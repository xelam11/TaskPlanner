import django_filters as filters
from django.db.models import Q

from .models import Card
from boards.models import Tag


class CardFilter(filters.FilterSet):
    board = filters.CharFilter(field_name='list__board')
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    tag_name = filters.CharFilter(field_name='tags__name',
                                  lookup_expr='contains')
    tag_color = filters.CharFilter(method='get_tag_color',
                                   lookup_expr='contains')
    first_name = filters.CharFilter(field_name='participants__first_name',
                                    lookup_expr='contains')
    last_name = filters.CharFilter(field_name='participants__last_name',
                                   lookup_expr='contains')
    username = filters.CharFilter(field_name='participants__username',
                                  lookup_expr='contains')
    is_participant = filters.BooleanFilter(method='get_is_participant')
    search = filters.CharFilter(field_name='get_search')
    # tag__in = NumberInFilter(field_name='tags', lookup_expr='in')

    # tags__in=[1,2,4,5]
    # filters.InFilter
    # filters
    # SELECT * WHERE name IN (1, 2, 3, 4, 5)

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

    def get_search(self, queryset, name, value: str):
        query = Q()

        for field in [
            'name',
            'tags__name',
            'tags__color',
            'participants__first_name',
            'participants__last_name',
            'participants__username'
        ]:
            lookup = {field + '__icontains': value}
            query |= Q(**lookup)

        return queryset.filter(query)

    def get_tag_color(self, queryset, name, value):
        for color in CardFilter.dict_of_colors:
            if value in color:
                return queryset.filter(tags__id=CardFilter.dict_of_colors[color])
        return queryset.none()

    def get_is_participant(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(participants__id=user.id)

        return queryset.exclude(participants__id=user.id)