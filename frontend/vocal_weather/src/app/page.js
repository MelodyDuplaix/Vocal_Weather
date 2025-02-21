"use client";

import Image from "next/image";
import styles from "./page.module.css";
import { TiMicrophoneOutline } from "react-icons/ti";
import { useState } from "react";

export default function Home() {
  const [dateType, setDateType] = useState("date");

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
        <button className={styles.searchButton}>Search</button>
        <button className={styles.micButton}>
          <TiMicrophoneOutline size={40} />
        </button>
      </main>
    </div>
  );
}
