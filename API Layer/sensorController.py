import time
import socket
import queue
import struct

class SensorController():
    def __init__(self):
        self.UDP_IP = "192.168.4.1"
        self.UDP_PORT = 4210
        self.sensorData = []

        self.recording = False
        self.connected = False

        self.sock = None

    def connect(self):
        trials = 5
        counter = 0

        while counter < trials and self.connected == False:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind(("", self.UDP_PORT))
                
                if self.pingSensor():
                    self.connected = True
                    break
            
            except Exception as e:
                print(e)
                # self.sock = None
                self.connected = False
            
            counter += 1
            
        if self.connected:
            print(f"Connected to sensor at {self.UDP_IP}:{self.UDP_PORT}...")
            return True
        
        else:
            print(f"Failed to create or bind UDP socket:")
            return False
        
    def pingSensor(self):
        if self.recording: return True

        self.sock.settimeout(0.5)
        self.sock.sendto(b"Ping", (self.UDP_IP, self.UDP_PORT)) 
        print(f"Sending ping to {self.UDP_IP}:{self.UDP_PORT}")

        try:
            data, addr = self.sock.recvfrom(1024)
            self.connected = True
            return True
        
        except socket.timeout:
            print("No ping recieved")
            self.connected = False
            return False
        
        finally:
            # Restore default (blocking) behavior
            self.sock.settimeout(None)

    def getSensorQueue(self):
        data = self.sensorData
        self.sensorData = []
        return data

    def beginRecording(self, duration: float):
        if self.recording:
            print("already recording")
            return False

        if not self.pingSensor():
            print("Sensor is not connected")
            # Try to reconnect
            if not self.connect():
                return False
            
        start_time = time.time()
        self.recording = True
        
        print("UDP recording started")

        # Send start signal
        self.sock.sendto(b"Begin", (self.UDP_IP, self.UDP_PORT))

        while (time.time() - start_time < duration):
            try:
                data, addr = self.sock.recvfrom(1024)

                fmt = "<Iffffff"  # little-endian: uint32 + 6 floats
                sample_size = struct.calcsize(fmt)

                for i in range(0, len(data), sample_size):
                    chunk = data[i:i+sample_size]
                    if len(chunk) == sample_size:
                        line = struct.unpack(fmt, chunk)
                        self.sensorData.append(line)

            except socket.timeout:
                print("Socket timed out")
                self.connected = False
                continue
        
        # Send end command
        self.sock.sendto(b"End", (self.UDP_IP, self.UDP_PORT))
        self.recording = False

        print("UDP recording ended.")

        return True
