from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import threading
import pandas as pd

import pandas as pd
import sqlite3
import pickle

from SensorController import SensorController
# from dataAnalysis import analyseDataframe

app = FastAPI()

conn = sqlite3.connect("jumpData.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS jumps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atleteId INTEGER NOT NULL,
        timestamp DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
        name TEXT NOT NULL,
        dataframe BLOB NOT NULL,
        duration REAL,
               
        takeoff_velocity REAL,
        jump_height REAL,
        flight_time_suvat REAL,
        flight_time_measured REAL,
        peak_net_accel REAL,
        avg_net_accel REAL,
        time_to_peak_force REAL,
        peak_grf REAL,
        avg_grf REAL,
        impulse REAL,
        avg_power REAL,
        peak_power REAL,
        peak_rfd REAL
    )
""")

conn.commit()
conn.close()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sensor = SensorController()
sensor.connect()

class StartRecordingRequest(BaseModel):
    duration: float
    name: str

@app.post("/sensor/begin")
def start_recording(req: StartRecordingRequest):
    
    recording = True

    thread = threading.Thread(target=sensor.beginRecording, args=(req.duration,))
    thread.start()
    thread.join()

    data = sensor.getSensorQueue()
    print(data.qsize(), " samples in ", req.duration," seconds")
    print(data.qsize()/req.duration,"Hz")

    data_list = []
    while not data.empty():
        data_list.append(data.get())

    # save to df
    df = pd.DataFrame(data_list, columns=["time", "ax", "ay", "az", "gx", "gy", "gz"])
    df["time"] = df["time"] - df.iloc[0]["time"]

    # save to database    
    conn = sqlite3.connect("jumpData.db")
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO jumps (
                    atleteId,
                    name,
                    dataframe,
                   duration
                   )
                   VALUES (?, ?, ?, ?)
                   """, (
                       1,
                       req.name,
                       pickle.dumps(df),
                       req.duration
                    )
    )
    conn.commit()
    conn.close()

    print(f"saved to database with name: {req.name}")

    return {"status": "success"}

@app.get("/data/{id}")
def get_data(id: int):

    # Fetch the pickled dataframe from DB
    conn = sqlite3.connect("jumpData.db")
    cursor = conn.cursor()
    cursor.execute("SELECT dataframe FROM jumps WHERE id = ?", (id,))
    stored_pickle = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    # Unpickle (deserialize) to DataFrame
    df = pickle.loads(stored_pickle)

    return df

@app.get("/graph/{name}")
def get_graph(name: str):

    return "results"

@app.get("/index")
def get_all():
    conn = sqlite3.connect("jumpData.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, atleteId, timestamp, name, duration FROM jumps ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    return {"results": rows}
