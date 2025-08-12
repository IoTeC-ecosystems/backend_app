"""
Contains all the oject representations for the schemas,
along with their dict_to_obj funtion.
"""

class GPSData(object):
    def __init__(self, uuid, latitude, longitude, height, velocity, datetime):
        self.uuid = uuid
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.velocity = velocity
        self.datetime = datetime

def dict_to_gpsdata(dict, ctx):
    return GPSData(dict["uuid"], dict["latitude"], dict["longitude"],
                   dict["height"], dict["velocity"], dict["datetime"])

def gpsdata_to_dict(gpsdata, ctx):
    return {"uuid": gpsdata.uuid,
            "latitude": gpsdata.latitude,
            "longitude": gpsdata.longitude,
            "height": gpsdata.height,
            "velocity": gpsdata.velocity,
            "datetime": gpsdata.datetime,}
