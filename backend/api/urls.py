from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BoardViewSet, ListViewSet, RequestViewSet, TagViewSet,
                    CardViewSet)


router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')
router.register('lists', ListViewSet, basename='lists')
router.register('requests', RequestViewSet, basename='requests')
router.register('tags', TagViewSet, basename='tags')
router.register('cards', CardViewSet, basename='cards')

urlpatterns = [
    path('v1/', include(router.urls)),
]
