import django_filters as filters
from django.db.models import Q

from .models import Board, ParticipantInBoard, Card


class BoardFilter(filters.FilterSet):
    is_favored = filters.BooleanFilter(method='get_is_favored')
    is_author = filters.BooleanFilter(method='get_is_author')
    is_participant = filters.BooleanFilter(method='get_is_participant')
    name = filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Board
        fields = ('is_favored', 'is_author', 'is_participant', 'name')

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


# class ParticipantsFilter(filters.FilterSet):
#     is_moderator = filters.BooleanFilter(method='get_is_moderator')
#
#     class Meta:
#         model = ParticipantInBoard
#         fields = ('is_moderator', )
#
#     def get_is_moderator(self, queryset, name, value):
#         breakpoint()
#         if value:
#             return queryset.filter(is_moderator=True)
#
#         else:
#             return queryset.filter(is_moderator=False)


class CardFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    first_name = filters.CharFilter(field_name='participants__first_name',
                                    lookup_expr='contains')
    last_name = filters.CharFilter(field_name='participants__last_name',
                                   lookup_expr='contains')
    username = filters.CharFilter(field_name='participants__username',
                                  lookup_expr='contains')
    is_participant = filters.BooleanFilter(method='get_is_participant')

    class Meta:
        model = Card
        fields = ('name', )

    def get_is_participant(self, queryset, name, value):
        user = self.request.user

        if value:
            return queryset.filter(participants__id=user.id)

        return queryset.exclude(participants__id=user.id)
