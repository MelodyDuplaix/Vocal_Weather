import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

def get_weather(latitude, longitude, days):
    
    # préparer le client api
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    if isinstance(days, int):
        days_number = days
        days_range = None
    elif isinstance(days, list):
        if len(days) == 2:
            days_number = None
            days_range = days
        else:
            raise ValueError("days_range must be a list of two elements")
    else:
        raise ValueError("days must be an integer or a list")
    
    url = "https://api.open-meteo.com/v1/forecast"
    if days_range == None:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "weather_code", "cloud_cover", "wind_speed_10m"],
            "hourly": ["temperature_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "weather_code", "cloud_cover", "wind_speed_10m"],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum", "rain_sum", "precipitation_hours"],
            "timezone": "Europe/London",
            "forecast_days": days_number
        }
    else:
        if isinstance(days_range, list) and len(days_range) == 2:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "weather_code", "cloud_cover", "wind_speed_10m"],
                "hourly": ["temperature_2m", "apparent_temperature", "precipitation_probability", "precipitation", "rain", "weather_code", "cloud_cover", "wind_speed_10m"],
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum", "rain_sum", "precipitation_hours"],
                "timezone": "Europe/London",
                "start": days_range[0],
                "end": days_range[1]
            }
        else:
            raise ValueError("days_range must be a list of two elements")
    
    # récupération des données
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # récupération des données actuelles
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    current_precipitation = current.Variables(3).Value()
    current_rain = current.Variables(4).Value()
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

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["rain"] = hourly_rain
    hourly_data["weather_code"] = hourly_weather_code
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

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
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours

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