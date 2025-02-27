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

def select_weather(dates, hourly, daily):
    """
    Select the weather data for the given dates.

    Args:
        dates (list): List of dates. 
        hourly (Dataframe): Hourly weather data. 
        daily (Dataframe): Daily weather data.

    Returns:
        (dict, Dataframe, Dataframe) : A tuple containing the data, the current weather dataframe and the weather forecast dataframe.
    """
    weather_data = []
    if len(dates) == 1:
        date = datetime.strptime(dates[0], '%Y-%m-%d %H:%M:%S')
        date = date.replace(minute=0, second=0, microsecond=0)
        hour = hourly[hourly['date'] == date.strftime('%Y-%m-%d %H:%M:%S')]
        if not hour.empty:
            weather_data.append({
                'date': hour.iloc[0]['date'],
                'temperature': hour.iloc[0]['temperature_2m'],
                'apparent_temperature': hour.iloc[0]['apparent_temperature'],
                'weather': hour.iloc[0]['weather_code'],
                'wind_speed': hour.iloc[0]['wind_speed_10m'],
                'cloud_cover': hour.iloc[0]['cloud_cover'],
                'precipitation': hour.iloc[0]['precipitation'],
                'rain': hour.iloc[0]['rain'],
                'precipitation_probability': hour.iloc[0]['precipitation_probability']
            })
    elif len(dates) > 1:
        start_date = min(dates)
        end_date = max(dates)
        for date in pd.date_range(start=start_date, end=end_date, inclusive='both'):
            day = daily[daily['date'] == date.strftime('%Y-%m-%d')]
            if not day.empty:
                weather_data.append({
                    'date': day.iloc[0]['date'],
                    'temperature_max': day.iloc[0]['temperature_2m_max'],
                    'temperature_min': day.iloc[0]['temperature_2m_min'],
                    'apparent_temperature_max': day.iloc[0]['apparent_temperature_max'],
                    'apparent_temperature_min': day.iloc[0]['apparent_temperature_min'],
                    'weather': day.iloc[0]['weather_code'],
                    'precipitation_sum': day.iloc[0]['precipitation_sum'],
                    'rain_sum': day.iloc[0]['rain_sum'],
                    'precipitation_hours': day.iloc[0]['precipitation_hours']
                })
    return pd.DataFrame(weather_data)

def get_meteo_from_transcribe():
    
    def dict_to_str(d):
        return str({k: (v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime) else v) for k, v in d.items()})
    
    print("Vocal transcription:")
    from src.Vocal_Transcript import transcribe_from_microphone
    
    # Commencer à charger le modèle dans un thread séparé
    model_thread = threading.Thread(target=load_model_thread)
    model_thread.start()
    
    # Timing for transcription
    start_time = time.time()
    try:
        result = transcribe_from_microphone()
    except Exception as e:
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'code_stt': 500,
            'error_message': str(e),
            'original_text': None,
            'response_time_azure': None,
            'recognized_entities': None,
            'extraction_time_entities': None,
            'formatted_dates': None,
            'localisation': None,
            'weather_api_code': None,
            'weather_api_time': None,
            'weather_api_response': None,
            'weather': None
        }, None, None
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
        }, None, None
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
        }, None, None
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
        }, None, None
    from src.Days_Choice import days_number_choice
    days_number = days_number_choice(entities['date'])
    print(f"nombre de jour {days_number}")
    
    from src.Weather_API import get_weather
    
    # Timing for weather API call
    start_time = time.time()
    weather = get_weather(geolocation['latitude'], geolocation['longitude'], days_number)
    weather_api_time = time.time() - start_time

    current = weather["current"]

    hourly = pd.DataFrame(weather["hourly"])
    daily = pd.DataFrame(weather["daily"])
    weather_df = select_weather(dates, hourly, daily)
    

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
    return data, pd.DataFrame([current]), weather_df
    
    
def main():
    from src.Database import create_connexion, insert_data, create_table
    start_time = time.time()
    engine, LogTable = create_connexion()
    db_connexion_time = time.time() - start_time
    data, current_weather_df, weather_df = get_meteo_from_transcribe()
    data['db_connexion_time'] = db_connexion_time
    insert_data(engine, data, LogTable)

    if current_weather_df is not None and not current_weather_df.empty:
        print("Current Weather:")
        print(current_weather_df.to_string(index=False))

    if weather_df is not None and not weather_df.empty:
        print("Weather Forecast:")
        for index, row in weather_df.iterrows():
            print(f"Date: {row['date']}")
            optional_fields = [
                ('temperature', 'Temperature', '°C'),
                ('temperature_max', 'Temperature Max', '°C'),
                ('temperature_min', 'Temperature Min', '°C'),
                ('apparent_temperature', 'Apparent Temperature', '°C'),
                ('apparent_temperature_max', 'Apparent Temperature Max', '°C'),
                ('apparent_temperature_min', 'Apparent Temperature Min', '°C'),
                ('wind_speed', 'Wind Speed', 'm/s'),
                ('cloud_cover', 'Cloud Cover', '%'),
                ('precipitation', 'Precipitation', 'mm'),
                ('rain', 'Rain', 'mm'),
                ('precipitation_probability', 'Precipitation Probability', '%'),
                ('precipitation_sum', 'Precipitation Sum', 'mm'),
                ('rain_sum', 'Rain Sum', 'mm'),
                ('precipitation_hours', 'Precipitation Hours', 'hours')
            ]
            for field, label, unit in optional_fields:
                if field in row:
                    print(f"{label}: {row[field]}{unit}")
            print(f"Weather: {row['weather']}")
            print("-" * 20)
        

if __name__ == "__main__":
    main()