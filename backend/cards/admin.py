from django.contrib import admin

from .models import Card, Comment, CheckList, FileInCard


class CommentAdmin(admin.ModelAdmin):
    list_filter = ('card', )


class CheckListAdmin(admin.ModelAdmin):
    list_filter = ('card', )


admin.site.register(Card)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CheckList, CheckListAdmin)
admin.site.register(FileInCard)
