from django.contrib import admin

from .models import List


class ListAdmin(admin.ModelAdmin):
    list_filter = ('board', 'name')


admin.site.register(List, ListAdmin)
