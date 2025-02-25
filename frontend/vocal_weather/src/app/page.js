"use client";

import { useState, useRef, useEffect } from "react";
import { TiMicrophoneOutline } from "react-icons/ti";
import styles from "./page.module.css";

// Dictionnaire des codes météo
const weatherCodes = {
  "0": { "day": { "description": "Sunny", "image": "http://openweathermap.org/img/wn/01d@2x.png" }, "night": { "description": "Clear", "image": "http://openweathermap.org/img/wn/01n@2x.png" } },
  "1": { "day": { "description": "Mainly Sunny", "image": "http://openweathermap.org/img/wn/01d@2x.png" }, "night": { "description": "Mainly Clear", "image": "http://openweathermap.org/img/wn/01n@2x.png" } },
  "2": { "day": { "description": "Partly Cloudy", "image": "http://openweathermap.org/img/wn/02d@2x.png" }, "night": { "description": "Partly Cloudy", "image": "http://openweathermap.org/img/wn/02n@2x.png" } },
  "3": { "day": { "description": "Cloudy", "image": "http://openweathermap.org/img/wn/03d@2x.png" }, "night": { "description": "Cloudy", "image": "http://openweathermap.org/img/wn/03n@2x.png" } },
  "45": { "day": { "description": "Foggy", "image": "http://openweathermap.org/img/wn/50d@2x.png" }, "night": { "description": "Foggy", "image": "http://openweathermap.org/img/wn/50n@2x.png" } },
  "48": { "day": { "description": "Rime Fog", "image": "http://openweathermap.org/img/wn/50d@2x.png" }, "night": { "description": "Rime Fog", "image": "http://openweathermap.org/img/wn/50n@2x.png" } },
  "51": { "day": { "description": "Light Drizzle", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Light Drizzle", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "53": { "day": { "description": "Drizzle", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Drizzle", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "55": { "day": { "description": "Heavy Drizzle", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Heavy Drizzle", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "56": { "day": { "description": "Light Freezing Drizzle", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Light Freezing Drizzle", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "57": { "day": { "description": "Freezing Drizzle", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Freezing Drizzle", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "61": { "day": { "description": "Light Rain", "image": "http://openweathermap.org/img/wn/10d@2x.png" }, "night": { "description": "Light Rain", "image": "http://openweathermap.org/img/wn/10n@2x.png" } },
  "63": { "day": { "description": "Rain", "image": "http://openweathermap.org/img/wn/10d@2x.png" }, "night": { "description": "Rain", "image": "http://openweathermap.org/img/wn/10n@2x.png" } },
  "65": { "day": { "description": "Heavy Rain", "image": "http://openweathermap.org/img/wn/10d@2x.png" }, "night": { "description": "Heavy Rain", "image": "http://openweathermap.org/img/wn/10n@2x.png" } },
  "66": { "day": { "description": "Light Freezing Rain", "image": "http://openweathermap.org/img/wn/10d@2x.png" }, "night": { "description": "Light Freezing Rain", "image": "http://openweathermap.org/img/wn/10n@2x.png" } },
  "67": { "day": { "description": "Freezing Rain", "image": "http://openweathermap.org/img/wn/10d@2x.png" }, "night": { "description": "Freezing Rain", "image": "http://openweathermap.org/img/wn/10n@2x.png" } },
  "71": { "day": { "description": "Light Snow", "image": "http://openweathermap.org/img/wn/13d@2x.png" }, "night": { "description": "Light Snow", "image": "http://openweathermap.org/img/wn/13n@2x.png" } },
  "73": { "day": { "description": "Snow", "image": "http://openweathermap.org/img/wn/13d@2x.png" }, "night": { "description": "Snow", "image": "http://openweathermap.org/img/wn/13n@2x.png" } },
  "75": { "day": { "description": "Heavy Snow", "image": "http://openweathermap.org/img/wn/13d@2x.png" }, "night": { "description": "Heavy Snow", "image": "http://openweathermap.org/img/wn/13n@2x.png" } },
  "77": { "day": { "description": "Snow Grains", "image": "http://openweathermap.org/img/wn/13d@2x.png" }, "night": { "description": "Snow Grains", "image": "http://openweathermap.org/img/wn/13n@2x.png" } },
  "80": { "day": { "description": "Light Showers", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Light Showers", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "81": { "day": { "description": "Showers", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Showers", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "82": { "day": { "description": "Heavy Showers", "image": "http://openweathermap.org/img/wn/09d@2x.png" }, "night": { "description": "Heavy Showers", "image": "http://openweathermap.org/img/wn/09n@2x.png" } },
  "85": { "day": { "description": "Light Snow Showers", "image": "http://openweathermap.org/img/wn/13d@2x.png" }, "night": { "description": "Light Snow Showers", "image": "http://openweathermap.org/img/wn/13n@2x.png" } },
  "86": { "day": { "description": "Snow Showers", "image": "http://openweathermap.org/img/wn/13d@2x.png" }, "night": { "description": "Snow Showers", "image": "http://openweathermap.org/img/wn/13n@2x.png" } },
  "95": { "day": { "description": "Thunderstorm", "image": "http://openweathermap.org/img/wn/11d@2x.png" }, "night": { "description": "Thunderstorm", "image": "http://openweathermap.org/img/wn/11n@2x.png" } },
  "96": { "day": { "description": "Light Thunderstorms With Hail", "image": "http://openweathermap.org/img/wn/11d@2x.png" }, "night": { "description": "Light Thunderstorms With Hail", "image": "http://openweathermap.org/img/wn/11n@2x.png" } },
  "99": { "day": { "description": "Thunderstorm With Hail", "image": "http://openweathermap.org/img/wn/11d@2x.png" }, "night": { "description": "Thunderstorm With Hail", "image": "http://openweathermap.org/img/wn/11n@2x.png" } }
};

export default function Home() {
  // définition des états
  const [dateType, setDateType] = useState("date");
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [apiResult, setApiResult] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const silenceTimeoutRef = useRef(null);

  const handleDataAvailable = (event) => {
    if (event.data.size > 0) {
      audioChunksRef.current.push(event.data);
    }
  };

  const handleStop = async () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
  
    // Envoi du fichier audio à l'API
    try {
      console.log("Sending audio to the server");
      const formData = new FormData();
      formData.append("file", audioBlob, "enregistrement.wav");
  
      const response = await fetch("http://127.0.0.1:8000/weather", {
        method: "POST",
        headers: {
          "Accept": "application/json",
        },
        body: formData,
      });
  
      console.log("Fetch request sent");
  
      if (!response.ok) {
        throw new Error("Error while sending audio to the server");
      }
  
      const result = await response.json();
      console.log("API response: ", result);
      setApiResult(result); // Stocker le résultat de l'API
    } catch (err) {
      console.error("Error while sending audio to the server:", err);
      setApiResult({ error: "Erreur interne du serveur" }); // Stocker l'erreur
    }
    // audio.onplay = () => {
    //   setIsPlaying(true);
    //   console.log("Audio is playing");
    // };
  
    // audio.onended = () => {
    //   setIsPlaying(false);
    //   console.log("Audio has ended, isPlaying set to false");
    // };
  
    // audio.play();
  };

  const startRecording = async () => {
    if (isPlaying) {
      setIsPlaying(false);
    }

    console.log("start recording");
    try {
      // création des configurations pour l'enregistrement audio
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = handleDataAvailable;
      mediaRecorderRef.current.onstop = handleStop;
      mediaRecorderRef.current.start();

      setIsRecording(true);
      audioChunksRef.current = [];

      // création de l'analyseur audio pour détecter le silence
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 2048;
      const bufferLength = analyserRef.current.fftSize;
      const dataArray = new Uint8Array(bufferLength);

      const detectSilence = () => {
        analyserRef.current.getByteTimeDomainData(dataArray);
        const isSilent = dataArray.every(value => value > 120 && value < 130);

        if (isSilent) {
          silenceTimeoutRef.current = setTimeout(() => {
            stopRecording();
          }, 6000);
        } else {
          clearTimeout(silenceTimeoutRef.current);
        }

        if (isRecording) {
          requestAnimationFrame(detectSilence);
        }
      };

      detectSilence();
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      console.log("recording stopped");
      setIsRecording(false);
      // on arrête le timeout de détection de silence
      clearTimeout(silenceTimeoutRef.current);

      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    }
  };

  useEffect(() => {
    // on arrête l'enregistrement si le composant est démonté
    return () => {
      if (isRecording) {
        stopRecording();
      }
    };
  }, [isRecording]);

  if (typeof window !== "undefined") {
    // expose les fonctions de l'enregistrement audio au global scope
    window.startRecording = startRecording;
    window.stopRecording = stopRecording;
  }

  const getWeatherDescription = (code) => {
    const weather = weatherCodes[code];
    if (!weather) return { description: "Unknown", image: "" };
    const isDay = new Date().getHours() >= 6 && new Date().getHours() < 18;
    return isDay ? weather.day : weather.night;
  };

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Vocal Weather</h1>
      {apiResult && (
        <div className={styles.result}>
          {apiResult.error ? (
            <p>{apiResult.error}</p>
          ) : (
            <>
              <div className="mx-auto p-2" style={{ width: "200px", textAlign: "center" }}>
                <h3><strong>{JSON.parse(apiResult.location.replace(/'/g, '"')).city}</strong></h3>
              </div>
                <div className="mx-auto row align-items-center justify-content-center">
                    <div className="col-md-auto">
                      <img src={getWeatherDescription(apiResult.current_weather.weather_code).image} alt="Weather Icon" className={`${styles.weatherIcon} img-fluid`} />
                    </div>
                    <div className="col-md-auto">
                      <p className="mb-0">Temperature: {apiResult.current_weather.temperature_2m.toFixed(2)}°C ({apiResult.current_weather.apparent_temperature.toFixed(2)}°C ress.)</p>
                      <p className="mb-0">{apiResult.current_weather.relative_humidity_2m.toFixed(2)}% humidity</p>
                      <p className="mb-0">Precipitation: {apiResult.current_weather.precipitation.toFixed(2)}mm (rain: {apiResult.current_weather.rain.toFixed(2)}mm)</p>
                    </div>
                    <div className="col-md-auto">
                      <p className="mb-0">{apiResult.current_weather.cloud_cover.toFixed(2)}% cloud cover</p>
                      <p className="mb-0">{apiResult.current_weather.wind_speed_10m.toFixed(2)} km/h wind speed</p>
                    </div>
                  </div>
                  <hr>
                  </hr>
                <div className="weatherForecast">
                  <div className="row">
                    {apiResult.weather_forecast.map((forecast, index) => (
                      <div key={index} className="mx-auto row align-items-center justify-content-center g-3">
                      <div className="col-12 col-md-auto text-center">
                        <p className="mb-0">
                          <strong>
                            {new Date(forecast.date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', })}
                          </strong>
                        </p>
                      </div>
                      <div className="col-12 col-md-auto text-center">
                        <img
                          src={getWeatherDescription(forecast.weather).image}
                          alt="Weather Icon"
                          className="img-fluid"
                          style={{maxWidth: '50px'}}
                        />
                      </div>
                      <div className="col-12 col-md-auto text-center">
                        <p className="mb-0">
                          Temperature: {forecast.temperature.toFixed(2)}°C ({forecast.apparent_temperature.toFixed(2)}°C ress.)
                        </p>
                        <p className="mb-0">Precipitation: {forecast.precipitation.toFixed(2)}mm</p>
                        <p className="mb-0">Rain: {forecast.rain.toFixed(2)}mm</p>
                      </div>
                      <div className="col-12 col-md-auto text-center">
                        <p className="mb-0">Cloud Cover: {forecast.cloud_cover.toFixed(2)}%</p>
                        <p className="mb-0">Wind Speed: {forecast.wind_speed.toFixed(2)} km/h</p>
                      </div>
                    </div>                    
                    ))}
                  </div>
                </div>
            </>
          )}
        </div>
      )}
      <main className={styles.main}>
        <div className={styles.dateInputs}>
          <label>
            Lieu:
            <input type="text" placeholder="Enter location" className="form-control" />
          </label>
          <label>
            Type de date:
            <select onChange={(e) => setDateType(e.target.value)} className="form-control">
              <option value="date">Single Date</option>
              <option value="daterange">Date Range</option>
            </select>
          </label>
          {dateType === "date" ? (
            <label>
              Date:
              <input type="date" className="form-control" />
            </label>
          ) : (
            <>
              <label>
                Date de début:
                <input type="date" className="form-control" />
              </label>
              <label>
                Date de fin:
                <input type="date" className="form-control" />
              </label>
            </>
          )}
        </div>
        <button className="btn btn-primary">Chercher</button>
        <button
          className={`${styles.micButton} ${isRecording ? styles.recording : ""}`}
          onClick={isRecording ? window.stopRecording : window.startRecording}
        >
          <TiMicrophoneOutline size={40} />
        </button>
      </main>
    </div>
  );
}
