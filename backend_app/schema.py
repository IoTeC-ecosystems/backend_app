
gps_data_schema_str = """{
    "$schema": "https://son-schema.org/draft/2020-12/schema",
    "title": "GPS Data Schema",
    "description": "Coordinates and data obtained from GPS",
    "type": "object",
    "properties": {
        "uuid": {
            "description": "Device uuid",
            "type": "string"
        },
        "latitude": {
            "description": "Device latitude",
            "type": "number"
        },
        "longitude": {
            "description": "Device longitud",
            "type": "number"
        },
        "height": {
            "description": "Device heigth",
            "type": "number"
        },
        "velocity": {
            "description": "Device velocity",
            "type": "number"
        },
        "datetime": {
            "description": "Datetime from GPS module",
            "type": "number"
        }
    }
}
"""
