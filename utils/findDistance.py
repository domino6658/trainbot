import math

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert degrees to radians
    lat_rad1 = math.radians(lat1)
    lon_rad1 = math.radians(lon1)
    lat_rad2 = math.radians(lat2)
    lon_rad2 = math.radians(lon2)

    # Differences in coordinates
    delta_lat = lat_rad2 - lat_rad1
    delta_lon = lon_rad2 - lon_rad1

    # Haversine formula
    a = math.sin(delta_lat / 2)**2 + math.cos(lat_rad1) * math.cos(lat_rad2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance
    distance = R * c

    return distance