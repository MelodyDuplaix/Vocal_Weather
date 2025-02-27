"use client";

import { useState, useRef, useEffect } from "react";
import { TiMicrophoneOutline } from "react-icons/ti";
import { FaQuestionCircle } from "react-icons/fa";
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
  const [location, setLocation] = useState("");
  const [dates, setDates] = useState([]);
  const [background, setBackground] = useState("");
  const [isDay, setIsDay] = useState(true);

  useEffect(() => {
    const updateBackground = () => {
      const hours = new Date().getHours();

      if (hours >= 6 && hours < 18) {
        setBackground(
          "linear-gradient(191deg, rgba(131,163,220,1) 0%, rgba(131,163,220,0.38035724543723737) 43%, rgba(131,163,220,0) 82%)"
        );
        setIsDay(true);
      } else {
        setBackground(
          "linear-gradient(191deg, rgba(73,46,153,1) 0%, rgba(73,46,153,0.4363796544008228) 43%, rgba(73,46,153,0) 82%)"
        );
        setIsDay(false);
      }
    };

    updateBackground();
    const interval = setInterval(updateBackground, 60000); // Met à jour chaque minute

    return () => clearInterval(interval);
  }, []);

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
          }, 5000);
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

  const handleSearch = async () => {
    if (!location || dates.length === 0) return;

    try {
      const response = await fetch("http://127.0.0.1:8000/weather-from-entities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location: location, dates: dates.map(d => new Date(new Date(d).getTime() - new Date(d).getTimezoneOffset() * 60000).toISOString().replace("T", " ").slice(0, 19))}),
      });

      if (!response.ok) throw new Error("Erreur lors de la requête");

      const result = await response.json();
      setApiResult(result);
    } catch (err) {
      setApiResult({ error: "Erreur interne du serveur" });
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
    <div className={styles.page} style={{ background }}>
      <h1 className={styles.title}>Vocal Weather</h1>
      <div className={isDay ? styles.sun : styles.moon}></div>
      <main className={styles.main}>
      {apiResult && (
        <div className={styles.result}>
          {apiResult.error ? (
            <div className="alert alert-warning" role="alert">
              <FaQuestionCircle /> {apiResult.error}
            </div>          
          ) : (
            <>
              <div className="mx-auto p-2" style={{ textAlign: "center" }}>
                <h3>
                  <strong>{JSON.parse(apiResult.location.replace(/'/g, '"')).city}</strong>
                </h3>
              </div>
              <div className="weatherForecast">
                <div className="row">
                  {apiResult.weather_forecast.map((forecast, index) => (
                    <div key={index} className="col-12 d-flex flex-column align-items-center flex-md-row justify-content-evenly">
                      <div className="text-center">
                        <p className="mb-0">
                          <strong>
                            {forecast.cloud_cover
                              ? new Date(forecast.date).toLocaleDateString('fr-FR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                  timeZone: 'UTC',
                                })
                              : new Date(forecast.date).toLocaleDateString('fr-FR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                })}
                          </strong>
                        </p>
                      </div>
                      <div className="text-center">
                        <img
                          src={getWeatherDescription(forecast.weather).image}
                          alt="Weather Icon"
                          className="img-fluid"
                          style={{ maxWidth: '80px' }}
                        />
                      </div>
                      <div className="text-center">
                        {forecast.temperature ? (
                          <p className="mb-0">
                            Temp: {forecast.temperature.toFixed(2)}°C ({forecast.apparent_temperature.toFixed(2)}°C ress.)
                          </p>
                        ) : (
                          <p className="mb-0">
                            Temp: {((forecast.temperature_max + forecast.temperature_min) / 2).toFixed(2)}°C (
                            {((forecast.apparent_temperature_max + forecast.apparent_temperature_min) / 2).toFixed(2)}°C ress.)
                          </p>
                        )}
                        <p className="mb-0">Precipitation: {forecast.precipitation?.toFixed(2) ?? forecast.precipitation_sum.toFixed(2)}mm</p>
                        <p className="mb-0">Rain: {forecast.rain?.toFixed(2) ?? forecast.rain_sum.toFixed(2)}mm</p>
                      </div>
                        {forecast?.cloud_cover && (
                          <div className="text-center">
                            <p className="mb-0">Cloud Cover: {forecast?.cloud_cover?.toFixed(2)}%</p>
                            <p className="mb-0">Wind Speed: {forecast?.wind_speed?.toFixed(2)} km/h</p>
                          </div>
                        )}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}
        <button
          className={`${styles.micButton} ${isRecording ? styles.recording : ""}`}
          onClick={isRecording ? window.stopRecording : window.startRecording}
        >
          <TiMicrophoneOutline size={40} />
        </button>
        <div className="container">
          <div className="row g-2 align-items-center justify-content-center">
            <div className="col-12 col-md-auto">
              <label className="w-100">
                Lieu:
                <input
                  type="text"
                  placeholder="Entrer un lieu"
                  className="form-control"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </label>
            </div>
            <div className="col-12 col-md-auto">
              <label className="w-100">
                Type de date:
                <select onChange={(e) => setDateType(e.target.value)} className="form-control">
                  <option value="date">Single Date</option>
                  <option value="daterange">Date Range</option>
                </select>
              </label>
            </div>
            {dateType === "date" ? (
              <div className="col-12 col-md-auto">
                <label className="w-100">
                  Date:
                  <input
                    type="datetime-local"
                    className="form-control"
                    value={dates}
                    onChange={(e) => setDates([e.target.value])}
                  />
                </label>
              </div>
            ) : (
              <>
                <div className="col-12 col-md-auto">
                  <label className="w-100">
                    Date de début:
                    <input
                      type="date"
                      className="form-control"
                      value={dates[0] || ''}
                      onChange={(e) => setDates([e.target.value, dates[1]])}
                    />
                  </label>
                </div>
                <div className="col-12 col-md-auto">
                  <label className="w-100">
                    Date de fin:
                    <input
                      type="date"
                      className="form-control"
                      value={dates[1] || ''}
                      onChange={(e) => setDates([dates[0], e.target.value])}
                    />
                  </label>
                </div>
              </>
            )}
          </div>
        </div>
        <button className="btn btn-primary mt-0" onClick={handleSearch}>Chercher</button>
      </main>
    </div>
  );
  
}
