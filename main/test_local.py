"""
Perform some tests against the local database
Must have the ./manage.py runserver running

Import and call from the shell

Current test runner doesn't work with mutli-schema setup
TODO: fix that
"""
import datetime
import glob
import pathlib
import random

from django.conf import settings
from django.db.models import Max
from django.urls import reverse

import requests

import main.utils as utils
from main.models import (SpatialArea, AreaType, SpatialContext, ContextType,
                         ObjectFind, MaterialCategory, ContextPhoto, BagPhoto)

headers = utils.get_test_header()
base_url = "http://aslcv2"
PHOTO_DIR = "/mnt/c/Users/ggetz/Pictures/"

# SpatialArea: N-38-478130-4419430
test_utm_hemisphere = "N"
test_utm_zone = 38
test_area_utm_easting_meters = 478130
test_area_utm_northing_meters = 4419430

all_sa = SpatialArea.objects.all()
sa_h = SpatialArea.objects.filter(utm_hemisphere=test_utm_hemisphere)
sa_hz = SpatialArea.objects.filter(utm_hemisphere=test_utm_hemisphere,
                                   utm_zone=test_utm_zone)
sa_hze = (SpatialArea
          .objects
          .filter(utm_hemisphere=test_utm_hemisphere,
                  utm_zone=test_utm_zone,
                  area_utm_easting_meters=test_area_utm_easting_meters))

sa_hzen = (SpatialArea
           .objects
           .filter(utm_hemisphere=test_utm_hemisphere,
                   utm_zone=test_utm_zone,
                   area_utm_easting_meters=test_area_utm_easting_meters,
                   area_utm_northing_meters=test_area_utm_northing_meters))

all_sc = SpatialContext.objects.all()

sc_hzen = (SpatialContext
           .objects
           .filter(utm_hemisphere=test_utm_hemisphere,
                   utm_zone=test_utm_zone,
                   area_utm_easting_meters=test_area_utm_easting_meters,
                   area_utm_northing_meters=test_area_utm_northing_meters))


def test_area():

    r = requests.get(base_url+reverse("api:spatialarea_list"),
                     headers=headers)
    assert r.status_code == 200
    assert all_sa.count() == len(r.json())
    print("SpatialArea List OK")

    r = requests.get(base_url+reverse("api:spatialarea_list_h",
                                      args=[test_utm_hemisphere]),
                     headers=headers)
    assert r.status_code == 200
    assert sa_h.count() == len(r.json())
    print("SpatialArea List Hemisphere OK")

    url404 = (base_url+reverse("api:spatialarea_list_h",
                               args=[test_utm_hemisphere])).replace("/N/", "/Q/")
    r = requests.get(url404, headers=headers)
    assert r.status_code == 404
    print("SpatialArea List Hemisphere 404 OK")

    r = requests.get(base_url+reverse("api:spatialarea_list_hz",
                                      args=[test_utm_hemisphere,
                                            test_utm_zone]),
                     headers=headers)
    assert r.status_code == 200
    assert sa_hz.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone OK")

    r = requests.get(base_url+reverse("api:spatialarea_list_hze",
                                      args=[test_utm_hemisphere,
                                            test_utm_zone,
                                            test_area_utm_easting_meters]),
                     headers=headers)
    assert r.status_code == 200
    assert sa_hze.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone Easting OK")

    r = requests.get(base_url+reverse("api:spatialarea_list_hzen",
                                      args=[test_utm_hemisphere,
                                            test_utm_zone,
                                            test_area_utm_easting_meters,
                                            test_area_utm_northing_meters]),
                     headers=headers)
    assert r.status_code == 200
    assert sa_hzen.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone Easting Northing OK")

    r = requests.get(base_url + reverse("api:spatialarea_detail",
                                        args=[sa_hzen[0].id]),
                     headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == str(sa_hzen[0].id)
    print("SpatialArea Detail by uuid OK")
    

def test_context():

    # test list all spatial contexts
    r = requests.get(base_url + reverse("api:spatialcontext_list"),
                     headers=headers)
    assert r.status_code == 200
    assert all_sc.count() == len(r.json())
    print("List all SpatialContext OK")

    # test filtered list of spatial context
    r = requests.get(base_url + reverse("api:spatialcontext_list_hzen",
                                        args=[test_utm_hemisphere,
                                              test_utm_zone,
                                              test_area_utm_easting_meters,
                                              test_area_utm_northing_meters]),
                     headers=headers)
    
    assert r.status_code == 200
    assert sc_hzen.count() == len(r.json())
    print("List all SpatialContext Filter URL OK")
    
    # test create new spatial context
    sc_type = random.choice(ContextType.objects.all())
    data = {"utm_hemisphere": test_utm_hemisphere,
            "utm_zone": test_utm_zone,
            "area_utm_easting_meters": test_area_utm_easting_meters,
            "area_utm_northing_meters": test_area_utm_northing_meters,
            "type": sc_type.type}
    old_max = (SpatialContext
               .objects
               .filter(utm_hemisphere=test_utm_hemisphere,
                       utm_zone=test_utm_zone,
                       area_utm_easting_meters=test_area_utm_easting_meters,
                       area_utm_northing_meters=test_area_utm_northing_meters)
               .aggregate(Max("context_number"))["context_number__max"] or 0)

    r = requests.post(base_url + reverse("api:spatialcontext_list"),
                      headers=headers,
                      data=data)
    assert r.status_code == 201
    assert r.json()["context_number"] == (old_max + 1)
    sc = SpatialContext.objects.get(id=r.json()["id"])
    print("SpatialContext Create OK")
    sc.delete()

    # test get spatial context by uuid
    sc = random.choice(SpatialContext.objects.all())
    r = requests.get(base_url + reverse("api:spatialcontext_detail",
                                        args=[sc.id]),
                     headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == str(sc.id)

    # test edit spatial context
    sc = random.choice(SpatialContext.objects.filter(opening_date__isnull=True))
    data = {"opening_date": datetime.date.today()}
    r = requests.put(base_url + reverse("api:spatialcontext_detail",
                                        args=[sc.id]),
                     headers=headers,
                     data=data)
    assert r.status_code == 200
    sc = SpatialContext.objects.get(id=r.json()["id"])
    assert sc.opening_date == datetime.date.today()
    sc.opening_date = None
    sc.save()
    print("SpatialContext edit OK")
    

def test_types():

    r = requests.get(base_url + reverse("api:spatialarea_types"),
                     headers=headers)
    assert r.status_code == 200
    area_types = AreaType.objects.all()
    res = {i["type"] for i in r.json()}
    for at in area_types:
        assert at.type in res
    print("Spatial Area Types List OK")

    r = requests.get(base_url + reverse("api:spatialcontext_types"),
                     headers=headers)
    assert r.status_code == 200
    context_types = ContextType.objects.all()
    res = {i["type"] for i in r.json()}
    for ct in context_types:
        assert ct.type in res
    print("Spatial Context Types List OK")

def test_photo_upload():
    sc = random.choice(SpatialContext.objects.all())
    url = base_url + reverse("api:spatialcontext_photo", args=[sc.id])
    photo_path = random.choice(glob.glob(f"{PHOTO_DIR}*.jpg"))

    r = requests.put(url, headers=headers,
                     files={"photo": open(photo_path, "rb")})
    assert r.status_code == 201
    p = ContextPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Context Photo upload OK")

def test_bagphoto_upload():    
    sc = random.choice(SpatialContext.objects.all())
    url = base_url + reverse("api:spatialcontext_bagphoto", args=[sc.id])
    photo_path = random.choice(glob.glob(f"{PHOTO_DIR}*.jpg"))
    r = requests.put(url, 
                     data={"source": "F"},
                     headers=headers,
                     files={"photo": open(photo_path, "rb")})
    assert r.status_code == 201
    p = BagPhoto.objects.get(id=r.json()["id"])
    assert pathlib.Path(p.photo.path).exists()
    print("Finds Bag Photo upload OK")

def test_all():
    test_area()
    test_context()
    test_types()
    test_photo_upload()
    test_bagphoto_upload()
