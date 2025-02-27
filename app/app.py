from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import threading
import pandas as pd
import time
import sys
import os
import json
from pydub import AudioSegment
from pydantic import BaseModel
from typing import List, Callable, Any

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.Database import create_connexion, insert_data, create_table

app = FastAPI()

# Ajout des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# variable globale pour stocker le modèle chargé
ner_model = None

# Fonction pour charger le modèle dans un thread séparé
def load_model_thread():
    global ner_model
    from src.Entities_Extract import load_model
    ner_model = load_model()

def select_weather(dates, hourly, daily):
    """
    Récupère les bonnes données des dataframes hourly  et daily selon les dates.

    Args:
        dates (list[str]): Dates de recherche de la météo.
        hourly (Dataframe): dataframe de la météo par heure
        daily (Dataframe): dataframe de la météo par jour

    Returns:
        Dataframe: Dataframe de la météo des date(s) demandé(s)
    """
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
        else:
            weather_data = None
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
            else:
                weather_data = None
    return pd.DataFrame(weather_data) if weather_data is not None else None

def process_entities(dates, location):
    """
    Traite les dates et localisation pour récupérer la météo par l'api Open Meteo.

    Args:
        dates (list[str]): Date ou dates de recherche de météos.
        location (list[str]]): Lieu de recherche de la météos.

    Returns:
        dict: données de monitoring, et résultas de la météo
    """
    from src.Geolocation import get_geolocation
    from src.Days_Choice import days_number_choice
    from src.Weather_API import get_weather

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
    data['response_time_azure'] = None
    data['original_text'] = None
    data['code_stt'] = None
    data['error_message'] = None
    data['extraction_time_entities'] = None
    data['recognized_entities'] = None
    data['formatted_dates'] = str(dates)

    if len(location) == 0:
        data['error_message'] = "Pas de lieu compris"
        return data, None, None

    try:
        geolocation = get_geolocation(location)
        data['localisation'] = str(geolocation)
    except Exception as e:
        data['error_message'] = f"Geolocation error: {str(e)}"
        return data, None, None

    if data['formatted_dates'] == "[]":
        data['error_message'] = "Pas de date(s) comprise(s)"
        return data, None, None

    days_number = days_number_choice([datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in dates])

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

def process_text(text: str):
    """
    Traite le texte pour récupérer les entités et traiter la demande de météo
    en envoyant à process_entities, pour récupérer la météo selon la demande textuelle

    Args:
        text (str): Demande de météo textuelle

    Returns:
        dict: données de monitoring, et résultas de la météo
    """
    from src.Entities_Extract import extract_entities

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
    data['response_time_azure'] = None
    data['original_text'] = text
    data['code_stt'] = None
    data['error_message'] = None

    # Attendre la fin du chargement du modèle
    model_thread.join()
    # TODO: refactoriser cette fonction pour pouvoir la réutiliser dans process_weather_data séparément du thread

    # Timing for entity extraction
    start_time = time.time()
    try:
        entities = extract_entities(text, ner_model)
        extraction_time_entities = time.time() - start_time
        data['extraction_time_entities'] = extraction_time_entities
        data['recognized_entities'] = str(entities)
    except Exception as e:
        data['error_message'] = f"Entity extraction error: {str(e)}"
        return data, None, None

    dates = [date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date, datetime) else date for date in entities['date']]
    data['formatted_dates'] = str(dates)
    
    if data['formatted_dates'] == "[]":
        data['error_message'] = "Pas de date(s) comprise"
        return data, None, None

    if len(entities["localisation"]) >= 1:
        data_ent, current, weather_df = process_entities(dates, entities['localisation'][0])
        data["localisation"] = data_ent["localisation"]
        data["weather_api_code"] = data_ent["weather_api_code"]
        data["weather_api_time"] = data_ent["weather_api_time"]
        data["weather_api_response"] = data_ent["weather_api_response"]
        data["weather"] = data_ent["weather"]
    else:
        data["error_message"] = "Pas de lieu compris"
        data["localisation"] = None
        data["weather_api_code"] = None
        data["weather_api_time"] = None
        data["weather_api_response"] = None
        data["weather"] = None
        current = None
        weather_df = None

    return data, current, weather_df

def process_weather_data(file_location):
    
    """
    Traite le fichier audio pour en extraite la demande de météo
    et récupérér les données météo demandé.

    Args:
        file_location (str): Chemin du fichier audio à traiter

    Returns:
        dict: données de monitoring, et résultas de la météo
    """
    from src.Vocal_Transcript import transcribe_from_microphone
    from src.Entities_Extract import extract_entities
    from src.Geolocation import get_geolocation
    from src.Days_Choice import days_number_choice
    from src.Weather_API import get_weather

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

    if len(entities["localisation"]) >= 1:
        data_ent, current, weather_df = process_entities(dates, entities['localisation'][0])
        data["localisation"] = data_ent["localisation"]
        data["weather_api_code"] = data_ent["weather_api_code"]
        data["weather_api_time"] = data_ent["weather_api_time"]
        data["weather_api_response"] = data_ent["weather_api_response"]
        data["weather"] = data_ent["weather"]
        if weather_df is None:
            if data["formatted_dates"] == "[]":
                data["error_message"] = "Pas de date(s) comprise"
            else:
                data["error_message"] = "Pas de météo trouvé, date trop lointaine ou passée"
    else:
        data["error_message"] = "Pas de lieu compris"
        data["localisation"] = None
        data["weather_api_code"] = None
        data["weather_api_time"] = None
        data["weather_api_response"] = None
        data["weather"] = None
        current = None
        weather_df = None

    return data, current, weather_df

class WeatherRequest(BaseModel):
    dates: List[str]
    location: str

async def process_weather_request(processing_function: Callable[..., Any],*args, **kwargs) -> JSONResponse:
    """
    Gère la partie commune des routes de demande météo 
    avec les timings de monitoring et l'enregistrement en base de données
    et l'appel des fonctions correspondante pour récupérer la météo

    Args:
        processing_function (function): fonction spécifique à la route à appelé pour processer les données

    Returns:
        JSONReponse: données de météo actuelle et localisation en json
    """
    
    data, current_weather, weather_df = processing_function(*args, **kwargs)

    # Enregistrer les données dans la base de données
    start_time = time.time()
    engine, LogTable = create_table()
    db_connexion_time = time.time() - start_time
    data["db_connexion_time"] = db_connexion_time
    insert_data(engine, data, LogTable)

    if current_weather is None or weather_df is None:
        return JSONResponse(content={"error": data["error_message"]})

    # Convertir les données en JSON
    current_weather_json = json.loads(pd.DataFrame([current_weather]).to_json(orient="records"))[0]
    weather_forecast_json = json.loads(weather_df.to_json(orient="records"))

    return JSONResponse(content={
        "current_weather": current_weather_json,
        "weather_forecast": weather_forecast_json,
        "location": data.get("localisation")
    })

@app.post("/weather")
async def process_weather(file: UploadFile = File(...)):

    os.makedirs("temp", exist_ok=True)
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    if not os.path.exists(file_location):
        return JSONResponse(content={"error": "file not saved correctly"})

    print(f"File saved at {file_location}")

    audio = AudioSegment.from_file(file_location)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(file_location, format="wav")

    return await process_weather_request(process_weather_data, file_location)

@app.post("/weather-from-text")
async def process_weather_from_text(text: str):
    return await process_weather_request(process_text, text)

@app.post("/weather-from-entities")
async def weather_from_entities(request: WeatherRequest, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return await process_weather_request(process_entities, request.dates, request.location)