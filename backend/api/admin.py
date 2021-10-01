from django.contrib import admin

from .models import Board, Favorite, List, ParticipantRequest, Tag


class BoardAdmin(admin.ModelAdmin):
    list_filter = ('name',)


class ListAdmin(admin.ModelAdmin):
    list_filter = ('board', 'name')


admin.site.register(Board, BoardAdmin)
admin.site.register(Favorite)
admin.site.register(List, ListAdmin)
admin.site.register(ParticipantRequest)
admin.site.register(Tag)
