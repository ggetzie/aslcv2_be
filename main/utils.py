import math
import pathlib
import requests

from django.conf import settings


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


# Convert between UTM (Universal Transverse Mercator) coordinates and Latitute/Longitude
# equations from https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system
# distances are in kilometers


# a = 6_378_206.4  # equatorial radius meters NAD 27
# f = 1 / 294.978698214  # flattening NAD 27

a = 6_378_137.0  # equatorial radius meters GRS 80
# f = 1 / 298.2572221001  # flattening GRS 80
f = 1 / 298.257223563  # flattening WGS 84

n = f / (2 - f)  # third flattening
# n = 1 / (2 * f - 1)  # third flattening
A = a / (1 + n) * (1 + n**2 / 4 + n**4 / 64)  # meridional radius of curvature
k0 = 0.9996  # scale on central meridian
E0 = 500_000  # meters


alpha = [
    n / 2.0 - 2 / 3.0 * n**2 + 5 / 16.0 * n**3,
    13 / 48.0 * n**2 - 3 / 5.0 * n**3,
    61 / 240.0 * n**3,
]

beta = [
    1 / 2.0 * n - 2 / 3.0 * n**2 + 37 / 96.0 * n**3,
    1 / 48.0 * n**2 + 1 / 15.0 * n**3,
    17 / 480.0 * n**3,
]

# delta = [
#     2 * n - 2 / 3.0 * n**2 - 2 * n**3,
#     7 / 3.0 * n**2 - 8 / 5.0 * n**3,
#     56 / 15.0 * n**3,
# ]


def latlong_to_UTM(latitude: float, longitude: float) -> tuple:
    N0 = 0.0 if latitude >= 0.0 else 10_000_000.0  # meters
    zone = math.ceil((longitude + 180) / 6)

    # reference meridian
    lambda0 = math.radians((zone - 1.0) * 6 - 180 + 3)  # longitude of central meridian

    latitude = math.radians(latitude)
    longitude = math.radians(longitude)
    print(f"{lambda0=}, {longitude=}, {latitude=}")
    # latitude: phi (φ)
    # longitude: lambda (λ)

    x = 2.0 * math.sqrt(n) / (1.0 + n)
    t = math.sinh(
        math.atanh(math.sin(latitude)) - x * math.atanh(x * math.sin(latitude))
    )
    zeta_p = math.atan(t / math.cos(longitude - lambda0))
    nu_p = math.atan(math.sin(longitude - lambda0) / math.sqrt(1 + t**2.0))
    sigma = 1 + sum(
        [
            2
            * (i + 1)
            * alph
            * math.cos(2 * (i + 1) * zeta_p)
            * math.cosh(2 * (i + 1) * nu_p)
            for i, alph in enumerate(alpha)
        ]
    )

    tau = sum(
        [
            2
            * (i + 1)
            * alph
            * math.sin(2 * (i + 1) * zeta_p)
            * math.sinh(2 * (i + 1) * nu_p)
            for i, alph in enumerate(alpha)
        ]
    )
    # Easting
    E = E0 + k0 * A * (
        nu_p
        + sum(
            [
                alph * math.cos(2 * (i + 1) * zeta_p) * math.sinh(2 * (i + 1) * nu_p)
                for i, alph in enumerate(alpha)
            ]
        )
    )
    # Northing
    N = N0 + k0 * A * (
        zeta_p
        + sum(
            [
                alph * math.sin(2 * (i + 1) * zeta_p) * math.cosh(2 * (i + 1) * nu_p)
                for i, alph in enumerate(alpha)
            ]
        )
    )
    # Scale Factor
    k = (
        k0
        * A
        / a
        * math.sqrt(
            (1 + ((1 - n) / (1 + n) * math.tan(latitude)) ** 2)
            * (sigma**2 + tau**2)
            / (t**2 + math.cos(longitude - lambda0) ** 2)
        )
    )

    # Grid Convergence
    sqrt1t2 = math.sqrt(1 + t**2)
    gamma = math.atan(
        (tau * sqrt1t2 + sigma * t * math.tan(longitude - lambda0))
        / (sigma * sqrt1t2 - tau * t * math.tan(longitude - lambda0))
    )

    return zone, E, N, k, gamma
