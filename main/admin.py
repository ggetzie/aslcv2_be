from django.contrib import admin

from main.models import (SpatialArea, SpatialContext, ObjectFind,
                         MaterialCategory, ContextPhoto)

@admin.register(SpatialArea)
class SpatialAreaAdmin(admin.ModelAdmin):
    pass


@admin.register(SpatialContext)
class SpatialContextAdmin(admin.ModelAdmin):
    pass


@admin.register(ObjectFind)
class ObjectFindAdmin(admin.ModelAdmin):
    pass


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ContextPhoto)
class ContextPhotoAdmin(admin.ModelAdmin):
    pass
