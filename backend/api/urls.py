from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter

from .views import BoardViewSet, ListViewSet


router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')
# router.register('lists', ListViewSet, basename='lists')

router_bulk = BulkRouter()
router_bulk.register('lists', ListViewSet, basename='lists')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(router_bulk.urls)),
]
