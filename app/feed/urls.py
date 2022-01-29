from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedViewsets

app_name = 'feed'

router = DefaultRouter()
router.register('', FeedViewsets)

urlpatterns = [
    path('', include(router.urls))
]
