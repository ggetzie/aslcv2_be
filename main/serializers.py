from rest_framework import serializers
from main.models import SpatialArea, SpatialContext, ObjectFind


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
                  "contextphoto_set"]

        
class SpatialContextEditSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        sa, _ = SpatialArea.objects.get_or_create(
            utm_hemisphere=validated_data["utm_hemisphere"],
            utm_zone=validated_data["utm_zone"],
            area_utm_easting_meters=validated_data["area_utm_easting_meters"],
            area_utm_northing_meters=validated_data["area_utm_northing_meters"])
        print(validated_data)
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


class SpatialContextNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpatialContext
        fields = ["utm_hemisphere",
                  "utm_zone",
                  "area_utm_easting_meters",
                  "area_utm_northing_meters",
                  "context_number"]

        

                    
