from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import threading
import pandas as pd
import time
import sys
import os
import json

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI()

# variable globale pour stocker le modèle chargé
ner_model = None

# Fonction pour charger le modèle dans un thread séparé
def load_model_thread():
    global ner_model
    from src.Entities_Extract import load_model
    ner_model = load_model()

def select_weather(dates, hourly, daily):
    weather_data = []
    # Pour une seule date
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
    # Pour un range de date
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

def process_weather_data(file_location):
    from src.Vocal_Transcript import transcribe_from_microphone
    from src.Entities_Extract import extract_entities
    from src.Geolocation import get_geolocation
    from src.Days_Choice import days_number_choice
    from src.Weather_API import get_weather
    from src.Database import create_connexion, insert_data, create_table

    # Commencer à charger le modèle dans un thread séparé
    model_thread = threading.Thread(target=load_model_thread)
    model_thread.start()

    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'code_stt': None,
        'error_message': None,
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
    }

    # Timing for transcription
    start_time = time.time()
    try:
        result = transcribe_from_microphone(file_location)
        transcription_time = time.time() - start_time
        data['response_time_azure'] = transcription_time

        if result["status"] != "success":
            data['code_stt'] = result["status_code"]
            data['error_message'] = result["status"]
            data['original_text'] = result["text"]
            return data, None, None
    except Exception as e:
        data['code_stt'] = 500
        data['error_message'] = f"Transcription error: {str(e)}"
        return data, None, None

    data['original_text'] = result["text"]
    data['code_stt'] = result["status_code"]
    data['error_message'] = result["status"]

    # Attendre la fin du chargement du modèle
    model_thread.join()

    # Timing for entity extraction
    start_time = time.time()
    try:
        entities = extract_entities(result["text"], ner_model)
        extraction_time_entities = time.time() - start_time
        data['extraction_time_entities'] = extraction_time_entities
        data['recognized_entities'] = str(entities)
    except Exception as e:
        data['error_message'] = f"Entity extraction error: {str(e)}"
        return data, None, None

    dates = [date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date, datetime) else date for date in entities['date']]
    data['formatted_dates'] = str(dates)

    if len(entities['localisation']) == 0:
        data['error_message'] = "No location found"
        return data, None, None

    try:
        geolocation = get_geolocation(entities['localisation'][0])
        data['localisation'] = str(geolocation)
    except Exception as e:
        data['error_message'] = f"Geolocation error: {str(e)}"
        return data, None, None

    if isinstance(entities['date'], list) and len(entities['date']) == 0:
        data['error_message'] = "No date found"
        return data, None, None

    days_number = days_number_choice(entities['date'])

    # Timing for weather API call
    start_time = time.time()
    try:
        weather = get_weather(geolocation['latitude'], geolocation['longitude'], days_number)
        weather_api_time = time.time() - start_time
        data['weather_api_time'] = weather_api_time
        data['weather_api_code'] = 200
        data['weather_api_response'] = str(weather)
    except Exception as e:
        data['error_message'] = f"Weather API error: {str(e)}"
        return data, None, None

    current = weather["current"]
    hourly = pd.DataFrame(weather["hourly"])
    daily = pd.DataFrame(weather["daily"])
    weather_df = select_weather(dates, hourly, daily)

    data['weather'] = str(current)

    return data, current, weather_df

@app.post("/weather")
async def process_weather(file: UploadFile = File(...)):
    from src.Database import create_connexion, insert_data, create_table

    # au cas ou le dossier temp n'existe pas
    os.makedirs("temp", exist_ok=True)

    # Enregistrer le fichier audio
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    data, current_weather, weather_df = process_weather_data(file_location)

    # Enregistrer les données dans la base de données
    start_time = time.time()
    engine, LogTable = create_connexion()
    db_connexion_time = time.time() - start_time
    data['db_connexion_time'] = db_connexion_time
    insert_data(engine, data, LogTable)

    if current_weather is None or weather_df is None:
        raise HTTPException(status_code=500, detail=data['error_message'])

    # Convertir les données en JSON
    current_weather_json = json.loads(pd.DataFrame([current_weather]).to_json(orient="records"))[0]
    weather_forecast_json = json.loads(weather_df.to_json(orient="records"))

    return JSONResponse(content={
        "current_weather": current_weather_json,
        "weather_forecast": weather_forecast_json
    })