from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BoardViewSet


router = DefaultRouter()
router.register('boards', BoardViewSet, basename='boards')

urlpatterns = [
    path('v1/', include(router.urls))
]
