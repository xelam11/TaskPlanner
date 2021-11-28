from django.shortcuts import get_object_or_404
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

    def validate(self, data):
        list_id_1 = data.get('list_1')
        list_id_2 = data.get('list_2')
        list_1 = get_object_or_404(List, id=list_id_1)
        list_2 = get_object_or_404(List, id=list_id_2)

        if list_id_1 == list_id_2:
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Нельзя менять местами лист с самим собой!'
            })

        if list_1.board != list_2.board:
            raise serializers.ValidationError({
                'status': 'error',
                'message': 'Нельзя менять местами листы из разных досок!'
            })

        return data
