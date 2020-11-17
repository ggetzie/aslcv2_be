from django.contrib import admin

from main.models import (SpatialArea, SpatialContext, ObjectFind,
                         MaterialCategory, ContextPhoto, AreaType, ContextType)

@admin.register(SpatialArea)
class SpatialAreaAdmin(admin.ModelAdmin):
    list_display = ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters"]
    list_display_links = ["utm_hemisphere",
                          "utm_zone",
                          "area_utm_easting_meters",
                          "area_utm_northing_meters"]


@admin.register(SpatialContext)
class SpatialContextAdmin(admin.ModelAdmin):
    list_display = ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters",
                    "context_number"]
    list_display_links = ["utm_hemisphere",
                          "utm_zone",
                          "area_utm_easting_meters",
                          "area_utm_northing_meters",
                          "context_number"]    

    
@admin.register(ObjectFind)
class ObjectFindAdmin(admin.ModelAdmin):
    list_display = ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters",
                    "context_number",
                    "find_number"]
    list_display_links = ["utm_hemisphere",
                          "utm_zone",
                          "area_utm_easting_meters",
                          "area_utm_northing_meters",
                          "context_number",
                          "find_number"]


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ["material", "category"]
    list_display_links = ["material", "category"]


@admin.register(ContextPhoto)
class ContextPhotoAdmin(admin.ModelAdmin):
    pass

@admin.register(AreaType)
class AreaTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(ContextType)
class ContextTypeAdmin(admin.ModelAdmin):
    pass
