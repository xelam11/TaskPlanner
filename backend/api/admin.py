from django.contrib import admin

from .models import (Board, Favorite, List, ParticipantRequest, Tag,
                     ParticipantInBoard, TagInBoard, Card)


class BoardAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class ListAdmin(admin.ModelAdmin):
    list_filter = ('board', 'name')


class ParticipantInBoardAdmin(admin.ModelAdmin):
    list_filter = ('board', )


class TagInBoardAdmin(admin.ModelAdmin):
    list_filter = ('board', )


admin.site.register(Board, BoardAdmin)
admin.site.register(Favorite)
admin.site.register(List, ListAdmin)
admin.site.register(ParticipantRequest)
admin.site.register(ParticipantInBoard, ParticipantInBoardAdmin)
admin.site.register(Tag)
admin.site.register(TagInBoard, TagInBoardAdmin)
admin.site.register(Card)
