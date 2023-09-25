import pathlib
import requests
import numpy as np

from django.conf import settings
from django.db import connections


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
    # alpha 1
    n / 2.0
    - 2 / 3.0 * n**2
    + 5 / 16.0 * n**3
    + 41 / 180.0 * n**4
    - 127 / 288.0 * n**5
    + 7891 / 37800.0 * n**6
    + 72161 / 387072.0 * n**7
    - 18975107 / 50803200.0 * n**8,
    # alpha 2
    13 / 48.0 * n**2
    - 3 / 5.0 * n**3
    + 557 / 1440.0 * n**4
    + 281 / 630.0 * n**5
    - 1983433 / 1935360.0 * n**6
    + 13769 / 28800.0 * n**7
    + 148003883 / 174182400.0 * n**8,
    # alpha 3
    61 / 240.0 * n**3
    - 103 / 140.0 * n**4
    + 15061 / 26880.0 * n**5
    + 167603 / 181440.0 * n**6
    - 67102379 / 29030400.0 * n**7
    + 79682431 / 79833600.0 * n**8,
    # alpha 4
    49561 / 161280.0 * n**4
    - 179 / 168.0 * n**5
    + 6601661 / 7257600.0 * n**6
    + 97445 / 49896.0 * n**7
    - 40176129013 / 7664025600.0 * n**8,
]

beta = [
    # beta 1
    1 / 2.0 * n
    - 2 / 3.0 * n**2
    + 37 / 96.0 * n**3
    - 1 / 360.0 * n**4
    - 81 / 512.0 * n**5
    + 96199 / 604800.0 * n**6
    - 5406467 / 38707200.0 * n**7
    + 7944359 / 67737600.0 * n**8,
    # beta 2
    1 / 48.0 * n**2
    + 1 / 15.0 * n**3
    - 437 / 1440.0 * n**4
    + 46 / 105.0 * n**5
    - 1118711 / 3870720.0 * n**6
    + 51841 / 1209600.0 * n**7
    + 24749483 / 348364800.0 * n**8,
    # beta 3
    17 / 480.0 * n**3
    - 37 / 840.0 * n**4
    - 209 / 4480.0 * n**5
    + 5569 / 90720.0 * n**6
    + 9261899 / 58060800.0 * n**7
    - 6457463 / 17740800.0 * n**8,
    # beta 4
    4397 / 161280.0 * n**4
    - 11 / 504.0 * n**5
    - 830251 / 7257600.0 * n**6
    - 466511 / 2494800.0 * n**7
    + 324154477 / 7664025600.0 * n**8,
]

# delta = [
#     2 * n - 2 / 3.0 * n**2 - 2 * n**3,
#     7 / 3.0 * n**2 - 8 / 5.0 * n**3,
#     56 / 15.0 * n**3,
# ]


def latlong_to_UTM(latitude: float, longitude: float) -> tuple:
    N0 = 0.0 if latitude >= 0.0 else 10_000_000.0  # meters
    zone = np.ceil((longitude + 180) / 6)

    # reference meridian
    lambda0 = np.radians((zone - 1.0) * 6 - 180 + 3)  # longitude of central meridian

    latitude = np.radians(latitude)
    longitude = np.radians(longitude)
    # latitude: phi (φ)
    # longitude: lambda (λ)

    x = 2.0 * np.sqrt(n) / (1.0 + n)
    t = np.sinh(np.arctanh(np.sin(latitude)) - x * np.arctanh(x * np.sin(latitude)))
    zeta_p = np.arctan(t / np.cos(longitude - lambda0))
    nu_p = np.arctan(np.sin(longitude - lambda0) / np.sqrt(1 + t**2.0))
    sigma = 1 + sum(
        [
            2
            * (i + 1)
            * alph
            * np.cos(2 * (i + 1) * zeta_p)
            * np.cosh(2 * (i + 1) * nu_p)
            for i, alph in enumerate(alpha)
        ]
    )

    tau = sum(
        [
            2
            * (i + 1)
            * alph
            * np.sin(2 * (i + 1) * zeta_p)
            * np.sinh(2 * (i + 1) * nu_p)
            for i, alph in enumerate(alpha)
        ]
    )
    # Easting
    E = E0 + k0 * A * (
        nu_p
        + sum(
            [
                alph * np.cos(2 * (i + 1) * zeta_p) * np.sinh(2 * (i + 1) * nu_p)
                for i, alph in enumerate(alpha)
            ]
        )
    )
    # Northing
    N = N0 + k0 * A * (
        zeta_p
        + sum(
            [
                alph * np.sin(2 * (i + 1) * zeta_p) * np.cosh(2 * (i + 1) * nu_p)
                for i, alph in enumerate(alpha)
            ]
        )
    )
    # Scale Factor
    k = (
        k0
        * A
        / a
        * np.sqrt(
            (1 + ((1 - n) / (1 + n) * np.tan(latitude)) ** 2)
            * (sigma**2 + tau**2)
            / (t**2 + np.cos(longitude - lambda0) ** 2)
        )
    )

    # Grid Convergence
    sqrt1t2 = np.sqrt(1 + t**2)
    gamma = np.arctan(
        (tau * sqrt1t2 + sigma * t * np.tan(longitude - lambda0))
        / (sigma * sqrt1t2 - tau * t * np.tan(longitude - lambda0))
    )

    return zone, E, N, k, gamma


def test_latlong_toUTM():
    # get sample data from database

    with connections["archaeology"].cursor() as cursor:
        cursor.execute(
            """
            SELECT 
            latitude_decimal_degrees, 
            longitude_decimal_degrees, 
            utm_zone, 
            utm_easting_meters, 
            utm_northing_meters
            FROM spatial.survey_points;
            """
        )
        samples = cursor.fetchall()
    easting_errors = np.array([])
    northing_errors = np.array([])
    for sample in samples:
        latitude = float(sample[0])
        longitude = float(sample[1])
        zone = sample[2]
        easting = float(sample[3])
        northing = float(sample[4])
        zone_calc, easting_calc, northing_calc, _, _ = latlong_to_UTM(
            latitude, longitude
        )
        easting_errors = np.append(easting_errors, easting - easting_calc)
        northing_errors = np.append(northing_errors, northing - northing_calc)
        assert zone == zone_calc

    print(
        f"easting error:\nmean: {np.mean(easting_errors)} max: {np.max(np.abs(easting_errors))}"
    )
    print(
        f"northing error:\n mean: {np.mean(northing_errors)} max: {np.max(np.abs(northing_errors))}"
    )


def test_latlong_toUTM_single(
    lat_in=43.642567,
    long_in=-79.387139,
    zone_in=17,
    easting_in=630084.0,
    northing_in=4833439.0,
):
    # default test point is CN Tower
    # from https://geohack.toolforge.org/geohack.php?pagename=Universal_Transverse_Mercator_coordinate_system&params=43_38_33.24_N_79_23_13.7_W_&title=CN+Tower
    zone_calc, easting_calc, northing_calc, _, _ = latlong_to_UTM(lat_in, long_in)
    print(f"zone: {zone_in} zone calculated: {zone_calc}")
    print(f"easting input \teasting calculated\teasting error")
    print(f"{easting_in}\t{easting_calc}\t{easting_in - easting_calc}")
    print()
    print(f"northing input \tnorthing calculated\tnorthing error")
    print(f"{northing_in}\t{northing_calc}\t{northing_in - northing_calc}")
