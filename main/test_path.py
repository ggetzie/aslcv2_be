import datetime
import random
from django.contrib.auth import get_user_model

from dateutil.tz import gettz
from main.models import SurveyPath, SurveyPoint
from main.utils import utm_to_latlong

User = get_user_model()
H = "N"
Z = 38
timezone = gettz("Asia/Yerevan")


def create_test_path():
    test_user = User.objects.get(username="test")
    path = SurveyPath.objects.create(
        user=test_user, notes="Randomly generated path for testing"
    )
    easting = random.uniform(478000, 488000)
    northing = random.uniform(4417900, 4420000)
    timestamp = datetime.datetime.fromtimestamp(
        random.uniform(0, datetime.datetime.now().timestamp()), tz=timezone
    )
    latitude, longitude = utm_to_latlong(Z, easting, northing)

    for i in range(random.randint(20, 50)):
        SurveyPoint.objects.create(
            survey_path=path,
            latitude=latitude,
            longitude=longitude,
            utm_hemisphere=H,
            utm_zone=Z,
            utm_easting_meters=easting,
            utm_northing_meters=northing,
            timestamp=timestamp,
            utm_altitude=random.uniform(900, 1200),
            source="R",
        )
        easting = easting + random.uniform(-1, 1)
        northing = northing + random.uniform(-1, 1)
        timestamp = datetime.datetime.fromtimestamp(
            timestamp.timestamp() + random.uniform(0.5, 3), tz=timezone
        )
        latitude, longitude = utm_to_latlong(Z, easting, northing)

    return path
