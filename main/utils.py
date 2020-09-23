import requests

def get_token(username, password):
    r = requests.post("http://localhost:3000/auth-token/",
                      data={"username":username,
                            "password": password})
    if r.status_code == 200:
        headers = {"Authorization": f"Token {r.json()['token']}"}
        return headers
    else:
        return r.status_code, r.content
