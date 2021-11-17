from rest_framework import serializers

from .models import List
from cards.serializers import CardListOrCreateSerializer


class ListSerializer(serializers.ModelSerializer):
    cards = CardListOrCreateSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ('id', 'name', 'board', 'position', 'cards')
        read_only_fields = ('board', 'position')


class SwapListsSerializer(serializers.Serializer):
    list_1 = serializers.IntegerField()
    list_2 = serializers.IntegerField()