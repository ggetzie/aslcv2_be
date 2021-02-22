from django.http import Http404
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


from main.models import (FindPhoto, SpatialArea, SpatialContext, ObjectFind, ContextPhoto,
                         AreaType, ContextType, ActionLog, BagPhoto, MaterialCategory)

from main.serializers import (FindPhotoSerializer, SpatialAreaSerializer, SpatialContextSerializer,
                              SpatialContextEditSerializer, AreaTypeSerializer,
                              ContextTypeSerializer, ContextPhotoSerializer,
                              BagPhotoSerializer, ObjectFindSerializer, MCSerializer)

FILTER_VARS = ["utm_hemisphere",
               "utm_zone",
               "area_utm_easting_meters",
               "area_utm_northing_meters"]

# api views
class SpatialAreaList(ListAPIView):
    serializer_class = SpatialAreaSerializer
    model = SpatialArea
    paginate_by = 100

    def get_queryset(self):
        qs = SpatialArea.objects.all()
        for var in FILTER_VARS:
            if var in self.kwargs:
                qs = qs.filter(**{var: self.kwargs[var]})
            elif var in self.request.GET:
                val = self.request.GET[var].strip('"\' ')
                qs = qs.filter(**{var: int(val) if val.isnumeric() else val})
        return qs


class SpatialAreaDetail(APIView):

    def get_object(self, area_id):
        try:
            res = SpatialArea.objects.get(id=area_id)
            return res
        except SpatialArea.DoesNotExist:
            raise Http404

    def get(self, request, area_id, format=None):
        sa = self.get_object(area_id)
        serializer = SpatialAreaSerializer(sa)
        _ = ActionLog.objects.create(user=self.request.user,
                                         model_name=SpatialArea._meta.verbose_name,
                                         action="R",
                                         object_id=area_id)
        return Response(serializer.data)


class SpatialContextList(ListCreateAPIView):
    serializer_class = SpatialContextSerializer

    def get_queryset(self):
        qs = SpatialContext.objects.all()
        for var in FILTER_VARS:
            if var in self.kwargs:
                qs = qs.filter(**{var: self.kwargs[var]})
            elif var in self.request.GET:
                val = self.request.GET[var].strip('"\' ')
                qs = qs.filter(**{var: int(val) if val.isnumeric() else val})
        return qs
    

    def post(self, request, format=None):
        serializer = SpatialContextEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            _ = ActionLog.objects.create(user=request.user,
                                         model_name=SpatialContext._meta.verbose_name,
                                         action="C",
                                         object_id=serializer.data["id"])
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
        _ = ActionLog.objects.create(user=request.user,
                                     model_name=SpatialContext._meta.verbose_name,
                                     action="R",
                                     object_id=context_id)
        serializer = SpatialContextSerializer(sc)
        return Response(serializer.data)

    def put(self, request, context_id, format=None):
        sc = self.get_object(context_id)
        _ = ActionLog.objects.create(user=request.user,
                                     model_name=SpatialContext._meta.verbose_name,
                                     action="U",
                                     object_id=context_id)
        serializer = SpatialContextEditSerializer(sc,
                                                  data=request.data,
                                                  partial=True)
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
        _ = ActionLog.objects.create(user=self.request.user,
                                     model_name=ContextPhoto._meta.verbose_name,
                                     action="C",
                                     object_id=op.id)
        ser = ContextPhotoSerializer(op)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class BagPhotoUpload(APIView):

    def put(self, request, context_id, format=None):
        sc = SpatialContext.objects.get(id=context_id)
        bp = BagPhoto(user=request.user,
                      utm_hemisphere=sc.utm_hemisphere,
                      utm_zone=sc.utm_zone,
                      area_utm_easting_meters=sc.area_utm_easting_meters,
                      area_utm_northing_meters=sc.area_utm_northing_meters,
                      context_number=sc.context_number,
                      source=request.data["source"],
                      photo=request.FILES["photo"])
        bp.save()
        _ = ActionLog.objects.create(user=request.user,
                                     model_name=BagPhoto._meta.verbose_name,
                                     action="C",
                                     object_id=bp.id)
        ser = BagPhotoSerializer(bp)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ObjectFindList(ListCreateAPIView):
    serializer_class = ObjectFindSerializer

    def get_queryset(self):
        qs = ObjectFind.objects.all()
        fv = FILTER_VARS + ["context_number"]
        fd = {v: self.kwargs[v] for v in fv if v in self.kwargs}
        if fd:
            qs = qs.filter(**fd)
        return qs

    def post(self, request, format=None):
        serializer = ObjectFindSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            _ = ActionLog.objects.create(user=request.user,
                                         model_name=ObjectFind._meta.verbose_name,
                                         action="C",
                                         object_id=serializer.data["id"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObjectFindDetail(APIView):

    def get_object(self, find_id):
        try:
            return ObjectFind.objects.get(id=find_id)
        except ObjectFind.DoesNotExist:
            raise Http404

    def get(self, request, find_id, format=None):
        obj = self.get_object(find_id)
        _ = ActionLog.objects.create(user=request.user,
                                     model_name=ObjectFind._meta.verbose_name,
                                     action="R",
                                     object_id=find_id)
        serializer=ObjectFindSerializer(obj)
        return Response(serializer.data)

    def put(self, request, find_id, format=None):
        obj = self.get_object(find_id)
        _ = ActionLog.objects.create(user=request.user,
                                     model_name=ObjectFind._meta.verbose_name,
                                     action="U",
                                     object_id=find_id)
        serializer = ObjectFindSerializer(obj,
                                          data=request.data,
                                          partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FindPhotoUpload(APIView):

    def put(self, request, find_id, format=None):
        obj = ObjectFind.objects.get(id=find_id)
        fp = FindPhoto(user=request.user,
                       utm_hemisphere=obj.utm_hemisphere,
                       utm_zone=obj.utm_zone,
                       area_utm_easting_meters=obj.area_utm_easting_meters,
                       area_utm_northing_meters=obj.area_utm_northing_mmeters,
                       context_number=obj.context_number,
                       find_number=obj.find_number,
                       photo=request.FILES["photo"])
        fp.save()
        _ = ActionLog.objects.create(user=request.user,
                                     model_name=FindPhoto._meta.verbose_name,
                                     action="C",
                                     object_id=fp.id)
        ser = FindPhotoSerializer(fp)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class AreaTypeList(ListAPIView):
    model = AreaType
    serializer_class = AreaTypeSerializer
    queryset = AreaType.objects.all()


class ContextTypeList(ListAPIView):
    model = ContextType
    serializer_class = ContextTypeSerializer
    queryset = ContextType.objects.all()
    

class MCList(ListAPIView):
    model = MaterialCategory
    serializer_class = MCSerializer
    queryset = MaterialCategory.objects.all()