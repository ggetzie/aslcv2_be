from django.conf import settings
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

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
    ContextFindListSerializer,
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


@api_view(["GET"])
def find_list_by_context(
    request,
    utm_hemisphere,
    utm_zone,
    area_utm_easting_meters,
    area_utm_northing_meters,
    context_number,
):
    find_numbers = list(
        ObjectFind.objects.filter(
            utm_hemisphere=utm_hemisphere,
            utm_zone=utm_zone,
            area_utm_easting_meters=area_utm_easting_meters,
            area_utm_northing_meters=area_utm_northing_meters,
            context_number=context_number,
        )
        .order_by("find_number")
        .values_list("find_number", flat=True)
    )
    return Response({"find_numbers": find_numbers})


@api_view(["GET"])
def find_detail_hzencf(
    request,
    utm_hemisphere,
    utm_zone,
    area_utm_easting_meters,
    area_utm_northing_meters,
    context_number,
    find_number,
):
    try:
        obj = ObjectFind.objects.get(
            utm_hemisphere=utm_hemisphere,
            utm_zone=utm_zone,
            area_utm_easting_meters=area_utm_easting_meters,
            area_utm_northing_meters=area_utm_northing_meters,
            context_number=context_number,
            find_number=find_number,
        )
        serializer = ObjectFindSerializer(obj)
        d = serializer.data.copy()
        d["findphoto_set"] = obj.list_file_urls_from_photo_folder()
        return Response(d)
    except ObjectFind.DoesNotExist:
        raise Http404


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
        d = serializer.data.copy()
        d["findphoto_set"] = obj.list_file_urls_from_photo_folder()
        return Response(d)

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
        return self.put(request, find_id=find_id, format=format)

    def get(self, request, find_id, format=None):
        obj = ObjectFind.objects.get(id=find_id)
        photo_urls = obj.list_file_urls_from_photo_folder()
        return Response(photo_urls, status=status.HTTP_200_OK)


class FindPhotoReplace(APIView):
    def put(self, request, find_id, format=None):
        obj = ObjectFind.objects.get(id=find_id)
        try:
            filename = request.data["filename"]
        except KeyError:
            return Response(
                {"error": " No filename provided"}, status=status.HTTP_400_BAD_REQUEST
            )
        filepath = obj.absolute_findphoto_folder / filename
        if not filepath.exists():
            upload_url = reverse("api:objectfind_photo", args=[find_id])
            msg = f"{filename} not found in {obj.findphoto_folder} use PUT to {upload_url} to upload a new photo."
            return Response({"error": msg}, status=status.HTTP_404_NOT_FOUND)
        print(request.FILES["photo"])
        filepath.write_bytes(request.FILES["photo"].read())

        _ = ActionLog.objects.create(
            user=request.user,
            model_name=ObjectFind._meta.verbose_name,
            action="U",
            object_id=obj.id,
        )
        return Response(
            {"message": f"{filename} replaced in {obj.findphoto_folder}"},
            status=status.HTTP_200_OK,
        )


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
def find_by_uuid(request, object_id):
    object_find = get_object_or_404(ObjectFind, id=object_id)
    context = {
        "hemisphere": object_find.utm_hemisphere,
        "zone": object_find.utm_zone,
        "easting": object_find.area_utm_easting_meters,
        "northing": object_find.area_utm_northing_meters,
        "find": object_find,
        "spatial_context": object_find.spatial_context,
    }
    return render(request, template_name="main/find_detail.html", context=context)


@login_required
def home_page(request):
    # hzenc = [
    #     "utm_hemisphere",
    #     "utm_zone",
    #     "area_utm_easting_meters",
    #     "area_utm_northing_meters",
    #     "context_number",
    # ]
    # hzencf = hzenc + ["find_number"]
    # distinct_context_finds = ObjectFind.objects.order_by(*hzenc).distinct(*hzenc)
    # distinct_context_photos = ContextPhoto.objects.order_by(*hzenc).distinct(*hzenc)
    # distinct_bag_photos = BagPhoto.objects.order_by(*hzenc).distinct(*hzenc)
    # # distinct_find_photos = FindPhoto.objects.order_by(*hzencf).distinct(*hzencf)
    # distinct_find_photos = [
    #     of for of in ObjectFind.objects.all() if of.list_files_photo_folder()
    # ]

    test_find = ObjectFind.objects.order_by("?").first()

    return render(
        request,
        template_name="pages/home.html",
        context={
            "test_find": test_find,
            "distinct_context_finds": [],
            "distinct_context_photos": [],
            "distinct_bag_photos": [],
            "distinct_find_photos": [],
        },
    )
