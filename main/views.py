from django.http import Http404
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import SpatialArea, SpatialContext, ObjectFind, ObjectPhoto
from main.serializers import (SpatialAreaSerializer, SpatialContextSerializer,
                              ObjectFindSerializer, ObjectPhotoSerializer)

# api views
class SpatialAreaList(APIView):

    def get(self, request, format=None):
        qs = SpatialArea.objects.all()
        for var in ["utm_hemisphere",
                    "utm_zone",
                    "area_utm_easting_meters",
                    "area_utm_northing_meters"]:
            if var in request.GET:
                qs = qs.filter(**{var: request.GET[var]})
        serializer = SpatialAreaSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SpatialAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpatialAreaDetail(APIView):

    def get_object(self, pk):
        try:
            return SpatialArea.objects.get(pk=pk)
        except SpatialArea.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        sa = self.get_object(pk)
        serializer = SpatialAreaSerializer(sa)
        return Response(serializer.data)


class SpatialContextDetail(APIView):
    def get_object(self, pk):
        try:
            return SpatialContext.objects.get(pk=pk)
        except SpatialContext.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        sc = self.get_object(pk)
        serializer = SpatialContextSerializer(sc)
        return Response(serializer.data)

    
class ObjectFindDetail(APIView):
    def get_object(self, pk):
        try:
            return ObjectFind.objects.get(pk=pk)
        except ObjectFind.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ObjectFindSerializer(obj)
        return Response(serializer.data)
        
        
