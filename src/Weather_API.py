import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

def get_weather(latitude, longitude, days):
    """
    Get the weather forecast for a location based on its latitude and longitude.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        days (int): The number of days to forecast.

    Raises:
        ValueError: If days is not an integer.

    Returns:
        dict: A dictionary containing the current weather, the hourly weather and the daily weather.
    """
    
    # préparer le client api
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    # vérifier si days est un entier, vérifier leur validité et attribuer les variables
    if isinstance(days, int):
        days_number = days
    else:
        raise ValueError("days must be an integer")
    
    # préparer les paramètres de la requête
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "weather_code", "cloud_cover", "wind_speed_10m"],
        "hourly": ["temperature_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "weather_code", "cloud_cover", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum", "rain_sum", "precipitation_hours"],
        "timezone": "Europe/London",
        "forecast_days": days_number
    }
    
    # récupération des données
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # récupération des données actuelles
    current = response.Current()
    current_temperature_2m = round(current.Variables(0).Value(), 2)
    current_relative_humidity_2m = round(current.Variables(1).Value(), 2)
    current_apparent_temperature = round(current.Variables(2).Value(), 2)
    current_precipitation = round(current.Variables(3).Value(), 2)
    current_rain = round(current.Variables(4).Value(), 2)
    current_weather_code = current.Variables(5).Value()
    current_cloud_cover = current.Variables(6).Value()
    current_wind_speed_10m = current.Variables(7).Value()
    
    # Récupération des donnés par heure
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_apparent_temperature_2m =  hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
    hourly_rain = hourly.Variables(4).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(7).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = [round(x, 2) for x in hourly_temperature_2m.tolist()]
    hourly_data["apparent_temperature"] = [round(x, 2) for x in hourly_apparent_temperature_2m.tolist()]
    hourly_data["precipitation_probability"] = [round(x, 2) for x in hourly_precipitation_probability.tolist()]
    hourly_data["precipitation"] = [round(x, 2) for x in hourly_precipitation.tolist()]
    hourly_data["rain"] = [round(x, 2) for x in hourly_rain.tolist()]
    hourly_data["weather_code"] = hourly_weather_code
    hourly_data["cloud_cover"] = [round(x, 2) for x in hourly_cloud_cover.tolist()]
    hourly_data["wind_speed_10m"] = [round(x, 2) for x in hourly_wind_speed_10m.tolist()]

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    
    # Récupération des données par jour
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(6).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(7).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["weather_code"] = daily_weather_code
    daily_data["temperature_2m_max"] = [round(x, 2) for x in daily_temperature_2m_max.tolist()]
    daily_data["temperature_2m_min"] = [round(x, 2) for x in daily_temperature_2m_min.tolist()]
    daily_data["apparent_temperature_max"] = [round(x, 2) for x in daily_apparent_temperature_max.tolist()]
    daily_data["apparent_temperature_min"] = [round(x, 2) for x in daily_apparent_temperature_min.tolist()]
    daily_data["precipitation_sum"] = [round(x, 2) for x in daily_precipitation_sum.tolist()]
    daily_data["rain_sum"] = [round(x, 2) for x in daily_rain_sum.tolist()]
    daily_data["precipitation_hours"] = [round(x, 2) for x in daily_precipitation_hours.tolist()]

    daily_dataframe = pd.DataFrame(data = daily_data)
    
    return {
        "current": {
            "temperature_2m": current_temperature_2m,
            "relative_humidity_2m": current_relative_humidity_2m,
            "apparent_temperature": current_apparent_temperature,
            "precipitation": current_precipitation,
            "rain": current_rain,
            "weather_code": current_weather_code,
            "cloud_cover": current_cloud_cover,
            "wind_speed_10m": current_wind_speed_10m
        },
        "hourly": hourly_dataframe,
        "daily": daily_dataframe
    }
    
if __name__ == "__main__":
    latitude = input("Entrez la latitude: ")
    longitude = input("Entrez la longitude: ")
    weather = get_weather(latitude, longitude, 16)
    print(f"Current weather: {weather['current']}")
    print(f"Hourly weather: {weather['hourly']}")
    print(f"Daily weather: {weather['daily']}")
