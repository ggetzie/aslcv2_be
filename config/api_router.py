from django.conf import settings
from django.urls import include, path, register_converter
from rest_framework.routers import DefaultRouter, SimpleRouter

from aslcv2_be.users.api.views import UserViewSet

import main.views as views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


class HemisphereConverter:
    regex = r'[NS]'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

register_converter(HemisphereConverter, "hem")    
router.register("users", UserViewSet)
app_name = "api"

area_urls = [
    path("", views.SpatialAreaList.as_view()),
    path("<hem:utm_hemisphere>/", views.SpatialAreaList.as_view()),
    path("<hem:utm_hemisphere>/<int:utm_zone>/", views.SpatialAreaList.as_view()),
    path(("<hem:utm_hemisphere>/"
          "<int:utm_zone>/"
          "<int:area_utm_easting_meters>/"), views.SpatialAreaList.as_view()),
    path(("<hem:utm_hemisphere>/"
          "<int:utm_zone>/"
          "<int:area_utm_easting_meters>/"
          "<int:area_utm_northing_meters>/"), views.SpatialAreaList.as_view()),
    path("<uuid:area_id>/", views.SpatialAreaDetail.as_view()),
    
    ]

urlpatterns = [
    path("area/", include(area_urls)),
    path("context/", views.SpatialContextList.as_view()),
    path("context/<uuid:context_id>/", views.SpatialContextDetail.as_view()),
    path("context/<uuid:context_id>/photo/", views.ContextPhotoUpload.as_view()),
] + router.urls



