import googlemaps
import math


def get_distance_between_locations(api_key, origin, destination):
    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")

    if result['rows'][0]['elements'][0]['status'] == 'OK':
        # Extract distance in meters and convert duration to minutes (round to nearest integer)
        distance_m = result['rows'][0]['elements'][0]['distance']['value']  # Distance in meters
        duration_sec = result['rows'][0]['elements'][0]['duration']['value']  # Duration in seconds
        duration_min = math.ceil(duration_sec / 60)  # Convert to minutes and round up
        return distance_m, duration_min
    else:
        return None, None

