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

  const handleStop = () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    audio.onplay = () => {
      setIsPlaying(true);
      console.log("Audio is playing");
    };

    audio.onended = () => {
      setIsPlaying(false);
      console.log("Audio has ended, isPlaying set to false");
    };

    audio.play();

    setTimeout(() => {
      if (isPlaying) {
        setIsPlaying(false);
        console.log("Audio timeout reached, isPlaying set to false");
      }
    }, audio.duration * 1000 + 1000);
  };

  const startRecording = async () => {
    if (isPlaying) {
      setIsPlaying(false);
    }

    console.log("start recording");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = handleDataAvailable;
      mediaRecorderRef.current.onstop = handleStop;
      mediaRecorderRef.current.start();

      setIsRecording(true);
      audioChunksRef.current = [];

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
          }, 4000);
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
        <label>
          Lieu:
          <input type="text" placeholder="Enter location" className={styles.input} />
        </label>
        <div className={styles.dateInputs}>
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