import random
import glob
import requests
from django.conf import settings
from main.models import (
    ObjectFind,
    FindPhoto,
    SpatialArea,
    SpatialContext,
    AreaType,
    ContextType,
    ContextPhoto,
    BagPhoto,
    MaterialCategory,
    SurveyPath,
    SurveyPoint,
)


def get_random_object_find():
    return ObjectFind.objects.order_by("?").first()


def upload_find_photo(url, headers, photo_path):
    r = requests.put(url, headers=headers, files={"photo": open(photo_path, "rb")})
    return r


def get_test_photo(photo_dir=settings.TEST_PHOTO_DIR):
    return random.choice(glob.glob(f"{photo_dir}/*.jpg"))
