"""Вынос класса TagSerializer в отдельный файл было необходимо для избавления
от цикличности в импортах, т.к. TagSerializer вызывается и в BoardSerializer,
и в CardSerializer, а CardSerializer, если следовать цепочке, вызывается
в BoardSerializer."""

from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'hex')
        read_only_fields = ('color', 'hex')
