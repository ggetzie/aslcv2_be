import requests

def get_token(username, password, url="http://localhost:3000/auth-token/"):
    r = requests.post(url,
                      data={"username":username,
                            "password": password})
    if r.status_code == 200:
        headers = {"Authorization": f"Token {r.json()['token']}"}
        return headers
    else:
        return r.status_code, r.content
