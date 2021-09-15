from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BoardViewSet, ListViewSet


router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')
router.register(r'boards/(?P<board_id>\d+)/lists', ListViewSet,
                basename='lists')

urlpatterns = [
    path('v1/', include(router.urls))
]
