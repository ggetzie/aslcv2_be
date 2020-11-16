import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

def utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)

class SpatialArea(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    utm_hemisphere = models.CharField("UTM Hemisphere",
                                      max_length=1,
                                      choices = [("N", "North"),
                                                 ("S", "South")])
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")
    type = models.ForeignKey("AreaType",
                             on_delete=models.SET_NULL,
                             blank=True, null=True,
                             to_field="type",
                             db_column="type")
    longitude_decimal_degrees = models.FloatField("Longitude",
                                                  null=True,
                                                  blank=True)
    latitude_decimal_degrees = models.FloatField("Latitude",
                                                 null=True,
                                                 blank=True)

    class Meta:
        db_table = "areas"
        managed = False
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

    @property
    def contexts(self):
        return (SpatialContext
                .objects
                .filter(utm_hemisphere=self.utm_hemisphere,
                        utm_zone=self.utm_zone,
                        area_utm_easting_meters=self.area_utm_easting_meters,
                        area_utm_northing_meters=self.area_utm_northing_meters))
    

class AreaType(models.Model):
    type = models.CharField("Type", max_length=255,
                            primary_key=True)

    class Meta:
        db_table = "area_types"
        managed = False


class SpatialContext(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    utm_hemisphere = models.CharField("UTM Hemisphere",
                                      max_length=1,
                                      choices = [("N", "North"),
                                                 ("S", "South")])
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")    

    context_number = models.IntegerField("Context Number",
                                         editable=False)
    type = models.ForeignKey("ContextType",
                             null=True, blank=True,
                             to_field="type",
                             on_delete=models.SET_NULL,
                             db_column="type")
                             
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
                                   
    class Meta:
        db_table = "contexts"
        managed = False
        constraints = [
            models.UniqueConstraint(fields=["spatial_area",
                                           "context_number"],
                                    name="unique_spatial_context")
            ]
        verbose_name = "Spatial Context"
        verbose_name_plural = "Spatial Contexts"
        
        ordering = ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters",
                    "context_number"]

    def __str__(self):
        return (f"{self.utm_hemisphere}-{self.utm_zone}-"
                f"{self.area_utm_easting_meters}-"
                f"{self.area_utm_northing_meters}-{self.context_number}")

    def save(self, *args, **kwargs):
        # increment to next context_number
        if not self.context_number and self.spatial_area:
            nc = (self.__class__
                  .objects
                  .filter(spatial_area=self.spatial_area)
                  .aggregate(models
                             .Max("context_number"))["context_number__max"])
            self.context_number = nc + 1 if nc else 1
        super().save(*args, **kwargs)

    @property
    def area(self):
        return (SpatialArea
                .objects
                .get(utm_hemisphere=self.utm_hemisphere,
                     utm_zone=self.utm_zone,
                     area_utm_easting_meters=self.area_utm_easting_meters,
                     area_utm_northing_meters=self.area_utm_northing_meters))


class ContextType(models.Model):
    type = models.CharField("Type",
                            primary_key=True,
                            max_length=255)

    class Meta:
        db_table = "context_types"
        managed=False

    def __str__(self):
        return self.type

    
class ObjectFind(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    utm_hemisphere = models.CharField("UTM Hemisphere",
                                      max_length=1,
                                      choices = [("N", "North"),
                                                 ("S", "South")])
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")    

    context_number = models.IntegerField("Context Number", editable=False)    
    find_number = models.IntegerField("Find Number")
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,
                             null=True,
                             on_delete=models.SET_NULL)
    material = models.CharField("Material",
                                max_length=255,
                                default="")
    category = models.CharField("Category",
                                max_length=255,
                                default="")
    director_notes = models.TextField("Director Notes",
                                      default="",
                                      blank=True)

    class Meta:
        db_table = "finds"
        managed = False
        verbose_name = "Object Find"
        verbose_name_plural = "Object Finds"
        ordering = ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters",
                    "context_number",
                    "find_number"]

    def save(self, *args, **kwargs):
        # increment to next find number in same context on creation
        if not self.find_number and self.spatial_context:
            nf = (self.__class__
                  .filter(spatial_context=self.spatial_context)
                  .aggregate(models.Max("find_number"))["find_number__max"])
            self.find_number = nf +1 if nf else 1
        super().save(*args, **kwargs)
        
    def __str__(self):
        return (f"{self.utm_hemisphere}-{self.utm_zone}-"
                f"{self.area_utm_easting_meters}-"
                f"{self.area_utm_northing_meters}-{self.context_number}"
                f"{self.find_number}")

    
class MaterialCategory(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4)
    material = models.CharField("Material",
                                max_length=255)
    category = models.CharField("Category",
                                max_length=255)

    class Meta:
        db_table = "material_category"
        managed = False
        constraints = [
            models.UniqueConstraint(fields=["material", "category"],
                                    name="unique_material_category")
            ]
        verbose_name = "Material Category"
        verbose_name_plural = "Material Categories"

    def __str__(self):
        return f"{self.material} - {self.category}"



def get_context_folder(instance, filename):
    s_context = instance.context
    s_area = s_context.spatial_area
    extension = filename.split(".")[-1]
    res = "{0}/{1}/{2}/{3}/{4}/{5}".format(s_area.utm_hemisphere,
                                           s_area.utm_zone,
                                           s_area.area_utm_easting_meters,
                                           s_area.area_utm_northing_meters,
                                           s_context.context_number,
                                           filename)
    return res


class ContextPhoto(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    utm_hemisphere = models.CharField("UTM Hemisphere",
                                      max_length=1,
                                      choices = [("N", "North"),
                                                 ("S", "South")])
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")    

    context_number = models.IntegerField("Context Number", editable=False)    
    photo = models.ImageField(upload_to=get_context_folder)
    user = models.ForeignKey(User,
                             null=True,
                             on_delete=models.SET_NULL)

    class Meta:
        db_table = "context_photos"
        verbose_name = "Context Photo"
        verbose_name_plural = "Context Photos"

    def __str__(self):
        return self.photo.name
        
