import requests


def get_coordinates(address, api_key):
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': api_key
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        results = response.json()
        if results['status'] == 'OK':
            location = results['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Error fetching coordinates: {results['status']}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
    except ValueError as e:
        print(f"Error decoding JSON response: {e}")
    return None, None
