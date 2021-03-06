from django.contrib import admin

from .models import (Board, Favorite, List, ParticipantRequest,
                     ParticipantInBoard, Card, FileInCard, Comment, CheckList,
                     Tag)


class BoardAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class ListAdmin(admin.ModelAdmin):
    list_filter = ('board', 'name')


class ParticipantInBoardAdmin(admin.ModelAdmin):
    list_filter = ('board', )


class CommentAdmin(admin.ModelAdmin):
    list_filter = ('card', )


class CheckListAdmin(admin.ModelAdmin):
    list_filter = ('card', )


admin.site.register(Board, BoardAdmin)
admin.site.register(Favorite)
admin.site.register(List, ListAdmin)
admin.site.register(ParticipantRequest)
admin.site.register(ParticipantInBoard, ParticipantInBoardAdmin)
admin.site.register(Tag)
admin.site.register(Card)
admin.site.register(FileInCard)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CheckList, CheckListAdmin)
