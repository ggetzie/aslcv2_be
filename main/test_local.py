"""
Perform some tests against the local database
Must have the ./manage.py runserver running

Import and call from the shell

Current test runner doesn't work with multi-schema setup
TODO: fix that
"""

import datetime
import pathlib
import random

from django.conf import settings
from django.db.models import Max
from django.urls import reverse

import requests

import main.utils as utils
from main.models import (
    SpatialArea,
    AreaType,
    SpatialContext,
    ContextType,
    ObjectFind,
    MaterialCategory,
    ContextPhoto,
    BagPhoto,
    FindPhoto,
    get_next_photo_number,
)
import main.test_helpers as th


class RunningTestInProduction(Exception):
    pass


if not settings.DEBUG:
    raise RunningTestInProduction("Tests must be run in DEBUG mode")

client = th.TestClient()

# SpatialArea: N-38-478130-4419430
test_utm_hemisphere = "N"
test_utm_zone = 38
test_area_utm_easting_meters = 478130
test_area_utm_northing_meters = 4419430
hzen = [
    test_utm_hemisphere,
    test_utm_zone,
    test_area_utm_easting_meters,
    test_area_utm_northing_meters,
]

# SpatialContext: N-38-478130-4419430-1
test_context_number = 1
hzenc = hzen + [test_context_number]


def test_area():
    r = client.get(reverse("api:spatialarea_list"))
    assert r.status_code == 200
    assert SpatialArea.objects.count() == len(r.json())
    print("SpatialArea List OK")

    r = client.get(reverse("api:spatialarea_list_h", args=[test_utm_hemisphere]))
    assert r.status_code == 200
    assert SpatialArea.objects.filter(
        utm_hemisphere=test_utm_hemisphere
    ).count() == len(r.json())
    print("SpatialArea List Hemisphere OK")

    url404 = reverse("api:spatialarea_list_h", args=[test_utm_hemisphere]).replace(
        "/N/", "/Q/"
    )
    r = client.get(url404)
    assert r.status_code == 404
    print("SpatialArea List Hemisphere 404 OK")

    r = client.get(
        reverse("api:spatialarea_list_hz", args=[test_utm_hemisphere, test_utm_zone])
    )
    assert r.status_code == 200
    assert (
        len(r.json())
        == SpatialArea.objects.filter(
            utm_hemisphere=test_utm_hemisphere, utm_zone=test_utm_zone
        ).count()
    )
    print("SpatialArea List Hemisphere Zone OK")

    r = client.get(
        reverse(
            "api:spatialarea_list_hze",
            args=[test_utm_hemisphere, test_utm_zone, test_area_utm_easting_meters],
        )
    )
    assert r.status_code == 200
    assert (
        len(r.json())
        == SpatialArea.objects.filter(
            utm_hemisphere=test_utm_hemisphere,
            utm_zone=test_utm_zone,
            area_utm_easting_meters=test_area_utm_easting_meters,
        ).count()
    )
    print("SpatialArea List Hemisphere Zone Easting OK")

    r = client.get(
        reverse(
            "api:spatialarea_list_hzen",
            args=[
                test_utm_hemisphere,
                test_utm_zone,
                test_area_utm_easting_meters,
                test_area_utm_northing_meters,
            ],
        )
    )
    assert r.status_code == 200
    assert (
        len(r.json())
        == SpatialArea.objects.filter(
            utm_hemisphere=test_utm_hemisphere,
            utm_zone=test_utm_zone,
            area_utm_easting_meters=test_area_utm_easting_meters,
            area_utm_northing_meters=test_area_utm_northing_meters,
        ).count()
    )
    print("SpatialArea List Hemisphere Zone Easting Northing OK")

    sa = SpatialArea.objects.order_by("?").first()
    r = client.get(reverse("api:spatialarea_detail", args=[sa.id]))
    assert r.status_code == 200
    assert r.json()["id"] == str(sa.id)
    print("SpatialArea Detail by uuid OK")


def test_context():
    # test list all spatial contexts
    r = client.get(reverse("api:spatialcontext_list"))
    assert r.status_code == 200
    assert SpatialContext.objects.count() == len(r.json())
    print("List all SpatialContext OK")

    # test filtered list of spatial context
    r = client.get(
        reverse(
            "api:spatialcontext_list_hzen",
            args=[
                test_utm_hemisphere,
                test_utm_zone,
                test_area_utm_easting_meters,
                test_area_utm_northing_meters,
            ],
        )
    )

    assert r.status_code == 200
    assert (
        len(r.json())
        == SpatialContext.objects.filter(
            utm_hemisphere=test_utm_hemisphere,
            utm_zone=test_utm_zone,
            area_utm_easting_meters=test_area_utm_easting_meters,
            area_utm_northing_meters=test_area_utm_northing_meters,
        ).count()
    )
    print("List all SpatialContext Filter URL OK")

    # test create new spatial context
    sc_type = ContextType.objects.order_by("?").first()
    data = {
        "utm_hemisphere": test_utm_hemisphere,
        "utm_zone": test_utm_zone,
        "area_utm_easting_meters": test_area_utm_easting_meters,
        "area_utm_northing_meters": test_area_utm_northing_meters,
        "type": sc_type.type,
    }
    old_max = (
        SpatialContext.objects.filter(
            utm_hemisphere=test_utm_hemisphere,
            utm_zone=test_utm_zone,
            area_utm_easting_meters=test_area_utm_easting_meters,
            area_utm_northing_meters=test_area_utm_northing_meters,
        ).aggregate(Max("context_number"))["context_number__max"]
        or 0
    )

    r = client.post(reverse("api:spatialcontext_list"), data=data)
    assert r.status_code == 201
    assert r.json()["context_number"] == (old_max + 1)
    sc = SpatialContext.objects.get(id=r.json()["id"])
    print("SpatialContext Create OK")
    sc.delete()

    # test get spatial context by uuid
    sc = SpatialContext.objects.order_by("?").first()
    r = client.get(reverse("api:spatialcontext_detail", args=[sc.id]))
    assert r.status_code == 200
    assert r.json()["id"] == str(sc.id)
    print(f"SpatialContext Detail OK")

    # test edit spatial context
    sc = SpatialContext.objects.filter(opening_date__isnull=True).order_by("?").first()
    data = {"opening_date": datetime.date.today()}
    r = client.put(
        reverse("api:spatialcontext_detail", args=[sc.id]),
        data=data,
    )
    assert r.status_code == 200
    sc = SpatialContext.objects.get(id=r.json()["id"])
    assert sc.opening_date == datetime.date.today()
    sc.opening_date = None
    sc.save()
    print("SpatialContext Edit OK")


def test_types():
    r = client.get(reverse("api:spatialarea_types"))
    assert r.status_code == 200
    area_types = AreaType.objects.all()
    res = {i["type"] for i in r.json()}
    for at in area_types:
        assert at.type in res
    print("Spatial Area Types List OK")

    r = client.get(reverse("api:spatialcontext_types"))
    assert r.status_code == 200
    context_types = ContextType.objects.all()
    res = {i["type"] for i in r.json()}
    for ct in context_types:
        assert ct.type in res
    print("Spatial Context Types List OK")


def test_contextphoto_upload():
    sc = SpatialContext.objects.order_by("?").first()
    url = reverse("api:spatialcontext_photo", args=[sc.id])
    photo_path = th.get_test_photo()
    r = client.put(url, data={}, files={"photo": open(photo_path, "rb")})
    assert r.status_code == 201
    p = ContextPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Context Photo upload OK")


def test_bagphoto_upload():
    sc = SpatialContext.objects.order_by("?").first()
    url = reverse("api:spatialcontext_bagphoto", args=[sc.id])
    photo_path = th.get_test_photo()
    r = client.put(
        url,
        data={"source": random.choice(("F", "D"))},
        files={"photo": open(photo_path, "rb")},
    )
    assert r.status_code == 201
    p = BagPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Bag Photo upload OK")


def test_findphoto_upload():
    objFind = ObjectFind.objects.order_by("?").first()
    photo_path = th.get_test_photo()
    url = reverse("api:objectfind_photo", args=[objFind.id])
    r = client.put(url, data=None, files={"photo": open(photo_path, "rb")})
    assert r.status_code == 201
    p = FindPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Find Photo Upload OK")


def test_multiple_findphoto_upload():
    objFind = ObjectFind.objects.order_by("?").first()
    extension = ".jpg"
    photo_folder = pathlib.Path(settings.MEDIA_ROOT) / objFind.findphoto_folder
    largest = max([int(p.stem) for p in photo_folder.glob(f"*{extension}")], default=0)
    expected_1 = f"{largest + 1}{extension}"
    expected_2 = f"{largest + 2}{extension}"
    photo_paths = [th.get_test_photo() for _ in range(2)]
    url = reverse("api:objectfind_photo", args=[objFind.id])
    r = client.put(url, data=None, files={"photo": open(photo_paths[0], "rb")})
    assert r.status_code == 201
    assert pathlib.Path(photo_folder / expected_1).exists()
    r = client.put(url, data=None, files={"photo": open(photo_paths[1], "rb")})
    assert r.status_code == 201
    assert pathlib.Path(photo_folder / expected_2).exists()
    print("Multiple Find Photo Upload OK")


def test_findphoto_list():
    objFind = th.get_random_find_with_photos()
    url = reverse("api:objectfind_photo", args=[objFind.id])
    r = client.get(url)
    assert r.status_code == 200
    for p in r.json():
        fp = pathlib.Path(settings.MEDIA_ROOT) / p.replace(settings.MEDIA_URL, "")
        assert fp.exists()
    print("Find Photo List OK")


def test_findphoto_replace(find_id=None, filename=None):
    objFind = (
        th.get_random_find_with_photos(extension=".jpg")
        if not find_id
        else ObjectFind.objects.get(id=find_id)
    )

    # test happy path - replace a photo with a new one
    old_photo_path = (
        random.choice(objFind.list_files_photo_folder(extension=".jpg"))
        if not filename
        else objFind.absolute_findphoto_folder / filename
    )
    assert old_photo_path.exists()
    old_hash = th.get_file_hash(old_photo_path)
    filename = old_photo_path.name

    new_photo_path = pathlib.Path(
        th.get_test_photo(extension=".jpg", hash_is_not=old_hash)
    )
    new_hash = th.get_file_hash(new_photo_path)

    url = reverse("api:objectfind_photo_replace", args=[objFind.id])
    r = client.put(
        url, data={"filename": filename}, files={"photo": open(new_photo_path, "rb")}
    )
    assert r.status_code == 200

    uploaded = objFind.absolute_findphoto_folder / filename
    assert uploaded.exists()
    assert th.get_file_hash(uploaded) == new_hash

    # test replacing a photo that doesn't exist
    filename = "nonexistent.jpg"
    url = reverse("api:objectfind_photo_replace", args=[objFind.id])
    r = client.put(
        url, data={"filename": filename}, files={"photo": open(new_photo_path, "rb")}
    )
    assert r.status_code == 404

    print("Find Photo Replace OK")


def test_objectfind():
    # test get all object finds
    all_obj_url = reverse("api:objectfind_list")
    r = client.get(all_obj_url)
    assert r.status_code == 200
    data = r.json()
    assert ObjectFind.objects.count() == data["count"]
    print("List all ObjectFinds OK")

    # test filter object finds by hzenc
    hzenc_url = reverse(
        "api:objectfind_list_hzenc",
        args=hzenc,
    )
    r = client.get(hzenc_url)
    received = r.json()
    assert r.status_code == 200
    assert (
        received["count"]
        == ObjectFind.objects.filter(
            utm_hemisphere=test_utm_hemisphere,
            utm_zone=test_utm_zone,
            area_utm_easting_meters=test_area_utm_easting_meters,
            area_utm_northing_meters=test_area_utm_northing_meters,
            context_number=test_context_number,
        ).count()
    )
    print("Filter ObjectFinds list OK")

    # test creating new find
    data = {
        "utm_hemisphere": "N",
        "utm_zone": 38,
        "area_utm_easting_meters": 478850,
        "area_utm_northing_meters": 4419560,
        "context_number": 1,
        "material": "pottery",
        "category": "rim",
        "weight_grams": "21332.65",
    }
    r = client.post(all_obj_url, data)
    assert r.status_code == 201
    print("Create ObjectFind OK")


def test_objectfind_detail():
    obj = ObjectFind.objects.order_by("?").first()
    url = reverse("api:objectfind_detail", args=[obj.id])
    r = client.get(url)
    assert r.status_code == 200
    data = r.json()
    assert str(obj.id) == data["id"]
    print("Get object find detail OK")

    new_note = obj.director_notes + " edited" if obj.director_notes else "edited"
    data = {"director_notes": new_note, "weight_grams": "99999.69"}
    r = client.put(url, data=data)
    assert r.status_code == 200
    assert r.json()["director_notes"] == new_note
    assert r.json()["weight_grams"] == data["weight_grams"]
    print("Edit object find detail OK")


def test_contextfind_list():
    sc = th.get_random_context_with_finds()
    url = reverse("api:contextfind_list", args=sc.hzenc_list())
    want = list(
        ObjectFind.objects.filter(**sc.hzenc_dict())
        .order_by("find_number")
        .values_list("find_number", flat=True)
    )

    r = client.get(url)
    got = r.json()["find_numbers"]
    assert r.status_code == 200
    assert got == want
    print("Context Find List OK")


def test_find_detail_hzencf():
    want = th.get_random_object_find()
    url = reverse("api:find_detail_hzencf", args=want.hzencf_list())
    r = client.get(url)
    got = r.json()
    assert r.status_code == 200
    assert got["id"] == str(want.id)
    print("Find Detail by HZENCF OK")


def test_mc_list():
    mcs = MaterialCategory.objects.all()
    url = reverse("api:materialcategory_list")
    r = client.get(url)
    assert r.status_code == 200
    assert mcs.count() == len(r.json())
    print("Material Category list OK")


def test_all():
    test_area()
    test_context()
    test_types()
    test_contextphoto_upload()
    test_bagphoto_upload()
    test_objectfind()
    test_objectfind_detail()
    test_mc_list()
    test_findphoto_upload()
    test_multiple_findphoto_upload()
    test_findphoto_replace()
    test_contextfind_list()
