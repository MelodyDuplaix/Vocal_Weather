import pytest
import pandas as pd
from datetime import datetime
from fastapi.testclient import TestClient
from app.app import select_weather, process_entities, process_text, process_weather_data, app

def test_select_weather():
    hourly_data = pd.DataFrame({
        'date': ['2025-03-03 14:00:00'],
        'temperature_2m': [10],
        'apparent_temperature': [9],
        'weather_code': ['Clear'],
        'wind_speed_10m': [5],
        'cloud_cover': [0],
        'precipitation': [0],
        'rain': [0],
        'precipitation_probability': [0],
    })

    daily_data = pd.DataFrame({
        'date': ['2025-03-03'],
        'temperature_2m_max': [15],
        'temperature_2m_min': [5],
        'apparent_temperature_max': [14],
        'apparent_temperature_min': [4],
        'weather_code': ['Clear'],
        'precipitation_sum': [0],
        'rain_sum': [0],
        'precipitation_hours': [0],
    })
 
    dates = ['2025-03-03 14:10:00']
    result = select_weather(dates, hourly_data, daily_data)
    assert result is not None
    assert result['temperature'].iloc[0] == 10

    dates = ['2025-03-03', '2025-03-04']
    result = select_weather(dates, hourly_data, daily_data)
    assert result is not None


def test_process_entities():
    dates = ['2025-03-03 14:00:00']
    location = 'Paris'

    data, current, weather_df = process_entities(dates, location)
    
    assert data['error_message'] is None
    assert data['weather_api_code'] == 200
    assert current is not None
    assert weather_df is not None

def test_process_text():
    text = "Quel temps fera-t-il le 2025-03-03 à Paris ?"

    data, current, weather_df = process_text(text)
    
    assert data['error_message'] is None
    assert data['formatted_dates'] == "['2025-03-03 00:00:00']"
    assert current is not None
    assert weather_df is not None

def test_process_weather_data():
    file_location = "temp/enregistrement.wav"

    data, current, weather_df = process_weather_data(file_location)

    assert data['error_message'] is "success"
    assert current is not None
    assert weather_df is not None

client = TestClient(app)
def test_weather_request():
    response = client.post(
        "/weather-from-entities", json={"dates": ["2025-03-03 14:00:00"], "location": "Paris"}
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "weather_forecast" in json_response
