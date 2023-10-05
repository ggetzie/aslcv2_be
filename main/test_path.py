import datetime
import random
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from dateutil.tz import gettz
from main.models import SurveyPath, SurveyPoint
from main.utils import utm_to_latlong
from main.test_local import headers, base_url


User = get_user_model()
H = "N"
Z = 38
yerevan = gettz("Asia/Yerevan")
hongkong = gettz("Asia/Hong_Kong")


def increment_point(point: SurveyPoint) -> SurveyPoint:
    pass


def create_test_path_data():
    notes = f"Randomly generated data to test uploading new paths at {datetime.datetime.now().astimezone(hongkong):%Y-%m-%d %H:%M:%S %Z}"

    easting = random.uniform(478000, 488000)
    northing = random.uniform(4417900, 4420000)
    altitude = random.uniform(900, 1200)
    timestamp = random.uniform(0, datetime.datetime.now().timestamp())
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
            "timestamp": datetime.datetime.fromtimestamp(
                timestamp, tz=yerevan
            ).isoformat(),
            "utm_altitude": altitude,
            "source": "R",
        }
        points.append(point)
        easting = easting + random.uniform(-1, 1)
        northing = northing + random.uniform(-1, 1)
        altitude = altitude + random.uniform(-1, 1)
        timestamp = timestamp + random.uniform(0.5, 3)
        latitude, longitude = utm_to_latlong(Z, easting, northing)
    return {"user": settings.TEST_USERNAME, "notes": notes, "points": points}


def create_test_path():
    data = create_test_path_data()
    test_user = User.objects.get(username=data["user"])
    path = SurveyPath.objects.create(user=test_user, notes=data["notes"])
    points = [
        SurveyPoint(
            survey_path=path,
            latitude=point["latitude"],
            longitude=point["longitude"],
            utm_hemisphere=point["utm_hemisphere"],
            utm_zone=point["utm_zone"],
            utm_easting_meters=point["utm_easting_meters"],
            utm_northing_meters=point["utm_northing_meters"],
            timestamp=point["timestamp"],
            utm_altitude=point["utm_altitude"],
            source=point["source"],
        )
        for point in data["points"]
    ]
    SurveyPoint.objects.bulk_create(points)
    return path


def create_new_points(starting_point, num_points):
    points = []

    utm_easting_meters = starting_point.utm_easting_meters + random.uniform(-1, 1)
    utm_northing_meters = starting_point.utm_northing_meters + random.uniform(-1, 1)
    timestamp = starting_point.timestamp + random.uniform(0.5, 3)
    utm_altitude = starting_point.utm_altitude + random.uniform(-1, 1)
    latitude, longitude = utm_to_latlong(
        starting_point.utm_zone, utm_easting_meters, utm_northing_meters
    )
    for i in range(num_points):
        point = SurveyPoint(
            survey_path=starting_point.survey_path,
            latitude=latitude,
            longitude=longitude,
            utm_hemisphere=starting_point.utm_hemisphere,
            utm_zone=starting_point.utm_zone,
            utm_easting_meters=utm_easting_meters,
            utm_northing_meters=utm_northing_meters,
            timestamp=datetime.datetime.fromtimestamp(timestamp, tz=yerevan),
            utm_altitude=utm_altitude,
            source="R",
        )

        points.append(point)
    return points


def test_list_paths():
    r = requests.get(base_url + reverse("api:surveypath_list"), headers=headers)
    all_paths = SurveyPath.objects.all()
    print(r.status_code)
    print(r.json())
    data = r.json()
    assert r.status_code == 200
    assert data["count"] == all_paths.count()
    assert len(data["results"]) == all_paths.count()
    print("test_list_paths passed")


def test_create_path():
    url = base_url + reverse("api:surveypath_list")
    data = create_test_path_data()
    r = requests.post(url, json=data, headers=headers)
    returned_data = r.json()
    assert r.status_code == 201
    assert returned_data["user"] == data["user"]
    assert returned_data["notes"] == data["notes"]
    assert len(returned_data["points"]) == len(data["points"])
    print("test_create_path passed")


def test_get_path():
    random_path = SurveyPath.objects.order_by("?").first()
    url = base_url + reverse("api:surveypath_detail", args=[random_path.id])
    r = requests.get(url, headers=headers)
    returned_data = r.json()
    assert r.status_code == 200
    assert returned_data["id"] == str(random_path.id)
    assert returned_data["user"] == random_path.user.username
    assert returned_data["notes"] == random_path.notes
    assert len(returned_data["points"]) == random_path.points.count()
    print("test_get_path passed")


def test_full_update_path():
    pass


def test_partial_update_path():
    pass
    # update notes

    # add new points
