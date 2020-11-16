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
    path("area/", views.SpatialAreaList.as_view()),
    path("area/<uuid:area_id>/", views.SpatialAreaDetail.as_view()),
    path("context/", views.SpatialContextList.as_view()),
    path("context/<uuid:context_id>/", views.SpatialContextDetail.as_view()),
    path("context/<uuid:context_id>/photo/", views.ContextPhotoUpload.as_view()),
] + router.urls
