from django.conf import settings

import requests
import pathlib
import re


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
