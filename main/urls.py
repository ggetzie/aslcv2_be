from django.urls import include, path, register_converter
from config.api_router import HemisphereConverter

from main import views

register_converter(HemisphereConverter, "hem")
app_name = "main"

urlpatterns = [
    path("", views.hemisphere_select, name="hemisphere_select"),
    path("find/<uuid:uuid>", views.find_by_uuid, name="find_by_uuid"),
    path("<hem:hemisphere>", views.zone_select, name="zone_select"),
    path("<hem:hemisphere>/<int:zone>", views.easting_select, name="easting_select"),
    path(
        "<hem:hemisphere>/<int:zone>/<int:easting>",
        views.northing_select,
        name="northing_select",
    ),
    path(
        "<hem:hemisphere>/<int:zone>/<int:easting>/<int:northing>",
        views.spatialcontext_select,
        name="spatialcontext_select",
    ),
    path(
        "<hem:hemisphere>/<int:zone>/<int:easting>/<int:northing>/<int:context_number>",
        views.find_select,
        name="find_select",
    ),
    path(
        "<hem:hemisphere>/<int:zone>/<int:easting>/<int:northing>/<int:context_number>/<int:find_number>",
        views.find_detail,
        name="find_detail",
    ),
]
