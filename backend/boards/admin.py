from django.contrib import admin

from .models import Board, Favorite, ParticipantInBoard, Tag


class BoardAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class ParticipantInBoardAdmin(admin.ModelAdmin):
    list_filter = ('board',)


admin.site.register(Board, BoardAdmin)
admin.site.register(Favorite)
admin.site.register(ParticipantInBoard, ParticipantInBoardAdmin)
admin.site.register(Tag)
