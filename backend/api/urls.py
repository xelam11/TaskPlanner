from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BoardViewSet, ListViewSet, RequestViewSet,
                    CardViewSet, CommentViewSet, CheckListViewSet,
                    SearchAPIView)


router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')
router.register('lists', ListViewSet, basename='lists')
router.register('requests', RequestViewSet, basename='requests')
# router.register('tags', TagViewSet, basename='tags')
router.register('cards', CardViewSet, basename='cards')
router.register(r'cards/(?P<card_id>\d+)/comments',
                CommentViewSet,
                basename='comments')
router.register(r'cards/(?P<card_id>\d+)/check-lists',
                CheckListViewSet,
                basename='check_lists')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/search/', SearchAPIView.as_view(), name='search')
]
