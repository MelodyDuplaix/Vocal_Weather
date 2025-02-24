"use client";

import { useState, useRef, useEffect } from "react";
import { TiMicrophoneOutline } from "react-icons/ti";
import styles from "./page.module.css";

export default function Home() {
  // définition des états
  const [dateType, setDateType] = useState("date");
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
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
      // TODO: Traiter le résultat ici
    } catch (err) {
      console.error("Error while sending audio to the server:", err);
    }
  
    audio.onplay = () => {
      setIsPlaying(true);
      console.log("Audio is playing");
    };
  
    audio.onended = () => {
      setIsPlaying(false);
      console.log("Audio has ended, isPlaying set to false");
    };
  
    audio.play();
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

  // expose les fonctions de l'enregistrement audio au global scope
  window.startRecording = startRecording;
  window.stopRecording = stopRecording;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Vocal Weather</h1>
      <main className={styles.main}>
        <div className={styles.dateInputs}>
        <label>
          Lieu:
          <input type="text" placeholder="Enter location" className={styles.input} />
        </label>
          <label>
            Type de date:
            <select onChange={(e) => setDateType(e.target.value)} className={styles.input}>
              <option value="date">Single Date</option>
              <option value="daterange">Date Range</option>
            </select>
          </label>
          {dateType === "date" ? (
            <label>
              Date:
              <input type="date" className={styles.input} />
            </label>
          ) : (
            <>
              <label>
                Date de début:
                <input type="date" className={styles.input} />
              </label>
              <label>
                Date de fin:
                <input type="date" className={styles.input} />
              </label>
            </>
          )}
        </div>
        <button className={styles.searchButton}>Chercher</button>
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