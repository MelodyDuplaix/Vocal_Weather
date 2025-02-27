import sys
import os
from datetime import datetime
import threading
import pandas as pd
import json
import time

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# variable globale pour stocker le modèle chargé
ner_model = None

# Fonction pour charger le modèle dans un thread séparé
def load_model_thread():
    """
    Load the NER model in a separate thread.
    """
    global ner_model
    from src.Entities_Extract import load_model
    ner_model = load_model()

def print_weather(dates, hourly, daily):
    """
    Print the weather data for the given dates.

    Args:
        dates (list): List of dates.
        hourly (Dataframe): Hourly weather data.
        daily (Dataframe): Daily weather data.
    """
    if len(dates) == 1:
        date = datetime.strptime(dates[0], '%Y-%m-%d %H:%M:%S')
        date = date.replace(minute=0, second=0, microsecond=0)
        hour = hourly[hourly['date'] == date.strftime('%Y-%m-%d %H:%M:%S')]
        if not hour.empty:
            print(f"Météo pour le {hour.iloc[0]['date'].strftime('%Y-%m-%d %H:%M:%S')}:")
            print(f"Temperature: {hour.iloc[0]['temperature_2m']}°C")
            print(f"Apparent temperature: {hour.iloc[0]['apparent_temperature']}°C")
            print(f"Weather: {hour.iloc[0]['weather_code']}")
            print(f"Wind speed: {hour.iloc[0]['wind_speed_10m']} km/h")
            print(f"Cloud cover: {hour.iloc[0]['cloud_cover']}%")
            print(f"Precipitation: {hour.iloc[0]['precipitation']} mm")
            print(f"Rain: {hour.iloc[0]['rain']} mm")
            print(f"Precipitation probability: {hour.iloc[0]['precipitation_probability']}%")
    elif len(dates) > 1:
        start_date = min(dates)
        end_date = max(dates)
        for date in pd.date_range(start=start_date, end=end_date, inclusive='both'):
            day = daily[daily['date'] == date.strftime('%Y-%m-%d')]
            if not day.empty:
                print(f"Météo pour le {day.iloc[0]['date'].strftime('%Y-%m-%d')}:")
                print(f"Temperature max: {day.iloc[0]['temperature_2m_max']}°C")
                print(f"Temperature min: {day.iloc[0]['temperature_2m_min']}°C")
                print(f"Apparent temperature max: {day.iloc[0]['apparent_temperature_max']}°C")
                print(f"Apparent temperature min: {day.iloc[0]['apparent_temperature_min']}°C")
                print(f"Weather: {day.iloc[0]['weather_code']}")
                print(f"Precipitation sum: {day.iloc[0]['precipitation_sum']} mm")
                print(f"Rain sum: {day.iloc[0]['rain_sum']} mm")
                print(f"Precipitation hours: {day.iloc[0]['precipitation_hours']} hours")
    else:
        print("No date found")

def get_meteo_from_transcribe():
    """
    Get the weather data from a vocal transcription.
    """
    def dict_to_str(d):
        return str({k: (v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else v) for k, v in d.items()})
    
    print("Vocal transcription:")
    from src.Vocal_Transcript import transcribe_from_microphone
    
    # Commencer à charger le modèle dans un thread séparé
    model_thread = threading.Thread(target=load_model_thread)
    model_thread.start()
    
    # Timing for transcription
    start_time = time.time()
    result = transcribe_from_microphone()
    transcription_time = time.time() - start_time
    
    if result["status"] == "success":
        print(result["text"])
    else:
        print(result["status"])
        raise Exception("Transcription error")

    # Attendre la fin du chargement du modèle
    model_thread.join()

    from src.Entities_Extract import extract_entities
    
    # Timing for entity extraction
    start_time = time.time()
    entities = extract_entities(result["text"], ner_model)
    extraction_time_entities = time.time() - start_time
    
    dates = [date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date, datetime) else date for date in entities['date']]
    print(f"Dates: {dates}")
    print(f"Localisations: {entities['localisation']}")
    
    from src.Geolocation import get_geolocation
    if len(entities['localisation']) == 0:
        print("No location found")
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'code_stt': result["status_code"],
            'error_message': result["status"],
            'original_text': result["text"],
            'response_time_azure': transcription_time,
            'recognized_entities': dict_to_str(entities),
            'extraction_time_entities': extraction_time_entities,
            'formatted_dates': None,
            'localisation': None,
            'weather_api_code': None,
            'weather_api_time': None,
            'weather_api_response': None,
            'weather': None
        }
    geolocation = get_geolocation(entities['localisation'][0])
    print(f"Latitude: {geolocation['latitude']}")
    print(f"Longitude: {geolocation['longitude']}")
    print(f"City: {geolocation['city']}")
    print(f"Status: {geolocation['status']}")
    
    if isinstance(entities['date'], list) and len(entities['date']) == 0:
        print("No date found")
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'code_stt': result["status_code"],
            'error_message': result["status"],
            'original_text': result["text"],
            'response_time_azure': transcription_time,
            'recognized_entities': dict_to_str(entities),
            'extraction_time_entities': None,
            'formatted_dates': str(dates),
            'localisation': dict_to_str(geolocation),
            'weather_api_code': None,
            'weather_api_time': None,
            'weather_api_response': None,
            'weather': None
        }
    if isinstance(entities['date'], list) and len(entities['date']) == 1 and isinstance(entities['date'][0], str):
        print("No date found")
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'code_stt': result["status_code"],
            'error_message': result["status"],
            'original_text': result["text"],
            'response_time_azure': transcription_time,
            'recognized_entities': None,
            'extraction_time_entities': None,
            'formatted_dates': str(dates),
            'localisation': dict_to_str(geolocation),
            'weather_api_code': None,
            'weather_api_time': None,
            'weather_api_response': None,
            'weather': None
        }
    from src.Days_Choice import days_number_choice
    days_number = days_number_choice(entities['date'])
    print(f"nombre de jour {days_number}")
    
    from src.Weather_API import get_weather
    
    # Timing for weather API call
    start_time = time.time()
    weather = get_weather(geolocation['latitude'], geolocation['longitude'], days_number)
    weather_api_time = time.time() - start_time

    current = weather["current"]
    print(f"Current temperature: {current['temperature_2m']}°C")
    print(f"Current weather: {current['weather_code']}")
    print(f"Current humidity: {current['relative_humidity_2m']}%")
    print(f"Current wind speed: {current['wind_speed_10m']} km/h")
    print(f"Current cloud cover: {current['cloud_cover']}%")
    print(f"Current precipitation: {current['precipitation']} mm")
    print(f"Current rain: {current['rain']} mm")
    print(f"Current apparent temperature: {current['apparent_temperature']}°C")

    hourly = pd.DataFrame(weather["hourly"])
    daily = pd.DataFrame(weather["daily"])
    print_weather(dates, hourly, daily)
    

    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'code_stt': result["status_code"],
        'error_message': result["status"],
        'original_text': result["text"],
        'response_time_azure': transcription_time,
        'recognized_entities': dict_to_str(entities),
        'extraction_time_entities': extraction_time_entities,
        'formatted_dates': str(dates),
        'localisation': dict_to_str(geolocation),
        'weather_api_code': 200,
        'weather_api_time': weather_api_time,
        'weather_api_response': dict_to_str(weather),
        'weather': dict_to_str(current)
    }
    return data
    
    
def main():
    from src.Database import create_connexion, insert_data, create_table
    start_time = time.time()
    engine, LogTable = create_connexion()
    db_connexion_time = time.time() - start_time
    data = get_meteo_from_transcribe()
    data['db_connexion_time'] = db_connexion_time
    insert_data(engine, data, LogTable)

if __name__ == "__main__":
    main()