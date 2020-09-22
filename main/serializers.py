from rest_framework import serializers
from main.models import SpatialArea, SpatialContext, ObjectFind, ObjectPhoto


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

        
class SpatialContextSerializer(serializers.ModelSerializer):
    spatial_area = SpatialAreaNestedSerializer()
    
    class Meta:
        model=SpatialContext
        fields = ["spatial_area",
                  "context_number",
                  "id",
                  "type",
                  "opening_date",
                  "closing_date",
                  "description",
                  "director_notes",
                  "objectphoto_set"]


class SpatialContextNestedSerializer(serializers.ModelSerializer):
    spatial_area = SpatialAreaNestedSerializer()

    class Meta:
        model = SpatialContext
        fields = ["spatial_area",
                  "context_number"]

        
class ObjectFindSerializer(serializers.ModelSerializer):
    spatial_context = SpatialContextNestedSerializer()
    
    class Meta:
        model = ObjectFind
        fields = ["id",
                  "spatial_context",
                  "find_number",
                  "created",
                  "user",
                  "material_category",
                  "director_notes"]

                    
