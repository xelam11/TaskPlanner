from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from boards.views import (BoardViewSet, ParticipantInBoardViewSet,
                          TagInBoardViewSet, SearchAPIView)
from cards.views import (CardViewSet, ParticipantInCardViewSet,
                         FileInCardViewSet, TagInCardViewSet, CommentViewSet,
                         CheckListViewSet)
from requests.views import BoardRequestViewSet, UserRequestViewSet
from lists.views import ListViewSet


router = DefaultRouter()

router.register('boards', BoardViewSet, basename='boards')
router.register(r'boards/(?P<board_id>\d+)/participants',
                ParticipantInBoardViewSet,
                basename='participants')
router.register(r'boards/(?P<board_id>\d+)/tags',
                TagInBoardViewSet,
                basename='tags')
router.register(r'boards/(?P<board_id>\d+)/requests',
                BoardRequestViewSet,
                basename='requests')
router.register('my_requests', UserRequestViewSet, basename='my_requests')
router.register('lists', ListViewSet, basename='lists')
router.register('cards', CardViewSet, basename='cards')
router.register(r'cards/(?P<card_id>\d+)/files',
                FileInCardViewSet,
                basename='files')
router.register(r'cards/(?P<card_id>\d+)/participants',
                ParticipantInCardViewSet,
                basename='participants')
router.register(r'cards/(?P<card_id>\d+)/tags',
                TagInCardViewSet,
                basename='tags')
router.register(r'cards/(?P<card_id>\d+)/comments',
                CommentViewSet,
                basename='comments')
router.register(r'cards/(?P<card_id>\d+)/check-lists',
                CheckListViewSet,
                basename='check_lists')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/v1/search/', SearchAPIView.as_view(), name='search'),
    path('api/v1/', include(router.urls)),
]
