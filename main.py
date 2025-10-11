from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import socket
import struct
import threading, queue
import time
import pandas as pd

import os
from dotenv import load_dotenv

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# LOAD API TOKEN
load_dotenv()
token = os.environ.get("INFLUXDB_TOKEN")

org = "Personal"
bucket = "PersonalBucket"
url = "http://localhost:8086"

# INITIALISE InfluxDB Client
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

app = FastAPI()

# Allow CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for sensor data
recording = False
UDP_IP = "192.168.4.1"
UDP_PORT = 4210

data_queue = queue.Queue()

def udp_listener(duration: float):
    global recording

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", UDP_PORT))
        print(f"Listening on UDP port {UDP_PORT}")
    except OSError as e:
        print(f"Failed to create or bind UDP socket: {e}")
        # Optionally, raise the exception or return an error if in API context
        raise e
    
    print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")
    
    start_time = time.time()
    buffer = []

    # Send start commands
    sock.sendto(b"0", (UDP_IP, UDP_PORT))
    sock.sendto(b"Begin", (UDP_IP, UDP_PORT))

    while (time.time() - start_time < duration):
        try:
            data, addr = sock.recvfrom(1024)
            line = struct.unpack("7f", data)
            buffer.append(line)

        except socket.timeout:
            print("Socket timed out")
            continue
    
    # Send end command
    sock.sendto(b"End", (UDP_IP, UDP_PORT))
    recording = False

    print("UDP recording ended.")

    # add to queue
    data_queue.put(buffer)

@app.post("/sensor/begin")
def start_recording():
    print("start RECORDING")
    global recording
    # if recording:
    #     return {"status": "already recording"}
    recording = True
    start_time_ms = int(time.time() * 1000)

    thread = threading.Thread(target=udp_listener, args=(3.0,))
    thread.start()
    thread.join()  # optional

    data = data_queue.get()

    arduinoStartTime = data[0][0]
    points = []
    for row in data:
        rel_time_ms, ax, ay, az, gx, gy, gz = row

        # Compute absolute timestamp in ms
        timestamp_ms = int((rel_time_ms - arduinoStartTime) + start_time_ms)

        # Create data point
        p = (
            Point("imu_data1")
            .field("ax", ax)
            .field("ay", ay)
            .field("az", az)
            .field("gx", gx)
            .field("gy", gy)
            .field("gz", gz)
            .time(timestamp_ms, WritePrecision.MS)
        )

        points.append(p)
    print(len(points))
    print(points)

    write_api.write(bucket=bucket, org=org, record=points)

    return {"status": "recording started"}
