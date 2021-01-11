from django.conf import settings

import requests

def get_token(username, password, url="http://aslcv2/auth-token/"):
    r = requests.post(url,
                      data={"username":username,
                            "password": password})
    if r.status_code == 200:
        headers = {"Authorization": f"Token {r.json()['token']}"}
        return headers
    else:
        print(r.status_code, r.content)
        return r.status_code, r.content


def get_test_header():
    return get_token(username="test", password=settings.TEST_USER_PW)
