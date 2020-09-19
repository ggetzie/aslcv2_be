import datetime
import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

def utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)

class SpatialArea(models.Model):
    utm_hemisphere = models.CharField("UTM Hemisphere",
                                      max_length=1,
                                      choices = [("N", "North"),
                                                 ("S", "South")])
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")
    type = models.CharField("Type",
                            max_length=255,
                            default="",
                            blank=True)
    longitude_decimal_degrees = models.FloatField("Longitude",
                                                  null=True,
                                                  blank=True)
    latitude_decimal_degrees = models.FloatField("Latitude",
                                                 null=True,
                                                 blank=True)

    class Meta:
        db_table = "spatial_areas"
        constraints = [
            models.UniqueConstraint(fields=["utm_hemisphere",
                                            "utm_zone",
                                            "area_utm_easting_meters",
                                            "area_utm_northing_meters"],
                                    name="unique_spatial_area")
            ]
        ordering = ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters"]
        verbose_name = "Spatial Area"
        verbose_name_plural = "Spatial Areas"

    def __str__(self):
        return (f"{self.utm_hemisphere}-"
                f"{self.utm_zone}-"
                f"{self.area_utm_easting_meters}-"
                f"{self.area_utm_northing_meters}")

    
class SpatialContext(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    spatial_area = models.ForeignKey(SpatialArea,
                                     on_delete = models.CASCADE)
    context_number = models.IntegerField("Context Number", editable=False)
    type = models.CharField("Context Type",
                            max_length=255)
    opening_date = models.DateTimeField("Opening Date",
                                        null=True,
                                        blank=True)

    closing_date = models.DateTimeField("Closing Date",
                                        null=True,
                                        blank=True)
    description = models.CharField("Description",
                                   max_length=255,
                                   default="",
                                   blank=True)
    director_notes = models.TextField("Director Notes",
                                      default="",
                                      blank=True)

    def save(self, *args, **kwargs):
        # increment to next context_number
        if not self.context_number and self.spatial_area:
            nc = (self.__class__
                  .objects
                  .filter(spatial_area=self.spatial_area)
                  .aggregate(models
                             .Max("context_number"))["context_number__max"] + 1)
            self.context_number = nc
        super().save(*args, **kwargs)
                                   
    class Meta:
        db_table = "spatial_contexts"
        constraints = [
            models.UniqueConstraint(fields=["spatial_area",
                                           "context_number"],
                                    name="unique_spatial_context")
            ]
        verbose_name = "Spatial Context"
        verbose_name_plural = "Spatial Contexts"
        
        ordering = ["spatial_area__utm_hemisphere",
                    "spatial_area__utm_zone",
                    "spatial_area__area_utm_easting_meters",
                    "spatial_area__area_utm_northing_meters",
                    "context_number"]

    def __str__(self):
        return f"{self.spatial_area} - {self.context_number}"

    
class ObjectFind(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    spatial_context = models.ForeignKey(SpatialContext,
                                        on_delete=models.CASCADE)
    find_number = models.IntegerField("Find Number")
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,
                             null=True,
                             on_delete=models.SET_NULL)
    material_category = models.ForeignKey("main.MaterialCategory",
                                          null=True,
                                          blank=True,
                                          on_delete=models.SET_NULL)
    director_notes = models.TextField("Director Notes",
                                      default="",
                                      blank=True)

    class Meta:
        db_table = "object_finds"
        constraints = [
            models.UniqueConstraint(fields=["spatial_context",
                                            "find_number"],
                                    name="unique_object_find")
            ]
        verbose_name = "Object Find"
        verbose_name_plural = "Object Finds"
        ordering = ["spatial_context__spatial_area__utm_hemisphere",
                    "spatial_context__spatial_area__utm_zone",
                    "spatial_context__spatial_area__area_utm_easting_meters",
                    "spatial_context__spatial_area__area_utm_northing_meters",
                    "spatial_context__context_number",
                    "find_number"]

    def save(self, *args, **kwargs):
        # increment to next find number in same context on creation
        if not self.find_number and self.spatial_context:
            nf = (self.__class__
                  .filter(spatial_context=self.spatial_context)
                  .aggregate(models.Max("find_number")["find_number__max"])+1)
            self.find_number = nf
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.spatial_context}-{self.find_number}"
    
    
class MaterialCategory(models.Model):
    material = models.CharField("Material",
                                max_length=255)
    category = models.CharField("Category",
                                max_length=255)

    class Meta:
        db_table = "options_material_category"
        constraints = [
            models.UniqueConstraint(fields=["material", "category"],
                                    name="unique_material_category")
            ]
        verbose_name = "Material Category"
        verbose_name_plural = "Material Categories"

    def __str__(self):
        return f"{self.material} - {self.category}"



def get_object_folder(instance, filename):
    f = instane.object_find
    s_context = f.spatial_context
    s_area = s_context.spatial_area
    extension = filename.split(".")[-1]
    res = "{0}/{1}/{2}/{3}/{4}/{5}.{6}".format(s_area.utm_hemisphere,
                                               s_area.utm_zone,
                                               s_area.area_utm_easting_meters,
                                               s_area.area_utm_northing_meters,
                                               s_context.context_number,
                                               f.find_number,
                                               extension)
    return res
                  
    

class ObjectPhoto(models.Model):
    object_find = models.ForeignKey(ObjectFind,
                                    on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=get_object_folder,
                              height_field="height",
                              width_field="width")
    user = models.ForeignKey(User,
                             null=True,
                             on_delete=models.SET_NULL)
    height = models.IntegerField("Height")
    width = models.IntegerField("Width")
    

    class Meta:
        db_table = "object_photos"
        verbose_name = "Object Photo"
        verbose_name_plural = "Object Photos"

    def __str__(self):
        return photo.name
        
