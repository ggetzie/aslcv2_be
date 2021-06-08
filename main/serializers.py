from typing_extensions import Required
from rest_framework import serializers
from main.models import (FindPhoto, SpatialArea, SpatialContext, ObjectFind,
                         AreaType, ContextType, ContextPhoto, BagPhoto, MaterialCategory)


class ContextListingField(serializers.RelatedField):
    """
    List only context numbers. Used to retrive menu options once
    spatial area is selected.
    """
    def to_representation(self, value):
        return (value.id, value.context_number)


class SpatialAreaSerializer(serializers.ModelSerializer):
    spatialcontext_set = ContextListingField(many=True, read_only=True)
    
    class Meta:
        model = SpatialArea
        fields = ["id",
                  "utm_hemisphere",
                  "utm_zone",
                  "area_utm_easting_meters",
                  "area_utm_northing_meters",
                  "spatialcontext_set"]
        read_only_fields = ["id", "spatialcontext_set"]

        
class SpatialAreaNestedSerializer(serializers.ModelSerializer):
    """
    Return only the values needed to complete the information for the context.
    """
    class Meta:
        model = SpatialArea
        fields = ["utm_hemisphere",
                  "utm_zone",
                  "area_utm_easting_meters",
                  "area_utm_northing_meters"]

class ContextPhotoField(serializers.RelatedField):
    def to_representation(self, value):

        return {"thumbnail_url": value.thumbnail.url if value.thumbnail else "",
                "photo_url": value.photo.url if value.photo else ""}

        
class SpatialContextSerializer(serializers.ModelSerializer):
    contextphoto_set = ContextPhotoField(many=True, read_only=True)
    bagphoto_set = ContextPhotoField(many=True, read_only=True)
    
    class Meta:
        model=SpatialContext
        fields = ["id",
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
                  "bagphoto_set"]
                  
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
            area_utm_northing_meters=validated_data["area_utm_northing_meters"])

        return SpatialContext.objects.create(**validated_data)

    class Meta:
        model=SpatialContext

        fields = ["id",
                  "utm_hemisphere",
                  "utm_zone",
                  "area_utm_easting_meters",
                  "area_utm_northing_meters",
                  "context_number",
                  "type",
                  "opening_date",
                  "closing_date",
                  "description",
                  "director_notes"]

    def validate_description(self, value):
        if value.strip().lower() == "test error":
            raise serializers.ValidationError("Testing Error handling")
        else:
            return value


class SpatialContextNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpatialContext
        fields = ["utm_hemisphere",
                  "utm_zone",
                  "area_utm_easting_meters",
                  "area_utm_northing_meters",
                  "context_number"]

        
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
        fields = ["id",
                  "utm_hemisphere",
                  "utm_zone",
                  "area_utm_easting_meters",
                  "area_utm_northing_meters",
                  "context_number"]

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
            "source"
        ]


class FindPhotoField(serializers.RelatedField):
    def to_representation(self, value):
        return {"photo_name": value.photo.name,
                "photo_url": value.photo.url}        


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
            "findphoto_set"
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

        extra_kwargs = {
            "find_number": {
                "required": False
            }
        }

class MCSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCategory
        fields = [
            "id",
            "material", 
            "category"
        ]
