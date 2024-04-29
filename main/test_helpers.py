import glob
import hashlib
import pathlib
import random
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


class AuthFailed(Exception):
    pass


class NoPhotosFound(Exception):
    pass


def get_random_object_find():
    return ObjectFind.objects.order_by("?").first()


def get_random_find_with_photos(extension=None):
    for find in ObjectFind.objects.order_by("?"):
        if find.list_files_photo_folder(extension=extension):
            return find
    raise NoPhotosFound("No photos found in any find")


def get_file_hash(file_path: pathlib.Path):
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def upload_find_photo(url, headers, photo_path):
    r = requests.put(url, headers=headers, files={"photo": open(photo_path, "rb")})
    return r


def get_test_photo(
    photo_dir=settings.TEST_PHOTOS_DIR, extension=".jpg", hash_is_not=None
):
    options = list(pathlib.Path(photo_dir).glob(f"*{extension}"))
    if hash_is_not:
        options = [p for p in options if get_file_hash(p) != hash_is_not]
    return random.choice(options)


class TestClient:
    def __init__(
        self,
        username=settings.TEST_USERNAME,
        password=settings.TEST_USER_PW,
        base_url="http://127.0.0.1:8000",
    ):
        self.base_url = base_url
        self.headers = self.get_token(username, password)

    def get_token(self, username, password):
        url = self.base_url + "/asl/auth-token/"
        r = requests.post(url, data={"username": username, "password": password})

        if r.status_code == 200:
            headers = {"Authorization": f"Token {r.json()['token']}"}
            return headers
        else:
            raise AuthFailed(f"Authorization failed: {r.status_code} {r.content}")

    def get(self, path):
        url = self.base_url + path
        r = requests.get(url, headers=self.headers)
        return r

    def post(self, path, data=None, files={}):
        url = self.base_url + path
        r = requests.post(url, headers=self.headers, data=data, files=files)
        return r

    def put(self, path, data=None, files={}):
        url = self.base_url + path
        r = requests.put(url, headers=self.headers, data=data, files=files)
        return r

    def delete(self, path):
        url = self.base_url + path
        r = requests.delete(url, headers=self.headers)
        return r
