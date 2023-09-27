import datetime
from dateutil.tz import gettz
from rest_framework import serializers
from main.models import (
    FindPhoto,
    SpatialArea,
    SpatialContext,
    ObjectFind,
    AreaType,
    ContextType,
    ContextPhoto,
    BagPhoto,
    MaterialCategory,
    SurveyPath,
    SurveyPoint,
)


class ContextListingField(serializers.RelatedField):
    """
    List only context numbers. Used to retrieve menu options once
    spatial area is selected.
    """

    def to_representation(self, value):
        return (value.id, value.context_number)


class SpatialAreaSerializer(serializers.ModelSerializer):
    spatialcontext_set = ContextListingField(many=True, read_only=True)

    class Meta:
        model = SpatialArea
        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "spatialcontext_set",
        ]
        read_only_fields = ["id", "spatialcontext_set"]


class SpatialAreaNestedSerializer(serializers.ModelSerializer):
    """
    Return only the values needed to complete the information for the context.
    """

    class Meta:
        model = SpatialArea
        fields = [
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
        ]


class ContextPhotoField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            "thumbnail_url": value.thumbnail.url if value.thumbnail else "",
            "photo_url": value.photo.url if value.photo else "",
        }


class SpatialContextSerializer(serializers.ModelSerializer):
    contextphoto_set = ContextPhotoField(many=True, read_only=True)
    bagphoto_set = ContextPhotoField(many=True, read_only=True)

    class Meta:
        model = SpatialContext
        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
            "type",
            "opening_date",
            "closing_date",
            "description",
            "director_notes",
            "contextphoto_set",
            "bagphoto_set",
        ]

    def validate_director_notes(self, value):
        return value or ""

    def validate_description(self, value):
        if value.strip().lower() == "test error":
            raise serializers.ValidationError("Testing Error handling")
        else:
            return value


class SpatialContextEditSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        _ = SpatialArea.objects.get_or_create(
            utm_hemisphere=validated_data["utm_hemisphere"],
            utm_zone=validated_data["utm_zone"],
            area_utm_easting_meters=validated_data["area_utm_easting_meters"],
            area_utm_northing_meters=validated_data["area_utm_northing_meters"],
        )
        return SpatialContext.objects.create(**validated_data)

    class Meta:
        model = SpatialContext

        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
            "type",
            "opening_date",
            "closing_date",
            "description",
            "director_notes",
        ]

    def validate_description(self, value):
        if value.strip().lower() == "test error":
            raise serializers.ValidationError("Testing Error handling")
        else:
            return value


class SpatialContextNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpatialContext
        fields = [
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
        ]


class AreaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaType
        fields = ["type"]


class ContextTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextType
        fields = ["type"]


class ContextPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextPhoto
        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
        ]


class BagPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BagPhoto
        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
            "source",
        ]


class FindPhotoField(serializers.RelatedField):
    def to_representation(self, value):
        return {"photo_name": value.photo.name, "photo_url": value.photo.url}


class ObjectFindSerializer(serializers.ModelSerializer):
    findphoto_set = FindPhotoField(many=True, read_only=True)

    class Meta:
        model = ObjectFind
        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
            "find_number",
            "material",
            "category",
            "director_notes",
            "findphoto_set",
            "batch_year",
            "batch_number",
            "batch_piece",
            "weight_grams",
            "volume_millimeter_cubed",
        ]


class FindPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindPhoto
        fields = [
            "id",
            "utm_hemisphere",
            "utm_zone",
            "area_utm_easting_meters",
            "area_utm_northing_meters",
            "context_number",
            "find_number",
        ]


class MCSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCategory
        fields = ["id", "material", "category"]


class SurveyPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPoint
        fields = "__all__"


class SurveyPathSerializer(serializers.ModelSerializer):
    points = SurveyPointSerializer(many=True, read_only=False)

    class Meta:
        model = SurveyPath
        fields = "__all__"

    def create(self, validated_data):
        points_data = validated_data.pop("points")
        path = SurveyPath.objects.create(**validated_data)
        points = [
            SurveyPoint(
                path=path,
                latitude=point_data["latitude"],
                longitude=point_data["longitude"],
                utm_hemisphere=point_data["utm_hemisphere"],
                utm_zone=point_data["utm_zone"],
                utm_easting_meters=point_data["utm_easting_meters"],
                utm_northing_meters=point_data["utm_northing_meters"],
                timestamp=datetime.datetime.fromtimestamp(
                    point_data["timestamp"], tz=gettz(point_data["timezone"])
                ),
                utm_altitude=point_data["utm_altitude"],
                source=point_data["source"],
            )
            for point_data in points_data
        ]
        SurveyPoint.objects.bulk_create(points)
        return path

    def update(self, validated_data):
        points_data = validated_data.pop("points")
        path = SurveyPath.objects.create(**validated_data)
        for point_data in points_data:
            timezone_str = point_data.pop("timezone")
            timezone = gettz(timezone_str)
            timestamp_int = point_data.pop("timestamp")
            timestamp_obj = datetime.datetime.fromtimestamp(timestamp_int, tz=timezone)
            point_data["timestamp"] = timestamp_obj

            if "id" in point_data:
                point_id = point_data.pop("id")
                SurveyPoint.objects.filter(id=point_id).update(**point_data)
            else:
                SurveyPoint.objects.create(path=path, **point_data)

        return path


class SurveyPathListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyPath
        fields = ["id", "notes", "user__username"]
