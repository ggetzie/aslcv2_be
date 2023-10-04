import datetime
import random
import requests
from django.contrib.auth import get_user_model
from django.urls import reverse

from dateutil.tz import gettz
from main.models import SurveyPath, SurveyPoint
from main.utils import utm_to_latlong
from main.test_local import headers, base_url


User = get_user_model()
H = "N"
Z = 38
timezone = gettz("Asia/Yerevan")


def create_test_path_data():
    username = "test"
    notes = "Randomly generated data to test uploading new paths"

    easting = random.uniform(478000, 488000)
    northing = random.uniform(4417900, 4420000)
    altitude = random.uniform(900, 1200)
    timestamp = datetime.datetime.fromtimestamp(
        random.uniform(0, datetime.datetime.now().timestamp()), tz=timezone
    )
    latitude, longitude = utm_to_latlong(Z, easting, northing)
    points = []
    for i in range(random.randint(20, 50)):
        point = {
            "latitude": latitude,
            "longitude": longitude,
            "utm_hemisphere": H,
            "utm_zone": Z,
            "utm_easting_meters": easting,
            "utm_northing_meters": northing,
            "timestamp": timestamp,
            "utm_altitude": altitude,
            "source": "R",
        }
        points.append(point)
        easting = easting + random.uniform(-1, 1)
        northing = northing + random.uniform(-1, 1)
        altitude = altitude + random.uniform(-1, 1)
        timestamp = datetime.datetime.fromtimestamp(
            timestamp.timestamp() + random.uniform(0.5, 3), tz=timezone
        )
        latitude, longitude = utm_to_latlong(Z, easting, northing)
    return {"user": username, "notes": notes, "points": points}


def create_test_path():
    data = create_test_path_data()
    test_user = User.objects.get(username=data["user"])
    path = SurveyPath.objects.create(user=test_user, notes=data["notes"])
    points = [SurveyPoint(path=path, **point) for point in data["points"]]
    SurveyPoint.objects.bulk_create(points)
    return path


def test_list_paths():
    r = requests.get(base_url + reverse("api:surveypath_list"), headers=headers)
    all_paths = SurveyPath.objects.all()
    print(r.status_code)
    print(r.json())
    assert r.status_code == 200
    assert len(r.json()) == all_paths.count()


def test_create_path():
    # POST to reverse("path-list")
    url = base_url + reverse("api:surveypath_list")
    data = create_test_path_data()
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == 201
    assert r.json()["user"] == data["user"]
    assert r.json()["notes"] == data["notes"]
    assert len(r.json()["points"]) == len(data["points"])


def test_get_path():
    pass


def test_full_update_path():
    pass


def test_partial_update_path():
    pass
