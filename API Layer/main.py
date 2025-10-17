from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import threading
import pandas as pd

import pandas as pd
import sqlite3

from SensorController import SensorController
from databaseController import DatabaseController
from dataAnalysis import analyseDataframe

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseController()

sensor = SensorController()
sensor.connect()

class StartRecordingRequest(BaseModel):
    duration: float
    name: str

@app.post("/sensor/begin")
def start_recording(req: StartRecordingRequest):
    thread = threading.Thread(target=sensor.beginRecording, args=(req.duration,))
    thread.start()
    thread.join()

    data = sensor.getSensorQueue()

    # save to df
    df = pd.DataFrame(data, columns=["time", "ax", "ay", "az", "gx", "gy", "gz"])

    # save to database    
    db.saveJumpData(1, req.name, df, req.duration)

    print(f"saved to database with name: {req.name}")

    return {"status": "success"}

@app.get("/data/{id}")
def get_dataframe(id: int):
    df = db.getDataframe(id)

    return analyseDataframe(df)

@app.get("/index")
def get_all():
    conn = sqlite3.connect("jumpData.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, atleteId, timestamp, name, duration FROM jumps ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    results = [
        {
            "id": row[0],
            "athleteId": row[1],
            "date": row[2],
            "name": row[3],
            "duration": row[4]
        }
        for row in rows
    ]

    print(results)

    return results

@app.get("/ping")
def get_all():
    connected = sensor.pingSensor()

    return connected
