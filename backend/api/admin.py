from django.contrib import admin

from .models import Board


class BoardAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Board, BoardAdmin)
