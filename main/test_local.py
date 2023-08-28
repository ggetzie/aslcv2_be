"""
Perform some tests against the local database
Must have the ./manage.py runserver running

Import and call from the shell

Current test runner doesn't work with multi-schema setup
TODO: fix that
"""
import datetime
import decimal
import glob
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
)

headers = utils.get_test_header()
base_url = "http://127.0.0.1:8000"
PHOTO_DIR = "/mnt/c/Users/gabe/OneDrive - The University of Hong Kong/Pictures"

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

all_sa = SpatialArea.objects.all()
sa_h = SpatialArea.objects.filter(utm_hemisphere=test_utm_hemisphere)
sa_hz = SpatialArea.objects.filter(
    utm_hemisphere=test_utm_hemisphere, utm_zone=test_utm_zone
)
sa_hze = SpatialArea.objects.filter(
    utm_hemisphere=test_utm_hemisphere,
    utm_zone=test_utm_zone,
    area_utm_easting_meters=test_area_utm_easting_meters,
)

sa_hzen = SpatialArea.objects.filter(
    utm_hemisphere=test_utm_hemisphere,
    utm_zone=test_utm_zone,
    area_utm_easting_meters=test_area_utm_easting_meters,
    area_utm_northing_meters=test_area_utm_northing_meters,
)

all_sc = SpatialContext.objects.all()

sc_hzen = SpatialContext.objects.filter(
    utm_hemisphere=test_utm_hemisphere,
    utm_zone=test_utm_zone,
    area_utm_easting_meters=test_area_utm_easting_meters,
    area_utm_northing_meters=test_area_utm_northing_meters,
)

all_obj = ObjectFind.objects.all()

obj_hzenc = ObjectFind.objects.filter(
    utm_hemisphere=test_utm_hemisphere,
    utm_zone=test_utm_zone,
    area_utm_easting_meters=test_area_utm_easting_meters,
    area_utm_northing_meters=test_area_utm_northing_meters,
    context_number=test_context_number,
)


def test_area():
    r = requests.get(base_url + reverse("api:spatialarea_list"), headers=headers)
    assert r.status_code == 200
    assert all_sa.count() == len(r.json())
    print("SpatialArea List OK")

    r = requests.get(
        base_url + reverse("api:spatialarea_list_h", args=[test_utm_hemisphere]),
        headers=headers,
    )
    assert r.status_code == 200
    assert sa_h.count() == len(r.json())
    print("SpatialArea List Hemisphere OK")

    url404 = (
        base_url + reverse("api:spatialarea_list_h", args=[test_utm_hemisphere])
    ).replace("/N/", "/Q/")
    r = requests.get(url404, headers=headers)
    assert r.status_code == 404
    print("SpatialArea List Hemisphere 404 OK")

    r = requests.get(
        base_url
        + reverse("api:spatialarea_list_hz", args=[test_utm_hemisphere, test_utm_zone]),
        headers=headers,
    )
    assert r.status_code == 200
    assert sa_hz.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone OK")

    r = requests.get(
        base_url
        + reverse(
            "api:spatialarea_list_hze",
            args=[test_utm_hemisphere, test_utm_zone, test_area_utm_easting_meters],
        ),
        headers=headers,
    )
    assert r.status_code == 200
    assert sa_hze.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone Easting OK")

    r = requests.get(
        base_url
        + reverse(
            "api:spatialarea_list_hzen",
            args=[
                test_utm_hemisphere,
                test_utm_zone,
                test_area_utm_easting_meters,
                test_area_utm_northing_meters,
            ],
        ),
        headers=headers,
    )
    assert r.status_code == 200
    assert sa_hzen.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone Easting Northing OK")

    r = requests.get(
        base_url + reverse("api:spatialarea_detail", args=[sa_hzen[0].id]),
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["id"] == str(sa_hzen[0].id)
    print("SpatialArea Detail by uuid OK")


def test_context():
    # test list all spatial contexts
    r = requests.get(base_url + reverse("api:spatialcontext_list"), headers=headers)
    assert r.status_code == 200
    assert all_sc.count() == len(r.json())
    print("List all SpatialContext OK")

    # test filtered list of spatial context
    r = requests.get(
        base_url
        + reverse(
            "api:spatialcontext_list_hzen",
            args=[
                test_utm_hemisphere,
                test_utm_zone,
                test_area_utm_easting_meters,
                test_area_utm_northing_meters,
            ],
        ),
        headers=headers,
    )

    assert r.status_code == 200
    assert sc_hzen.count() == len(r.json())
    print("List all SpatialContext Filter URL OK")

    # test create new spatial context
    sc_type = random.choice(ContextType.objects.all())
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

    r = requests.post(
        base_url + reverse("api:spatialcontext_list"), headers=headers, data=data
    )
    assert r.status_code == 201
    assert r.json()["context_number"] == (old_max + 1)
    sc = SpatialContext.objects.get(id=r.json()["id"])
    print("SpatialContext Create OK")
    sc.delete()

    # test get spatial context by uuid
    sc = random.choice(SpatialContext.objects.all())
    r = requests.get(
        base_url + reverse("api:spatialcontext_detail", args=[sc.id]), headers=headers
    )
    assert r.status_code == 200
    assert r.json()["id"] == str(sc.id)
    print(f"SpatialContext Detail OK")

    # test edit spatial context
    sc = random.choice(SpatialContext.objects.filter(opening_date__isnull=True))
    data = {"opening_date": datetime.date.today()}
    r = requests.put(
        base_url + reverse("api:spatialcontext_detail", args=[sc.id]),
        headers=headers,
        data=data,
    )
    assert r.status_code == 200
    sc = SpatialContext.objects.get(id=r.json()["id"])
    assert sc.opening_date == datetime.date.today()
    sc.opening_date = None
    sc.save()
    print("SpatialContext edit OK")


def test_types():
    r = requests.get(base_url + reverse("api:spatialarea_types"), headers=headers)
    assert r.status_code == 200
    area_types = AreaType.objects.all()
    res = {i["type"] for i in r.json()}
    for at in area_types:
        assert at.type in res
    print("Spatial Area Types List OK")

    r = requests.get(base_url + reverse("api:spatialcontext_types"), headers=headers)
    assert r.status_code == 200
    context_types = ContextType.objects.all()
    res = {i["type"] for i in r.json()}
    for ct in context_types:
        assert ct.type in res
    print("Spatial Context Types List OK")


def test_photo_upload():
    sc = random.choice(SpatialContext.objects.all())
    url = base_url + reverse("api:spatialcontext_photo", args=[sc.id])
    print(url)
    photo_path = random.choice(glob.glob(f"{PHOTO_DIR}*.jpg"))
    print(photo_path)

    r = requests.post(url, headers=headers, files={"photo": open(photo_path, "rb")})
    assert r.status_code == 201
    p = ContextPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Context Photo upload OK")


def test_bagphoto_upload():
    sc = random.choice(SpatialContext.objects.all())
    url = base_url + reverse("api:spatialcontext_bagphoto", args=[sc.id])
    photo_path = random.choice(glob.glob(f"{PHOTO_DIR}*.jpg"))
    r = requests.put(
        url,
        data={"source": "F"},
        headers=headers,
        files={"photo": open(photo_path, "rb")},
    )
    assert r.status_code == 201
    p = BagPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Finds Bag Photo upload OK")


def test_findphoto_upload():
    find = random.choice(all_obj)
    url = base_url + reverse("api:objectfind_photo", args=[find.id])
    photo_path = random.choice(glob.glob(f"{PHOTO_DIR}/*.jpg"))
    r = requests.put(url, headers=headers, files={"photo": open(photo_path, "rb")})
    print(r.json())
    assert r.status_code == 201


def test_objectfind():
    # test get all object finds
    all_obj_url = base_url + reverse("api:objectfind_list")
    r = requests.get(all_obj_url, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert all_obj.count() == data["count"]
    print("List all ObjectFinds OK")

    # test filter object finds by hzenc
    hzenc_url = base_url + reverse(
        "api:objectfind_list_hzenc",
        args=[
            test_utm_hemisphere,
            test_utm_zone,
            test_area_utm_easting_meters,
            test_area_utm_northing_meters,
            test_context_number,
        ],
    )
    r = requests.get(hzenc_url, headers=headers)
    data = r.json()
    assert r.status_code == 200
    assert obj_hzenc.count() == data["count"]
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
    r = requests.post(all_obj_url, data, headers=headers)
    print(r.status_code)
    assert r.status_code == 201
    print("Create ObjectFind OK")


def test_objectfind_detail():
    obj = random.choice(all_obj)
    url = base_url + reverse("api:objectfind_detail", args=[obj.id])
    r = requests.get(url, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert str(obj.id) == data["id"]
    print("Get object find detail OK")

    new_note = obj.director_notes + " edited" if obj.director_notes else "edited"
    data = {"director_notes": new_note, "weight_grams": "99999.69"}
    r = requests.put(url, data=data, headers=headers)
    assert r.status_code == 200
    assert r.json()["director_notes"] == new_note
    assert r.json()["weight_grams"] == data["weight_grams"]
    print("Edit object find detail OK")


def test_mc_list():
    mcs = MaterialCategory.objects.all()
    url = base_url + reverse("api:materialcategory_list")
    r = requests.get(url, headers=headers)
    assert r.status_code == 200
    assert mcs.count() == len(r.json())
    print("Material Category list OK")


def test_all():
    test_area()
    test_context()
    test_types()
    test_photo_upload()
    test_bagphoto_upload()
    test_objectfind()
    test_objectfind_detail()
