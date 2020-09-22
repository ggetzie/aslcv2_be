from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from aslcv2_be.users.api.views import UserViewSet

import main.views as views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = [
    path("areas/", views.SpatialAreaList.as_view()),
    path("areas/<uuid:area_id>/", views.SpatialAreaDetail.as_view()),
    path("context/<uuid:context_id>/", views.SpatialContextDetail.as_view()),
    path("context/<uuid:context_id>/photo/", views.ObjectPhotoUpload.as_view()),
] + router.urls
