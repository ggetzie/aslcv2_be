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
    regex = r"[NS]"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(HemisphereConverter, "hem")
router.register("users", UserViewSet)
app_name = "api"

area_urls = [
    path("", views.SpatialAreaList.as_view(), name="spatialarea_list"),
    path(
        "<hem:utm_hemisphere>/",
        views.SpatialAreaList.as_view(),
        name="spatialarea_list_h",
    ),
    path(
        "<hem:utm_hemisphere>/<int:utm_zone>/",
        views.SpatialAreaList.as_view(),
        name="spatialarea_list_hz",
    ),
    path(
        ("<hem:utm_hemisphere>/" "<int:utm_zone>/" "<int:area_utm_easting_meters>/"),
        views.SpatialAreaList.as_view(),
        name="spatialarea_list_hze",
    ),
    path(
        (
            "<hem:utm_hemisphere>/"
            "<int:utm_zone>/"
            "<int:area_utm_easting_meters>/"
            "<int:area_utm_northing_meters>/"
        ),
        views.SpatialAreaList.as_view(),
        name="spatialarea_list_hzen",
    ),
    path(
        "<uuid:area_id>/", views.SpatialAreaDetail.as_view(), name="spatialarea_detail"
    ),
    path("types/", views.AreaTypeList.as_view(), name="spatialarea_types"),
]

context_urls = [
    path("", views.SpatialContextList.as_view(), name="spatialcontext_list"),
    path(
        (
            "<hem:utm_hemisphere>/"
            "<int:utm_zone>/"
            "<int:area_utm_easting_meters>/"
            "<int:area_utm_northing_meters>/"
        ),
        views.SpatialContextList.as_view(),
        name="spatialcontext_list_hzen",
    ),
    path(
        "<uuid:context_id>/",
        views.SpatialContextDetail.as_view(),
        name="spatialcontext_detail",
    ),
    path(
        "<uuid:context_id>/photo/",
        views.ContextPhotoUpload.as_view(),
        name="spatialcontext_photo",
    ),
    path("types/", views.ContextTypeList.as_view(), name="spatialcontext_types"),
    path(
        "<uuid:context_id>/bagphoto/",
        views.BagPhotoUpload.as_view(),
        name="spatialcontext_bagphoto",
    ),
]

find_urls = [
    path("", views.ObjectFindList.as_view(), name="objectfind_list"),
    path("mc/", views.MCList.as_view(), name="materialcategory_list"),
    path(
        (
            "<hem:utm_hemisphere>/"
            "<int:utm_zone>/"
            "<int:area_utm_easting_meters>/"
            "<int:area_utm_northing_meters>/"
            "<int:context_number>/"
        ),
        views.ObjectFindList.as_view(),
        name="objectfind_list_hzenc",
    ),
    path(
        (
            "cfl/<hem:utm_hemisphere>/"
            "<int:utm_zone>/"
            "<int:area_utm_easting_meters>/"
            "<int:area_utm_northing_meters>/"
            "<int:context_number>/"
        ),
        views.find_list_by_context,
        name="contextfind_list",
    ),
    path(
        (
            "<hem:utm_hemisphere>/"
            "<int:utm_zone>/"
            "<int:area_utm_easting_meters>/"
            "<int:area_utm_northing_meters>/"
            "<int:context_number>/"
            "<int:find_number>/"
        ),
        views.find_detail_hzencf,
        name="find_detail_hzencf",
    ),
    path("<uuid:find_id>/", views.ObjectFindDetail.as_view(), name="objectfind_detail"),
    path(
        "<uuid:find_id>/photo/",
        views.FindPhotoUpload.as_view(),
        name="objectfind_photo",
    ),
    path(
        "<uuid:find_id>/photo/replace/",
        views.FindPhotoReplace.as_view(),
        name="objectfind_photo_replace",
    ),
]

path_urls = [
    path("", views.SurveyPathList.as_view(), name="surveypath_list"),
    path("<uuid:pk>/", views.SurveyPathDetail.as_view(), name="surveypath_detail"),
]

urlpatterns = [
    path("area/", include(area_urls)),
    path("context/", include(context_urls)),
    path("find/", include(find_urls)),
    path("path/", include(path_urls)),
] + router.urls
