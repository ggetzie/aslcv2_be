from django.http import Http404
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


from main.models import (SpatialArea, SpatialContext, ObjectFind, ContextPhoto,
                         AreaType, ContextType)
from main.serializers import (SpatialAreaSerializer, SpatialContextSerializer,
                              SpatialContextEditSerializer, AreaTypeSerializer,
                              ContextTypeSerializer, ContextPhotoSerializer)

# api views
class SpatialAreaList(ListAPIView):
    serializer_class = SpatialAreaSerializer
    model = SpatialArea
    paginate_by = 100

    def get_queryset(self):
        qs = SpatialArea.objects.all()
        for var in ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters"]:
            if var in self.kwargs:
                qs = qs.filter(**{var: self.kwargs[var]})
        return qs


class SpatialAreaDetail(APIView):

    def get_object(self, area_id):
        try:
            return SpatialArea.objects.get(id=area_id)
        except SpatialArea.DoesNotExist:
            raise Http404

    def get(self, request, area_id, format=None):
        sa = self.get_object(area_id)
        serializer = SpatialAreaSerializer(sa)
        return Response(serializer.data)


class SpatialContextList(ListCreateAPIView):
    serializer_class = SpatialContextSerializer

    def get_queryset(self):
        vars = ["utm_hemisphere",
                "utm_zone",
                "area_utm_easting_meters",
                "area_utm_northing_meters"]
        qs = SpatialContext.objects.all()
        if all([v in self.kwargs for v in vars]):
            qs = qs.filter(**{var: self.kwargs[var] for var in vars})
        return qs
    

    def post(self, request, format=None):
        serializer = SpatialContextEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpatialContextDetail(APIView):
    def get_object(self, context_id):
        try:
            return SpatialContext.objects.get(id=context_id)
        except SpatialContext.DoesNotExist:
            raise Http404

    def get(self, request, context_id, format=None):
        sc = self.get_object(context_id)
        serializer = SpatialContextSerializer(sc)
        return Response(serializer.data)

    def put(self, request, context_id, format=None):
        sc = self.get_object(context_id)
        serializer = SpatialContextEditSerializer(sc, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'

        
class ContextPhotoUpload(APIView):

    def put(self, request, context_id, format=None):
        
        sc = SpatialContext.objects.get(id=context_id)
        op = ContextPhoto(user=request.user,
                          utm_hemisphere=sc.utm_hemisphere,
                          utm_zone=sc.utm_zone,
                          area_utm_easting_meters=sc.area_utm_easting_meters,
                          area_utm_northing_meters=sc.area_utm_northing_meters,
                          context_number=sc.context_number,
                          photo=request.FILES["photo"])
        op.save()
        ser = ContextPhotoSerializer(op)
        return Response(ser.data, status=status.HTTP_201_CREATED)
    

class AreaTypeList(ListAPIView):
    model = AreaType
    serializer_class = AreaTypeSerializer
    queryset = AreaType.objects.all()


class ContextTypeList(ListAPIView):
    model = ContextType
    serializer_class = ContextTypeSerializer
    queryset = ContextType.objects.all()
                         
