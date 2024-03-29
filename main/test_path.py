import random
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from datetime import datetime
from dateutil.tz import gettz
from main.models import SurveyPath, SurveyPoint
from main.utils import utm_to_latlong
from main.test_local import headers, base_url


User = get_user_model()
H = "N"
Z = 38
yerevan = gettz("Asia/Yerevan")
hongkong = gettz("Asia/Hong_Kong")


def increment_timestamp(isostr: str) -> str:
    dt = datetime.fromisoformat(isostr)
    dt = datetime.fromtimestamp(dt.timestamp() + random.uniform(0.5, 3), tz=dt.tzinfo)
    return dt.isoformat()


def create_test_path_data():
    notes = f"Randomly generated data to test uploading new paths at {datetime.now().astimezone(hongkong):%Y-%m-%d %H:%M:%S %Z}"

    easting = random.uniform(478000, 488000)
    northing = random.uniform(4417900, 4420000)
    altitude = random.uniform(900, 1200)
    timestamp = random.uniform(0, datetime.now().timestamp())
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
            "timestamp": datetime.fromtimestamp(timestamp, tz=yerevan).isoformat(),
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


def create_new_points_data(starting_point: SurveyPoint, num_points: int):
    utm_easting_meters = float(starting_point.utm_easting_meters) + random.uniform(
        -1, 1
    )
    utm_northing_meters = float(starting_point.utm_northing_meters) + random.uniform(
        -1, 1
    )
    timestamp = increment_timestamp(starting_point.timestamp.isoformat())
    utm_altitude = float(starting_point.utm_altitude) + random.uniform(-1, 1)
    latitude, longitude = utm_to_latlong(
        starting_point.utm_zone, utm_easting_meters, utm_northing_meters
    )
    points = [
        {
            "latitude": latitude,
            "longitude": longitude,
            "utm_hemisphere": starting_point.utm_hemisphere,
            "utm_zone": starting_point.utm_zone,
            "utm_easting_meters": utm_easting_meters,
            "utm_northing_meters": utm_northing_meters,
            "timestamp": timestamp,
            "utm_altitude": utm_altitude,
            "source": "R",
        }
    ]
    for i in range(num_points):
        utm_easting_meters = utm_easting_meters + random.uniform(-1, 1)
        utm_northing_meters = utm_northing_meters + random.uniform(-1, 1)
        latitude, longitude = utm_to_latlong(
            starting_point.utm_zone, utm_easting_meters, utm_northing_meters
        )
        points.append(
            {
                "utm_hemisphere": starting_point.utm_hemisphere,
                "utm_zone": starting_point.utm_zone,
                "utm_easting_meters": utm_easting_meters,
                "utm_northing_meters": utm_northing_meters,
                "timestamp": increment_timestamp(points[-1]["timestamp"]),
                "latitude": latitude,
                "longitude": longitude,
                "utm_altitude": points[-1]["utm_altitude"] + random.uniform(-1, 1),
                "source": "R",
            }
        )
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
    random_path = (
        SurveyPath.objects.order_by("?")
        .filter(user__username=settings.TEST_USERNAME)
        .first()
    )
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
    random_path = (
        SurveyPath.objects.filter(user__username=settings.TEST_USERNAME)
        .order_by("?")
        .first()
    )
    url = base_url + reverse("api:surveypath_detail", args=[random_path.id])
    new_notes = (
        random_path.notes
        + f"\nupdated {datetime.now(tz=hongkong):%Y-%m-%d %H:%M:%S %Z}"
    ).strip()
    returned = requests.put(
        url,
        json={
            "notes": new_notes,
            "points": [],  # empty list won't delete points
            "user": settings.TEST_USERNAME,
        },
        headers=headers,
    )
    rj = returned.json()
    assert returned.status_code == 200
    assert rj["notes"] == new_notes
    assert len(rj["points"]) == random_path.points.count()
    print("test_full_update_path passed")


def test_partial_update_path():
    random_path = (
        SurveyPath.objects.filter(user__username=settings.TEST_USERNAME)
        .order_by("?")
        .first()
    )
    url = base_url + reverse("api:surveypath_detail", args=[random_path.id])
    new_notes = (
        random_path.notes
        + f"\nupdated {datetime.now(tz=hongkong):%Y-%m-%d %H:%M:%S %Z}"
    )
    r = requests.patch(url, json={"notes": new_notes}, headers=headers)
    returned_data = r.json()
    print(r.status_code)
    assert r.status_code == 200
    assert returned_data["notes"] == new_notes

    # add new points
    new_points = create_new_points_data(
        random_path.points.order_by("timestamp").last(), 10
    )
    old_len = random_path.points.count()
    r = requests.patch(url, json={"points": new_points}, headers=headers)
    returned_data = r.json()
    print(r.status_code)
    assert r.status_code == 200
    assert len(returned_data["points"]) == old_len + len(new_points)
