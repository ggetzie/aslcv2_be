from django.contrib import admin

from main.models import (
    SpatialArea,
    SpatialContext,
    ObjectFind,
    MaterialCategory,
    ContextPhoto,
    AreaType,
    ContextType,
    ActionLog,
    BagPhoto,
    FindPhoto,
    SurveyPath,
    SurveyPoint,
)


@admin.register(SpatialArea)
class SpatialAreaAdmin(admin.ModelAdmin):
    list_display = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
    ]
    list_display_links = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
    ]
    list_filter = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
    ]


@admin.register(SpatialContext)
class SpatialContextAdmin(admin.ModelAdmin):
    list_display = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
    ]
    list_display_links = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
    ]
    list_filter = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
    ]


@admin.register(ObjectFind)
class ObjectFindAdmin(admin.ModelAdmin):
    list_display = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
        "find_number",
    ]
    list_display_links = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
        "find_number",
    ]


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ["material", "category"]
    list_display_links = ["material", "category"]


@admin.register(ContextPhoto)
class ContextPhotoAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "created"]
    list_display_links = ["__str__"]
    readonly_fields = ["created", "thumbnail"]
    ordering = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
        "created",
    ]


@admin.register(BagPhoto)
class BagPhotoAdmin(admin.ModelAdmin):
    list_display = ["__str__", "source", "user", "created"]
    list_display_links = ["__str__"]
    readonly_fields = ["created", "thumbnail"]
    list_filter = ["source"]
    ordering = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
        "source",
        "created",
    ]


@admin.register(FindPhoto)
class FindPhotoAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "created"]
    list_display_links = ["__str__"]
    readonly_fields = ["created"]
    ordering = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
        "find_number",
        "created",
    ]


@admin.register(AreaType)
class AreaTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ContextType)
class ContextTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "model_name", "user"]
    list_display_links = ["timestamp", "model_name", "user"]
    readonly_fields = ["timestamp", "user", "model_name", "action", "object_id"]


class SurveyPointInline(admin.TabularInline):
    model = SurveyPoint


@admin.register(SurveyPath)
class SurveyPathAdmin(admin.ModelAdmin):
    list_display = ["id", "user"]
