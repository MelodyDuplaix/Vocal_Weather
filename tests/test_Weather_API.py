import pytest
import pandas as pd
from src.Weather_API import get_weather

def test_get_weather_valid_input():
    latitude = 48.8566
    longitude = 2.3522
    days = 5
    weather = get_weather(latitude, longitude, days)

    assert "current" in weather
    assert "hourly" in weather
    assert "daily" in weather
    assert isinstance(weather["current"], dict)
    assert isinstance(weather["hourly"], pd.DataFrame)
    assert isinstance(weather["daily"], pd.DataFrame)
    assert len(weather["hourly"]) > 0
    assert len(weather["daily"]) > 0

def test_get_weather_invalid_days_type():
    latitude = 48.8566
    longitude = 2.3522
    with pytest.raises(ValueError, match="days must be an integer"):
        get_weather(latitude, longitude, "five")


def test_get_weather_missing_data():
    latitude = 0 
    longitude = 0
    days = 5
    weather = get_weather(latitude, longitude, days)

    assert "current" in weather
    assert "hourly" in weather
    assert "daily" in weather
    assert weather["current"]["temperature_2m"] is not None
    assert len(weather["hourly"]) > 0
    assert len(weather["daily"]) > 0
