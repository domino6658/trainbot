import math


def find_closest_coordinates(target_coordinates, n=5):
    target_lat, target_lon = target_coordinates

    with open('newcoords.csv', 'r') as f:
        distances = []
        for line in f:
            data = line.strip().replace('\n','').split(',')
            category, name, description, lat, lon = data

            distance = haversine(target_lon, target_lat, lon, lat)
            distances.append((data, distance))

    distances.sort(key=lambda x: x[1])  # Sort by distance
    closest_coordinates = distances[:n]

    return closest_coordinates


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert degrees to radians
    lat_rad1 = int(math.radians(lat1))
    lon_rad1 = int(math.radians(lon1))
    lat_rad2 = int(math.radians(lat2))
    lon_rad2 = int(math.radians(lon2))

    # Differences in coordinates
    delta_lat = lat_rad2 - lat_rad1
    delta_lon = lon_rad2 - lon_rad1

    # Haversine formula
    a = math.sin(delta_lat / 2)**2 + math.cos(lat_rad1) * math.cos(lat_rad2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance
    distance = R * c

    return distance