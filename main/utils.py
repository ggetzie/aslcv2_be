import math
import pathlib
import requests
import numpy as np

from django.conf import settings
from django.db import connections

import pyproj


def get_token(username, password, url="http://127.0.0.1:8000/asl/auth-token/"):
    r = requests.post(url, data={"username": username, "password": password})

    if r.status_code == 200:
        headers = {"Authorization": f"Token {r.json()['token']}"}
        return headers
    else:
        return r.status_code, r.content


def get_test_header():
    return get_token(username="test", password=settings.TEST_USER_PW)


PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".gif", ".png", ".heic", ".cr3", ".raw"}


def get_next_photo_number(folder: pathlib.Path) -> str:
    largest = 0
    for p in folder.iterdir():
        if p.is_file() and p.stem.isdigit() and (p.suffix.lower() in PHOTO_EXTENSIONS):
            num = int(p.stem)
            if num > largest:
                largest = num
    return f"{largest + 1}"


# Convert between UTM (Universal Transverse Mercator) coordinates and Latitute/Longitude
# using pyproj see: https://stackoverflow.com/a/18620929
test_lat = 43.642567
test_long = -79.387139


def get_utm_zone(longitude: float) -> int:
    return math.ceil((longitude + 180) / 6)


def latlong_to_utm(latitude: float, longitude: float) -> (int, float, float):
    zone = get_utm_zone(longitude)
    p = pyproj.Proj(proj="utm", zone=zone, ellps="WGS84")
    easting, northing = p(longitude, latitude)
    return zone, easting, northing


def utm_to_latlong(zone: int, easting: float, northing: float) -> (float, float):
    p = pyproj.Proj(proj="utm", zone=zone, ellps="WGS84")
    longitude, latitude = p(easting, northing, inverse=True)
    return latitude, longitude


def test_latlong_toUTM():
    # get sample data from database

    with connections["archaeology"].cursor() as cursor:
        cursor.execute(
            """
            SELECT 
            latitude_decimal_degrees, 
            longitude_decimal_degrees, 
            utm_zone, 
            utm_easting_meters, 
            utm_northing_meters
            FROM spatial.survey_points;
            """
        )
        samples = cursor.fetchall()
    easting_errors = np.array([])
    northing_errors = np.array([])
    for sample in samples:
        latitude = float(sample[0])
        longitude = float(sample[1])
        zone = sample[2]
        easting = float(sample[3])
        northing = float(sample[4])
        zone_calc, easting_calc, northing_calc = latlong_to_utm(latitude, longitude)
        easting_errors = np.append(easting_errors, easting - easting_calc)
        northing_errors = np.append(northing_errors, northing - northing_calc)
        assert zone == zone_calc

    print(
        f"easting error:\nmean: {np.mean(easting_errors)} max: {np.max(np.abs(easting_errors))}"
    )
    print(
        f"northing error:\n mean: {np.mean(northing_errors)} max: {np.max(np.abs(northing_errors))}"
    )


def test_latlong_toUTM_single(
    lat_in=43.642567,
    long_in=-79.387139,
    zone_in=17,
    easting_in=630084.0,
    northing_in=4833439.0,
):
    # default test point is CN Tower
    # from https://geohack.toolforge.org/geohack.php?pagename=Universal_Transverse_Mercator_coordinate_system&params=43_38_33.24_N_79_23_13.7_W_&title=CN+Tower
    zone_calc, easting_calc, northing_calc = latlong_to_utm(lat_in, long_in)
    print(f"zone: {zone_in} zone calculated: {zone_calc}")
    print(f"easting input \teasting calculated\teasting error")
    print(f"{easting_in}\t{easting_calc}\t{easting_in - easting_calc}")
    print()
    print(f"northing input \tnorthing calculated\tnorthing error")
    print(f"{northing_in}\t{northing_calc}\t{northing_in - northing_calc}")
