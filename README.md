# Vocal weather

## Description

Application de météo par demande vocale

Cette application permet de demander la météo pour un lieu et date(s) donnée(s).


## Fonctionnalités

* Demander de météo par une demande vocale
* Demander la météo en écrivant le lieu et en choisissant la date
* Affichage de la météo pour le lieu et date(s) choisie
* possibilité de choisir une date, une date et heure, ou un intervalle de date
* monitoring de l'application sur une base de données

## Technologies utilisées

* Python - FastAPI pour le backend
* Next.js - React pour le frontend
* Base de données Azure PostGreSQL pour le monitoring de l'application

Utilisation de services externes:
* Service Azure Speech-to-text pour transcrire la voix en texte
* Modèle [CamemBERT-NER-with-dates](https://huggingface.co/Jean-Baptiste/camembert-ner-with-dates) d'hugging face pour l'extraction des entités depuis le texte transcrit
* API d'adresse data gouv pour géolocaliser les lieux
* API d'Open Meteo pour obtenir la météo

## Installation

installer [ffmpeg](https://ffmpeg.org/)

Créer un fichier .env à la racine:
```txt
# POUR LE SERVICE SPEECH-TO-TEXT
SPEECH_KEY=<clé api du service speech-to-text>
SPEECH_REGION=francecentral
# POUR LA BASE DE DONNÉES
DATABASE_URL="<url de connexion à la base de données>"
```

installation des dépendences:
```bash
pip install -r requirements.txt
```

lancement de l'api:
```bash
fastapi dev .\app\app.py
```

lancement de l'application:
```bash
cd .\frontend\vocal_weather\
npm run dev
```

## Utilisation de l'application

Deux possibilité pour obtenir la météo:

* Cliquer sur le bouton du micro, puis énoncer sa demande à haute voix, par exemple *"Je souhaite la météo de demain à 19h à Tours"* ou encore *"J'aimerais la météo dans 2 jours jusque dans 5 jours à Bordeaux"*
* Entrer un lieu (ville, adresse, département) dans le champs de texte, choisir à l'aide du menu déroulant si l'on souhaite une date ou un intervalle de date, puis rentrer la ou les dates et heure dans les champs de date, et enfin cliquer sur Chercher

La météo s'affichera pour le ou les jours concernés au dessus du bouton du micro.

## Utilisation de l'API

L'API propose trois endpoints pour obtenir les informations météorologiques :

*   **POST /weather**
    *   Description: Cet endpoint accepte un fichier audio, le transcrit en texte, extrait les informations de date et de lieu, et retourne les prévisions météorologiques correspondantes.
    *   Input: Un fichier audio (e.g., \*.wav, \*.mp3).
    *   Output: Un JSON contenant la météo actuelle (`current_weather`), les prévisions (`weather_forecast`) et la localisation (`location`).
    *   Example:
        ```bash
        curl -X POST -F "file=@audio.wav" http://localhost:8000/weather
        ```

*   **POST /weather-from-text**
    *   Description: Cet endpoint accepte une chaîne de caractères en entrée, extrait les informations de date et de lieu, et retourne les prévisions météorologiques correspondantes.
    *   Input: Une chaîne de caractères (text).
    *   Output: Un JSON contenant la météo actuelle (`current_weather`), les prévisions (`weather_forecast`) et la localisation (`location`).
    *   Example:
        ```bash
        curl -X POST -H "Content-Type: application/json" -d '"Je souhaite la météo de demain à 19h à Tours"' http://localhost:8000/weather-from-text
        ```

*   **POST /weather-from-entities**
    *   Description: Cet endpoint accepte une liste de dates et un lieu en entrée et retourne les prévisions météorologiques correspondantes.
    *   Input: Un JSON contenant une liste de dates (`dates`) et un lieu (`location`).
    *   Output: Un JSON contenant la météo actuelle (`current_weather`), les prévisions (`weather_forecast`) et la localisation (`location`).
    *   Example:
        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"dates": ["2025-03-02 19:00:00"], "location": "Tours"}' http://localhost:8000/weather-from-entities
