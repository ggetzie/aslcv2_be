from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


from main.models import (
    FindPhoto,
    SpatialArea,
    SpatialContext,
    ObjectFind,
    ContextPhoto,
    AreaType,
    ContextType,
    ActionLog,
    BagPhoto,
    MaterialCategory,
    SurveyPath,
    SurveyPoint,
)

from main.serializers import (
    FindPhotoSerializer,
    SpatialAreaSerializer,
    SpatialContextSerializer,
    SpatialContextEditSerializer,
    AreaTypeSerializer,
    ContextTypeSerializer,
    ContextPhotoSerializer,
    BagPhotoSerializer,
    ObjectFindSerializer,
    MCSerializer,
    SurveyPathSerializer,
    SurveyPathListSerializer,
)

import logging

logger = logging.getLogger(__name__)

FILTER_VARS = [
    "utm_hemisphere",
    "utm_zone",
    "area_utm_easting_meters",
    "area_utm_northing_meters",
]


# api views
class SpatialAreaList(ListAPIView):
    serializer_class = SpatialAreaSerializer
    model = SpatialArea
    # paginate_by = 100
    pagination_class = None

    def get_queryset(self):
        qs = SpatialArea.objects.all()
        for var in FILTER_VARS:
            if var in self.kwargs:
                qs = qs.filter(**{var: self.kwargs[var]})
            elif var in self.request.GET:
                val = self.request.GET[var].strip("\"' ")
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
        _ = ActionLog.objects.create(
            user=self.request.user,
            model_name=SpatialArea._meta.verbose_name,
            action="R",
            object_id=area_id,
        )
        return Response(serializer.data)


class SpatialContextList(ListCreateAPIView):
    serializer_class = SpatialContextSerializer
    pagination_class = None

    def get_queryset(self):
        qs = SpatialContext.objects.all()
        for var in FILTER_VARS:
            if var in self.kwargs:
                qs = qs.filter(**{var: self.kwargs[var]})
            elif var in self.request.GET:
                val = self.request.GET[var].strip("\"' ")
                qs = qs.filter(**{var: int(val) if val.isnumeric() else val})
        return qs

    def post(self, request, format=None):
        serializer = SpatialContextEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            _ = ActionLog.objects.create(
                user=request.user,
                model_name=SpatialContext._meta.verbose_name,
                action="C",
                object_id=serializer.data["id"],
            )
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
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=SpatialContext._meta.verbose_name,
            action="R",
            object_id=context_id,
        )
        serializer = SpatialContextSerializer(sc)
        return Response(serializer.data)

    def put(self, request, context_id, format=None):
        sc = self.get_object(context_id)
        logger.info(f"Updating context {context_id}")
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=SpatialContext._meta.verbose_name,
            action="U",
            object_id=context_id,
        )
        data = request.data.copy()
        if data.get("director_notes", "") is None:
            data["director_notes"] = ""
        if data.get("description", "") is None:
            data["description"] = ""

        serializer = SpatialContextEditSerializer(sc, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Saved data {serializer.data}")
            return Response(serializer.data)
        logger.info(f"Update Context errors {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageUploadParser(FileUploadParser):
    media_type = "image/*"


class ContextPhotoUpload(APIView):
    def put(self, request, context_id, format=None):
        logger.info("In context photo put upload")
        # return Response(f"ok", status=status.HTTP_201_CREATED)
        sc = SpatialContext.objects.get(id=context_id)

        logger.info(f"sc = {sc}")
        logger.info(request.FILES["photo"])
        op = ContextPhoto(
            user=request.user,
            utm_hemisphere=sc.utm_hemisphere,
            utm_zone=sc.utm_zone,
            area_utm_easting_meters=sc.area_utm_easting_meters,
            area_utm_northing_meters=sc.area_utm_northing_meters,
            context_number=sc.context_number,
            photo=request.FILES["photo"],
        )

        op.save()
        logger.info(op)
        _ = ActionLog.objects.create(
            user=self.request.user,
            model_name=ContextPhoto._meta.verbose_name,
            action="C",
            object_id=op.id,
        )
        ser = ContextPhotoSerializer(op)
        logger.info(ser)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class BagPhotoUpload(APIView):
    def put(self, request, context_id, format=None):
        sc = SpatialContext.objects.get(id=context_id)
        bp = BagPhoto(
            user=request.user,
            utm_hemisphere=sc.utm_hemisphere,
            utm_zone=sc.utm_zone,
            area_utm_easting_meters=sc.area_utm_easting_meters,
            area_utm_northing_meters=sc.area_utm_northing_meters,
            context_number=sc.context_number,
            source=request.data["source"],
            photo=request.FILES["photo"],
        )
        bp.save()
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=BagPhoto._meta.verbose_name,
            action="C",
            object_id=bp.id,
        )
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
        logger.info(f"ObjectFindList post {request.data}")
        if serializer.is_valid():
            serializer.save()
            _ = ActionLog.objects.create(
                user=request.user,
                model_name=ObjectFind._meta.verbose_name,
                action="C",
                object_id=serializer.data["id"],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # required_fields = [
        #     "utm_hemisphere",
        #     "utm_zone",
        #     "area_utm_easting_meters",
        #     "area_utm_northing_meters",
        #     "context_number",
        # ]
        # errmsg = ""
        # if all([f in request.data for f in required_fields]):
        #     new_find = ObjectFind(**request.data)
        #     try:
        #         new_find.save()
        #         serializer = ObjectFindSerializer(new_find)
        #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        #     except IntegrityError as e:
        #         print(e)
        #         errmsg = "Invalid Data"
        #         return Response({"error": errmsg}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     errmsg = "Missing required fields"
        #     return Response({"error", errmsg}, status=status.HTTP_400_BAD_REQUEST)


class ObjectFindDetail(APIView):
    def get_object(self, find_id):
        try:
            return ObjectFind.objects.get(id=find_id)
        except ObjectFind.DoesNotExist:
            raise Http404

    def get(self, request, find_id, format=None):
        obj = self.get_object(find_id)
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=ObjectFind._meta.verbose_name,
            action="R",
            object_id=find_id,
        )
        serializer = ObjectFindSerializer(obj)
        return Response(serializer.data)

    def put(self, request, find_id, format=None):
        obj = self.get_object(find_id)
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=ObjectFind._meta.verbose_name,
            action="U",
            object_id=find_id,
        )
        serializer = ObjectFindSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FindPhotoUpload(APIView):
    def put(self, request, find_id, format=None):
        obj = ObjectFind.objects.get(id=find_id)
        fp = FindPhoto(
            user=request.user,
            utm_hemisphere=obj.utm_hemisphere,
            utm_zone=obj.utm_zone,
            area_utm_easting_meters=obj.area_utm_easting_meters,
            area_utm_northing_meters=obj.area_utm_northing_meters,
            context_number=obj.context_number,
            find_number=obj.find_number,
            photo=request.FILES["photo"],
        )
        fp.save()
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=FindPhoto._meta.verbose_name,
            action="C",
            object_id=fp.id,
        )
        ser = FindPhotoSerializer(fp)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def post(self, request, find_id, format=None):
        obj = ObjectFind.objects.get(id=find_id)
        fp = FindPhoto(
            user=request.user,
            utm_hemisphere=obj.utm_hemisphere,
            utm_zone=obj.utm_zone,
            area_utm_easting_meters=obj.area_utm_easting_meters,
            area_utm_northing_meters=obj.area_utm_northing_meters,
            context_number=obj.context_number,
            find_number=obj.find_number,
            photo=request.FILES["photo"],
        )
        fp.save()
        _ = ActionLog.objects.create(
            user=request.user,
            model_name=FindPhoto._meta.verbose_name,
            action="C",
            object_id=fp.id,
        )
        ser = FindPhotoSerializer(fp)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class AreaTypeList(ListAPIView):
    model = AreaType
    serializer_class = AreaTypeSerializer
    queryset = AreaType.objects.all()
    pagination_class = None


class ContextTypeList(ListAPIView):
    model = ContextType
    serializer_class = ContextTypeSerializer
    queryset = ContextType.objects.all()
    pagination_class = None


class MCList(ListAPIView):
    model = MaterialCategory
    serializer_class = MCSerializer
    queryset = MaterialCategory.objects.all()
    pagination_class = None


class SurveyPathList(ListCreateAPIView):
    model = SurveyPath
    serializer_class = SurveyPathSerializer
    queryset = SurveyPath.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SurveyPathListSerializer
        else:
            return SurveyPathSerializer

    def post(self, *args, **kwargs):
        ser = SurveyPathSerializer(data=self.request.data)
        print(self.request.data)
        print()
        if ser.is_valid():
            print(ser.validated_data)
        else:
            print(ser.errors)

        return super().post(*args, **kwargs)


class SurveyPathDetail(RetrieveUpdateAPIView):
    model = SurveyPath
    serializer_class = SurveyPathSerializer
    queryset = SurveyPath.objects.all()


@login_required
def hemisphere_select(request):
    hemispheres = (
        SpatialArea.objects.order_by("utm_hemisphere")
        .distinct("utm_hemisphere")
        .values_list("utm_hemisphere", flat=True)
    )
    context = {"hemispheres": hemispheres}
    return render(request, template_name="main/hemisphere_select.html", context=context)


@login_required
def zone_select(request, hemisphere):
    zones = (
        SpatialArea.objects.filter(utm_hemisphere=hemisphere)
        .order_by("utm_zone")
        .distinct("utm_zone")
        .values_list("utm_zone", flat=True)
    )
    context = {
        "hemisphere": hemisphere,
        "zones": zones,
    }
    return render(request, template_name="main/zone_select.html", context=context)


@login_required
def easting_select(request, hemisphere, zone):
    eastings = (
        SpatialArea.objects.filter(utm_hemisphere=hemisphere, utm_zone=zone)
        .order_by("area_utm_easting_meters")
        .distinct("area_utm_easting_meters")
        .values_list("area_utm_easting_meters", flat=True)
    )
    context = {"hemisphere": hemisphere, "zone": zone, "eastings": eastings}

    return render(request, template_name="main/easting_select.html", context=context)


@login_required
def northing_select(request, hemisphere, zone, easting):
    northings = (
        SpatialArea.objects.filter(
            utm_hemisphere=hemisphere, utm_zone=zone, area_utm_easting_meters=easting
        )
        .order_by("area_utm_northing_meters")
        .distinct("area_utm_northing_meters")
        .values_list("area_utm_northing_meters", flat=True)
    )
    context = {
        "hemisphere": hemisphere,
        "zone": zone,
        "easting": easting,
        "northings": northings,
    }
    return render(request, template_name="main/northing_select.html", context=context)


@login_required
def spatialcontext_select(request, hemisphere, zone, easting, northing):
    area = get_object_or_404(
        SpatialArea,
        utm_hemisphere=hemisphere,
        utm_zone=zone,
        area_utm_easting_meters=easting,
        area_utm_northing_meters=northing,
    )
    spatial_contexts = area.spatialcontext_set
    context = {
        "hemisphere": hemisphere,
        "zone": zone,
        "easting": easting,
        "northing": northing,
        "spatial_contexts": spatial_contexts,
    }
    return render(
        request, template_name="main/spatialcontext_select.html", context=context
    )


@login_required
def find_select(request, hemisphere, zone, easting, northing, context_number):
    spatial_context = get_object_or_404(
        SpatialContext,
        utm_hemisphere=hemisphere,
        utm_zone=zone,
        area_utm_easting_meters=easting,
        area_utm_northing_meters=northing,
        context_number=context_number,
    )
    finds = ObjectFind.objects.filter(
        utm_hemisphere=hemisphere,
        utm_zone=zone,
        area_utm_easting_meters=easting,
        area_utm_northing_meters=northing,
        context_number=context_number,
    )

    context = {
        "hemisphere": hemisphere,
        "zone": zone,
        "easting": easting,
        "northing": northing,
        "spatial_context": spatial_context,
        "finds": finds,
    }
    return render(request, template_name="main/find_select.html", context=context)


@login_required
def find_detail(
    request, hemisphere, zone, easting, northing, context_number, find_number
):
    object_find = get_object_or_404(
        ObjectFind,
        utm_hemisphere=hemisphere,
        utm_zone=zone,
        area_utm_easting_meters=easting,
        area_utm_northing_meters=northing,
        context_number=context_number,
        find_number=find_number,
    )
    context = {
        "hemisphere": hemisphere,
        "zone": zone,
        "easting": easting,
        "northing": northing,
        "find": object_find,
        "spatial_context": object_find.spatial_context,
    }
    return render(request, template_name="main/find_detail.html", context=context)


@login_required
def home_page(request):
    hzenc = [
        "utm_hemisphere",
        "utm_zone",
        "area_utm_easting_meters",
        "area_utm_northing_meters",
        "context_number",
    ]
    hzencf = hzenc + ["find_number"]
    distinct_context_finds = ObjectFind.objects.order_by(*hzenc).distinct(*hzenc)
    distinct_context_photos = ContextPhoto.objects.order_by(*hzenc).distinct(*hzenc)
    distinct_bag_photos = BagPhoto.objects.order_by(*hzenc).distinct(*hzenc)
    distinct_find_photos = FindPhoto.objects.order_by(*hzencf).distinct(*hzencf)

    return render(
        request,
        template_name="pages/home.html",
        context={
            "distinct_context_finds": distinct_context_finds,
            "distinct_context_photos": distinct_context_photos,
            "distinct_bag_photos": distinct_bag_photos,
            "distinct_find_photos": distinct_find_photos,
        },
    )
