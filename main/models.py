import datetime
import pathlib
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from main.utils import PHOTO_EXTENSIONS, get_next_photo_number

User = get_user_model()


def utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def build_findphoto_path(find_obj):
    """Build the path to the subfolder where photos associated with a find are stored

    Args:
        find_obj (ObjectFind or FindPhoto): An associated object either the ObjectFind itself or one of its FindPhotos
        needs to have the following attributes:
            utm_hemisphere (str): "N" or "S"
            utm_zone (int): UTM zone number
            area_utm_easting_meters (int): Easting in meters
            area_utm_northing_meters (int): Northing in meters
            context_number (int): Context number
            find_number (int): Find number

    Returns:
        str: the subfolder under settings.MEDIA_ROOT
    """
    sub_root = (
        f"{find_obj.utm_hemisphere}/"
        f"{find_obj.utm_zone}/"
        f"{find_obj.area_utm_easting_meters}/"
        f"{find_obj.area_utm_northing_meters}/"
        f"{find_obj.context_number}"
    )
    return f"{sub_root}/finds/individual/{find_obj.find_number}/photos"


class SpatialArea(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")
    type = models.ForeignKey(
        "AreaType",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        to_field="type",
        db_column="type",
    )
    longitude_decimal_degrees = models.FloatField("Longitude", null=True, blank=True)
    latitude_decimal_degrees = models.FloatField("Latitude", null=True, blank=True)

    class Meta:
        db_table = "areas"
        managed = False
        ordering = [
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
        ]
        verbose_name = "Spatial Area"
        verbose_name_plural = "Spatial Areas"

    def __str__(self):
        return (
            f"{self.utm_hemisphere}-"
            f"{self.utm_zone}-"
            f"{self.area_utm_easting_meters}-"
            f"{self.area_utm_northing_meters}"
        )

    @property
    def spatialcontext_set(self):
        return SpatialContext.objects.filter(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
        )


class AreaType(models.Model):
    type = models.CharField("Type", max_length=255, primary_key=True)

    class Meta:
        db_table = "area_types"
        managed = False
        verbose_name = "Area Type"
        verbose_name_plural = "Area Types"
        ordering = ["type"]

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return self.type


class SpatialContextManager(models.Manager):
    def get_from_str(self, sc_str):
        """Look up a Spatial context from a string in the format
        "N-38-478130-4419430-32"

        Args:
            sc_str (str): A string in the format above

        Returns:
            SpatialContext: A SpatialContext object
        """
        h, z, e, n, c = [int(s) if s.isdigit() else s for s in sc_str.split("-")]
        return self.get(
            utm_hemisphere=h,
            utm_zone=z,
            area_utm_easting_meters=e,
            area_utm_northing_meters=n,
            context_number=c,
        )


class SpatialContext(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")

    context_number = models.IntegerField("Context Number", editable=False)
    type = models.ForeignKey(
        "ContextType",
        null=True,
        blank=True,
        to_field="type",
        on_delete=models.SET_NULL,
        db_column="type",
    )

    opening_date = models.DateField("Opening Date", null=True, blank=True)

    closing_date = models.DateField("Closing Date", null=True, blank=True)
    description = models.CharField(
        "Description", max_length=255, default="", blank=True
    )
    director_notes = models.TextField("Director Notes", default="", blank=True)

    objects = SpatialContextManager()

    class Meta:
        db_table = "contexts"
        managed = False
        verbose_name = "Spatial Context"
        verbose_name_plural = "Spatial Contexts"

        ordering = [
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
        ]

    def __str__(self):
        return (
            f"{self.utm_hemisphere}-{self.utm_zone}-"
            f"{self.area_utm_easting_meters}-"
            f"{self.area_utm_northing_meters}-{self.context_number}"
        )

    def save(self, *args, **kwargs):
        # increment to next context_number
        if not self.context_number:
            nc = self.__class__.objects.filter(
                utm_hemisphere=self.utm_hemisphere,
                utm_zone=self.utm_zone,
                area_utm_easting_meters=self.area_utm_easting_meters,
                area_utm_northing_meters=self.area_utm_northing_meters,
            ).aggregate(models.Max("context_number"))["context_number__max"]
            self.context_number = nc + 1 if nc else 1
        super().save(*args, **kwargs)

    def hzenc_list(self):
        return [
            self.utm_hemisphere,
            self.utm_zone,
            self.area_utm_easting_meters,
            self.area_utm_northing_meters,
            self.context_number,
        ]

    def hzenc_dict(self):
        return {
            "utm_hemisphere": self.utm_hemisphere,
            "utm_zone": self.utm_zone,
            "area_utm_easting_meters": self.area_utm_easting_meters,
            "area_utm_northing_meters": self.area_utm_northing_meters,
            "context_number": self.context_number,
        }

    @property
    def area(self):
        return SpatialArea.objects.get(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
        )

    @property
    def contextphoto_set(self):
        return ContextPhoto.objects.filter(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
        )

    @property
    def bagphoto_set(self):
        return BagPhoto.objects.filter(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
        ).order_by("source")


class ContextType(models.Model):
    type = models.CharField("Type", primary_key=True, max_length=255)

    class Meta:
        db_table = "context_types"
        managed = False
        verbose_name = "Context Type"
        verbose_name_plural = "Context Types"
        ordering = ["type"]

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return self.type


class ObjectFind(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")

    context_number = models.IntegerField("Context Number")
    find_number = models.IntegerField("Find Number", blank=True)
    material = models.CharField("Material", max_length=255, default="")
    category = models.CharField("Category", max_length=255, default="")
    director_notes = models.TextField("Director Notes", default="", blank=True)
    batch_year = models.IntegerField(
        "3d Batch Year", default=2022, db_column="3d_batch_year"
    )
    batch_number = models.IntegerField(
        "3d Batch Number", null=True, blank=True, db_column="3d_batch_number"
    )
    batch_piece = models.IntegerField(
        "3d Batch Piece", null=True, blank=True, db_column="3d_batch_piece"
    )
    weight_grams = models.DecimalField(
        "Weight in grams", max_digits=7, decimal_places=2, null=True, blank=True
    )
    volume_millimeter_cubed = models.DecimalField(
        "Volume in cubic millimeters",
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "finds"
        managed = False
        verbose_name = "Object Find"
        verbose_name_plural = "Object Finds"
        ordering = [
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
            "find_number",
        ]

    def save(self, *args, **kwargs):
        # ensure area and context exist
        _ = SpatialArea.objects.get_or_create(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
        )
        _ = SpatialContext.objects.get_or_create(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
        )

        # increment to next find number in same context on creation
        if not self.find_number and all(
            [
                self.utm_hemisphere,
                self.utm_zone,
                self.area_utm_easting_meters,
                self.area_utm_northing_meters,
                self.context_number,
            ]
        ):
            nf = self.__class__.objects.filter(
                utm_hemisphere=self.utm_hemisphere,
                utm_zone=self.utm_zone,
                area_utm_easting_meters=self.area_utm_easting_meters,
                area_utm_northing_meters=self.area_utm_northing_meters,
                context_number=self.context_number,
            ).aggregate(models.Max("find_number"))["find_number__max"]
            self.find_number = nf + 1 if nf else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.utm_hemisphere}-{self.utm_zone}-"
            f"{self.area_utm_easting_meters}-"
            f"{self.area_utm_northing_meters}-{self.context_number}-"
            f"{self.find_number}"
        )

    def hzencf_list(self):
        return [
            self.utm_hemisphere,
            self.utm_zone,
            self.area_utm_easting_meters,
            self.area_utm_northing_meters,
            self.context_number,
            self.find_number,
        ]

    def hzencf_dict(self):
        return {
            "utm_hemisphere": self.utm_hemisphere,
            "utm_zone": self.utm_zone,
            "area_utm_easting_meters": self.area_utm_easting_meters,
            "area_utm_northing_meters": self.area_utm_northing_meters,
            "context_number": self.context_number,
            "find_number": self.find_number,
        }

    def get_absolute_url(self):
        return reverse("main:find_detail", args=self.hzencf_dict())

    @property
    def material_category(self):
        return MaterialCategory.objects.get(
            material=self.material, category=self.category
        )

    @property
    def spatial_context(self):
        return SpatialContext.objects.get(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
        )

    def findphoto_set(self):
        return FindPhoto.objects.filter(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
            find_number=self.find_number,
        )

    @property
    def findphoto_folder(self):
        # folder is under MEDIA_ROOT
        return build_findphoto_path(self)

    @property
    def absolute_findphoto_folder(self):
        return pathlib.Path(settings.MEDIA_ROOT) / self.findphoto_folder

    def list_files_photo_folder(self, extension=None):
        """List all photos associated with this find from the filesystem
        optionally filtered by extension such as ".jpg".
        Filtering is case-insensitive and must include the leading period.

        Returns:
            list: A list of pathlib.Path objects
        """
        folder = pathlib.Path(settings.MEDIA_ROOT) / self.findphoto_folder
        if not folder.exists():
            return []
        files = sorted(
            list([f for f in folder.iterdir() if not f.is_dir()]),
            key=lambda f: (f.suffix, f.stem),
        )
        if extension:
            files = [f for f in files if f.suffix.lower() == extension.lower()]
        return files

    def list_file_urls_from_photo_folder(self):
        files = self.list_files_photo_folder()
        folder = self.findphoto_folder
        urls = [f"{settings.MEDIA_URL}{folder}/{f.name}" for f in files]
        return urls


class MaterialCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material = models.CharField("Material", max_length=255)
    category = models.CharField("Category", max_length=255)

    class Meta:
        db_table = "material_category"
        managed = False
        verbose_name = "Material Category"
        verbose_name_plural = "Material Categories"

    def __str__(self):
        return f"{self.material} - {self.category}"


def get_photo_filename(subfolder, extension):
    """
    Name photos by sequential numbers according to extension
    e.g. 1.jpg, 2.jpg, 3.jpg, etc.
    """
    full_path = pathlib.Path(settings.MEDIA_ROOT) / subfolder
    photos = full_path.glob(f"*.{extension}")
    existing = [int(p.stem) for p in photos if p.stem.isnumeric()]
    if existing:
        return f"{max(existing) + 1}.{extension}"
    else:
        return f"1.{extension}"


def get_context_folder(instance, filename):
    """
    Find the folder to store photos. Will be determined mostly by the photo
    object's "subfolder" property
    """
    subfolder = instance.subfolder
    extension = filename.rsplit(".", maxsplit=1)[-1]
    folder_path = pathlib.Path(settings.MEDIA_ROOT) / subfolder
    folder_path.mkdir(parents=True, exist_ok=True)
    new_filename = get_next_photo_number(folder_path)

    return f"{subfolder}/{new_filename}.{extension}"


def get_context_folder_tn(instance, filename):
    subfolder = instance.subfolder
    photo_path = pathlib.Path(instance.photo.file.name)

    return f"{subfolder}/tn_{photo_path.name}"


def get_bag_folder(instance, filename):
    """
    Not used. Kept for compatibility with migrations
    """
    pass


class ContextPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")

    context_number = models.IntegerField("Context Number")
    photo = models.ImageField(upload_to=get_context_folder)
    thumbnail = models.ImageField(
        upload_to=get_context_folder_tn, null=True, blank=True
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField("Created", default=utc_now)

    @property
    def subfolder(self):
        sub_root = (
            f"{self.utm_hemisphere}/"
            f"{self.utm_zone}/"
            f"{self.area_utm_easting_meters}/"
            f"{self.area_utm_northing_meters}/"
            f"{self.context_number}"
        )
        return f"{sub_root}/documentation"

    class Meta:
        db_table = "context_photos"
        verbose_name = "Context Photo"
        verbose_name_plural = "Context Photos"

    def __str__(self):
        return self.photo.name

    @property
    def spatial_context(self):
        sc = SpatialContext.objects.get(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
        )
        return sc


class BagPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")

    context_number = models.IntegerField("Context Number")
    photo = models.ImageField(upload_to=get_context_folder)
    thumbnail = models.ImageField(
        upload_to=get_context_folder_tn, null=True, blank=True
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField("Created", default=utc_now)
    source = models.CharField(
        "Location where taken",
        max_length=1,
        choices=(("F", "In Field"), ("D", "Drying")),
        default="F",
    )

    @property
    def subfolder(self):
        sub_root = (
            f"{self.utm_hemisphere}/"
            f"{self.utm_zone}/"
            f"{self.area_utm_easting_meters}/"
            f"{self.area_utm_northing_meters}/"
            f"{self.context_number}"
        )
        if self.source == "F":
            return f"{sub_root}/finds/bags/field"
        else:
            return f"{sub_root}/finds/bags/drying"

    @property
    def spatial_context(self):
        sc = SpatialContext.objects.get(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
        )
        return sc

    class Meta:
        db_table = "bag_photos"
        verbose_name = "Finds Bag Photo"
        verbose_name_plural = "Finds Bag Photos"

    def __str__(self):
        return self.photo.name


def get_findphoto_folder(instance: models.Model, filename: str) -> str:
    subfolder = instance.subfolder
    extension = filename.rsplit(".", maxsplit=1)[-1]
    extension = extension.lower()
    if extension == "jpeg":
        extension = "jpg"
    folder_path = pathlib.Path(settings.MEDIA_ROOT) / subfolder
    folder_path.mkdir(parents=True, exist_ok=True)
    new_filename = get_photo_filename(subfolder, extension)

    return f"{subfolder}/{new_filename}"


class FindPhoto(models.Model):
    # extension = "cr3"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    area_utm_easting_meters = models.IntegerField("Easting (meters)")
    area_utm_northing_meters = models.IntegerField("Northing (meters)")

    context_number = models.IntegerField("Context Number")
    find_number = models.IntegerField("Find Number")
    photo = models.FileField(upload_to=get_findphoto_folder)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField("Created", default=utc_now)

    class Meta:
        db_table = "find_photos"
        verbose_name = "Find Photo"
        verbose_name_plural = "Find Photos"

    def __str__(self):
        return self.photo.name

    def get_filename(self):
        p = pathlib.Path(self.photo.path)
        return p.name

    @property
    def subfolder(self):
        return build_findphoto_path(self)

    @property
    def object_find(self):
        return ObjectFind.objects.get(
            utm_hemisphere=self.utm_hemisphere,
            utm_zone=self.utm_zone,
            area_utm_easting_meters=self.area_utm_easting_meters,
            area_utm_northing_meters=self.area_utm_northing_meters,
            context_number=self.context_number,
            find_number=self.find_number,
        )


class ActionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    model_name = models.CharField("Model Name", max_length=100)
    timestamp = models.DateTimeField("timestamp", default=utc_now)
    action = models.CharField(
        "Action Type",
        max_length=2,
        choices=(("C", "CREATE"), ("R", "READ"), ("U", "UPDATE"), ("D", "DELETE")),
    )
    object_id = models.UUIDField("Object ID")

    class Meta:
        db_table = "action_log"
        verbose_name = "Action Log"
        verbose_name_plural = "Action Logs"

    def __str__(self):
        return (
            f"{self.get_action_display()} on {self.model_name} "
            f"by {self.user.username} at {self.timestamp}"
        )


class SurveyPath(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    notes = models.TextField("Notes", default="", blank=True)

    def started_at(self):
        return self.surveypoint_set.earliest("timestamp").timestamp

    def ended_at(self):
        return self.surveypoint_set.latest("timestamp").timestamp

    def __str__(self):
        return f"{self.id} {self.user}"


class SurveyPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey_path = models.ForeignKey(
        SurveyPath, on_delete=models.CASCADE, related_name="points"
    )
    utm_hemisphere = models.CharField(
        "UTM Hemisphere", max_length=1, choices=[("N", "North"), ("S", "South")]
    )
    utm_zone = models.IntegerField("UTM Zone")
    utm_easting_meters = models.DecimalField(
        "Easting (meters)", max_digits=9, decimal_places=3
    )
    utm_northing_meters = models.DecimalField(
        "Northing (meters)", max_digits=10, decimal_places=3
    )
    latitude = models.DecimalField(
        "Latitude (decimal degrees)", max_digits=9, decimal_places=6
    )
    longitude = models.DecimalField(
        "Longitude (decimal degrees)", max_digits=9, decimal_places=6
    )
    utm_altitude = models.DecimalField(
        "Elevation (meters)", max_digits=8, decimal_places=4
    )
    source = models.CharField(
        "Source", max_length=1, choices=[("G", "Phone GPS"), ("R", "Reach")]
    )
    timestamp = models.DateTimeField("Timestamp")

    def __str__(self):
        return f"{self.utm_hemisphere}-{self.utm_zone}-{self.utm_easting_meters}-{self.utm_northing_meters}"

    class Meta:
        ordering = ["survey_path", "timestamp"]
