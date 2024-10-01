import googlemaps


def get_distance_between_locations(api_key, origin, destination):

    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode="driving")

    if result['rows'][0]['elements'][0]['status'] == 'OK':
        distance_km = result['rows'][0]['elements'][0]['distance']['value'] / 1000  # distance in kilometers
        return distance_km
    else:
        return None

