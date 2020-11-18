"""
Perform some tests against the local database
Must have the ./manage.py runserver running

Import and call from the shell

Current test runner doesn't work with mutli-schema setup
TODO: fix that
"""
from django.db.models import Max
from django.urls import reverse

import requests

import main.utils as utils
from main.models import (SpatialArea, AreaType, SpatialContext, ContextType,
                         ObjectFind, MaterialCategory, ContextPhoto)

headers = utils.get_test_header()
base_url = "http://localhost:3000"

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
    assert n.count() == len(r.json())
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
    assert n_38.count() == len(r.json())
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
    assert n_38_478130_4419430.count() == len(r.json())
    print("SpatialArea List Hemisphere Zone Easting Northing OK")

    r = requests.get(base_url + reverse("api:spatialarea_detail",
                                        args=[n_38_478130_4419430[0].id]),
                     headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == str(n_38_478130_4419430[0].id)
    print("SpatialArea Detail by uuid OK")
    

def test_context():

    r = requests.get(base_url + reverse("api:spatialcontext_list"),
                     headers=headers)
    assert r.status_code == 200
    assert all_sc.count() == len(r.json())
    print("List all SpatialContext OK")

    r = requests.get(base_url + reverse("api:spatialcontext_list_hzen",
                                        args=[test_utm_hemisphere,
                                              test_utm_zone,
                                              test_area_utm_easting_meters,
                                              test_area_utm_northing_meters]),
                     headers=headers)
    
    assert r.status_code == 200
    assert sc_hzen.count() == len(r.json())
    print("List all SpatialContext Filter URL OK")

    data = {"utm_hemisphere": test_utm_hemisphere,
            "utm_zone": test_utm_zone,
            "area_utm_easting_meters": test_area_utm_easting_meters,
            "area_utm_northing_meters": test_area_utm_northing_meters}
    old_max = (SpatialContext
               .objects
               .filter(**data)
               .aggregate(Max("context_number"))["context_number__max"] or 0)

    r = requests.post(base_url + reverse("api:spatialcontext_list"),
                      headers=headers,
                      data=data)
    assert r.status_code == 201
    assert r.json()["context_number"] == (old_max + 1)
    sc = SpatialContext.objects.get(id=r.json()["id"])
    print("SpatialContext Create OK")
    sc.delete()
