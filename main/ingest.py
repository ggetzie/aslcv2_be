import csv
import datetime
import pathlib

from dateutil.parser import parse
from dateutil.tz import UTC

from main.models import (SpatialArea, SpatialContext, ObjectFind,
                         MaterialCategory)
DATA = pathlib.Path("/usr/local/src/aslcv2_be/main/data")
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"


def read_file(filename):
    with open(DATA / filename) as infile:
        dialect = csv.Sniffer().sniff(infile.read(1024))
        infile.seek(0)
        reader = csv.DictReader(infile,
                                dialect=dialect)
        rows = [row for row in reader]
    return rows


def spatial_areas():
    rows = read_file("spatial_areas.txt")
    objs = []
    for row in rows:
        del row["xmin"]
        lon = row["longitude_decimal_degrees"]
        lon = float(lon) if lon else None
        lat = row["latitude_decimal_degrees"]
        lat = float(lat) if lat else None
        objs.append(SpatialArea(utm_hemisphere=row["utm_hemisphere"],
                                utm_zone=int(row["utm_zone"]),
                                area_utm_easting_meters=int(row["area_utm_easting_meters"]),
                                area_utm_northing_meters=int(row["area_utm_northing_meters"]),
                                type=row["type"],
                                longitude_decimal_degrees=lon,
                                latitude_decimal_degrees=lat))
                                
    SpatialArea.objects.bulk_create(objs)

def spatial_contexts():
    rows = read_file("spatial_contexts.txt")
    objs = []
    for row in rows:
        if row["opening_date"]:
            # opening = datetime.datetime.strptime(row["opening_date"], DATE_FORMAT)
            opening = parse(row["opening_date"]+ " UTC", tzinfos={"UTC": UTC})
        else:
            opening = None

        if row["closing_date"]:
            # closing = datetime.datetime.strptime(row["closing_date"], DATE_FORMAT)
            closing = parse(row["closing_date"]+ " UTC", tzinfos={"UTC": UTC})
        else:
            closing = None
            
        sa = SpatialArea.objects.get(utm_hemisphere=row["utm_hemisphere"],
                                     utm_zone=row["utm_zone"],
                                     area_utm_easting_meters=row["area_utm_easting_meters"],
                                     area_utm_northing_meters=row["area_utm_northing_meters"])
        objs.append(SpatialContext(spatial_area=sa,
                                   context_number=row["context_number"],
                                   type=row["type"],
                                   opening_date=opening,
                                   closing_date=closing,
                                   description=row["description"],
                                   director_notes=row["director_notes"]))
    SpatialContext.objects.bulk_create(objs)


def material_categories():
    rows = read_file("options_material_category.txt")
    objs = []
    for row in rows:
        del row["xmin"]
        objs.append(MaterialCategory(**row))
    MaterialCategory.objects.bulk_create(objs)

    
def object_finds():
    rows = read_file("object_finds.txt")
    objs = []    
    for row in rows:
        sc = SpatialContext.objects.get(spatial_area__utm_hemisphere=row["utm_hemisphere"],
                                        spatial_area__utm_zone=row["utm_zone"],
                                        spatial_area__area_utm_easting_meters=row["area_utm_easting_meters"],
                                        spatial_area__area_utm_northing_meters=row["area_utm_northing_meters"],
                                        context_number=row["context_number"])
        mc, _ = MaterialCategory.objects.get_or_create(material=row["material"],
                                                       category=row["category"])
        objs.append(ObjectFind(spatial_context=sc,
                               find_number=row["find_number"],
                               material_category=mc,
                               director_notes=row["director_notes"]))
    ObjectFind.objects.bulk_create(objs)


