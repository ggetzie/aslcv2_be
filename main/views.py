from django.http import Http404
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


from main.models import SpatialArea, SpatialContext, ObjectFind, ObjectPhoto
from main.serializers import (SpatialAreaSerializer, SpatialContextSerializer,
                              ObjectFindSerializer)

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


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'

        
class ObjectPhotoUpload(APIView):

    def put(self, request, context_id, format=None):
        
        sc = SpatialContext.objects.get(id=context_id)
        op = ObjectPhoto(user=request.user,
                         context=sc,
                         photo=request.FILES["photo"])
        op.save()
        return Response(status=status.HTTP_201_CREATED)
                         
