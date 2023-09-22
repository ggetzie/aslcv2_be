# ASLCV API Documentation
items in curly brackets {} indicate a value should be provided

## Spatial Areas
### /asl/api/area/ 
GET list all SpatialAreas

### /asl/api/area/{utm_hemisphere}/ 
GET list all SpatialAreas with hemisphere "N or S"

### /asl/api/area/{utm_hemisphere}/{utm_zone}/ 
GET list all SpatialAreas with hemisphere "N or S" and zone

### /asl/api/area/{utm_hemisphere}/{utm_zone}/{area_utm_easting_meters/
GET list all SpatialAreas with hemisphere "N or S" and Zone and easting

### /asl/api/area/{utm_hemisphere}/{utm_zone}/{area_utm_easting_meters}/{area_utm_nothing_meters}/
GET list all SpatialAreas with hemisphere "N or S",  Zone,  Easting, Northing 
note: this will only be one area, but will be in a list

### /asl/api/area/{uuid}/ 
GET detail of Spatial Area with given uuid

### /asl/api/area/types 
GET list SpatialArea types

## Spatial Contexts
### /asl/api/context/ 
GET list all SpatialContexts  
POST create new Spatial Context

### /asl/api/context/{utm_hemisphere}/{utm_zone}/{area_utm_easting_meters}/{area_utm_nothing_meters}/
GET list all SpatialContexts for the SpatialArea with the given values

### /asl/api/context/{uuid} 
GET detail of Spatial Context with given uuid
PUT update Spatial Context with given uuid

### /asl/api/context/{uuid}/photo/
PUT upload context photo

### /asl/api/context/types/
GET list all Spatial Context Types

## Object Finds
### /asl/api/find/
GET list all ObjectFinds
POST create new Object Find

### /asl/api/find/mc/ 
GET list all Material Categories

### /asl/api/find/{utm_hemisphere}/{utm_zone}/{area_utm_easting_meters}/{area_utm_northing_meters}/{context_number}/
GET list all finds for context

### /asl/api/find/{uuid}/ 
GET object find detail

### /asl/api/find/{uuid}/photo/
PUT upload object find photo

## Paths
### /asl/api/path/
GET list all SurveyPaths
Returns a list of all SurveyPaths. To save data, points will not be included. Request details for the individual path to get the list of all points.

Returns:
```
[
  {
    "id": "03a45bbc-9866-47be-890f-2a1ab3a0cdbc",
    "notes": "Text field containing notes",
    "user": "test_user",
  },
  {
    "id": "03a45bbc-9866-47be-890f-2a1ab3a0cdbc",
    "notes": "Text field containing notes",
    "user": "test_user",
  },
  {
    "id": "03a45bbc-9866-47be-890f-2a1ab3a0cdbc",
    "notes": "Text field containing notes",
    "user": "test_user",
  }
]
```

POST create new SurveyPath  
Submit a payload with all the information required for the new path. Include the points in an array.  
Omit Ids. These will be created by the server.  
Include the IANA timezone name with the timestamp in the point data.  
Timestamp should be an integer repesenting a POSIX timestamp in seconds.

```
{
  "notes": "Excavation at the ancient temple site",
  "user": "digmaster45",
  "points": [
    {
      "utm_hemisphere": "N",
      "utm_zone": 33,
      "utm_easting_meters": 479120.234,
      "utm_northing_meters": 4420430.456,
      "latitude": 28.134567,
      "longitude": 111.1346789,
      "source": "R",
      "timestamp": 1695187223,
      "timezone": "Asia/Yerevan"
    },
    {
      "utm_hemisphere": "N",
      "utm_zone": 33,
      "utm_easting_meters": 479235.567,
      "utm_northing_meters": 4420501.987,
      "latitude": 28.135678,
      "longitude": 111.1354543,
      "source": "R",
      "timestamp": 1695187345,
      "timezone": "Asia/Yerevan"      
    },
    {
      "utm_hemisphere": "N",
      "utm_zone": 33,
      "utm_easting_meters": 479341.890,
      "utm_northing_meters": 4420572.890,
      "latitude": 28.136789,
      "longitude": 111.1362297,
      "source": "R",
      "timestamp": 1695187468,
      "timezone": "Asia/Yerevan"      
    }
  ]
}
```


### /asl/api/path/{uuid}/ 
GET retrieve details for path with id {uuid}

Returns:
```
{
  "id": "03a45bbc-9866-47be-890f-2a1ab3a0cdbc"
  "notes": "Text field containing notes"
  "user": "test_user"
  "points": [
    {
    "id": "41bae6e1-a47a-4f45-b90f-5f46df917d97"
    "utm_hemipshere": "N",
    "utm_zone": 38,
    "utm_easting_meters": 478130.123,
    "utm_northing_meters": 4419430.325,
    "latitude": 25.123456,
    "longitude": 110.123456,
    "utm_altitude": 200.1234,
    "source": "R",
    "timestamp": 1695007830469
    },
    // ... additional points in a JSON array
  ]
}
```

PUT update information for path with id {uuid}  
Send the fields to update in the payload
Points included in the PUT request will be created if they are missing the `id` field. If the `id` is included, the existing point with the matching id will be updated in the database.

```
{
  "notes": "updated notes text"
  "points": [
    {
    "utm_hemipshere": "N",
    "utm_zone": 38,
    "utm_easting_meters": 478150.987,
    "utm_northing_meters": 4419480.632,
    "latitude": 25.123456,
    "longitude": 110.123456,
    "utm_altitude": 200.1234,
    "source": "R",
    "timestamp": 1695007830469
  },
  ]
}
```

## Miscellanneous

### /asl/api/timezones
GET list all IANA timezones

Returns a JSON array of available timezones on the server:

```
[
  ...
  Asia/Gaza,
  Asia/Harbin,
  Asia/Hebron,
  Asia/Ho_Chi_Minh,
  Asia/Hong_Kong,
  Asia/Hovd,
  Asia/Irkutsk,
  Asia/Istanbul,
  Asia/Jakarta,
  Asia/Jayapura,
  ...
]

```



