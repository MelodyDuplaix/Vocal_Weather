from urllib import response
import requests
import json

def get_geolocation(location):
    """
    Get the geolocation of a location based on its name.

    Args:
        location (string): The name of the location.

    Returns:
        dict: A dictionary containing the latitude, the longitude, the city and the status of the request.
    """
    url = f"https://api-adresse.data.gouv.fr/search/?q={location}&limit=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response:
            data = json.loads(response.text)
            latitude = data["features"][0]["geometry"]["coordinates"][1]
            longitude = data["features"][0]["geometry"]["coordinates"][0]
            City = data["features"][0]["properties"]["city"]
            return {
                "latitude": latitude,
                "longitude": longitude,
                "city": City,
                "status": "success"
            }
        else:
            return {
                "latitude": None,
                "longitude": None,
                "city": None,
                "status": "Error: No data found"
            }
    except requests.exceptions.RequestException as e:
        return  {
            "latitude": None,
            "longitude": None,
            "city": None,
            "status": f"Error during request: {e}"
        }
    except json.JSONDecodeError as e:
        return {
            "latitude": None,
            "longitude": None,
            "city": None,
            "status": f"Error during JSON decoding: {e}"
        }
    except:
        return {
            "latitude": None,
            "longitude": None,
            "city": None,
            "status": f"Localisation non trouvée"
        }
        
if __name__ == "__main__":
    location = input("Entrez la localisation: ")
    geolocation = get_geolocation(location)
    print(f"Latitude: {geolocation['latitude']}")
    print(f"Longitude: {geolocation['longitude']}")
    print(f"City: {geolocation['city']}")
    print(f"Status: {geolocation['status']}")