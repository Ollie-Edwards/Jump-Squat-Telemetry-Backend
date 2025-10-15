#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebSocketsServer.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

#include <CircularBuffer.hpp>

Adafruit_MPU6050 mpu;

// Create WiFi network
const char *ssid = "ESP32_Accelerometer";
const char *password = "justJumpQuickly395";

// Setup UDP
WiFiUDP udp;
unsigned int localUdpPort = 4210; // UDP port
char incomingPacket[255];
char replyPacket[] = "Hello from ESP32 AP!";

// Sample structure
struct Sample {
  uint32_t timestamp_ms;
  float ax, ay, az, gx, gy, gz;
};

int counter = 0;

// Setup circular buffer
const int SAMPLE_RATE_HZ = 1000;
const int SEND_RATE_HZ = 100;
const int BUFFER_SIZE = 1024;  // Must be > (SAMPLE_RATE_HZ / SEND_RATE_HZ)
CircularBuffer<Sample, BUFFER_SIZE> sampleBuffer;

unsigned long lastSampleMicros = 0;
unsigned long lastSendMillis = 0;

int status = 0; // stores whether or not the device is sending
bool debug = false;

const int buzzerPin = 33;

void beep(int time) {
  digitalWrite(buzzerPin, HIGH);
  delay(time);
  digitalWrite(buzzerPin, LOW);
}

void handleIncomingPacket() {
  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    int len = udp.read(incomingPacket, 255);

    // Add string terminator
    if (len > 0)
      incomingPacket[len] = 0;

    if (debug){
      Serial.printf("Received from %s:%d\n",
        udp.remoteIP().toString().c_str(),
        udp.remotePort());
      Serial.printf("Message: %s\n", incomingPacket);
    }

    if (strcmp(incomingPacket, "Begin") == 0){
      beep(500);
      Serial.printf("Set status to 1");
      status = 1;
      counter = 0;
    }

    else if (strcmp(incomingPacket, "End") == 0){
      beep(500);
      Serial.printf("Set status to 0");
      status = 0;
      Serial.printf("send datapoints: %d\n", counter);

    }

    else if (strcmp(incomingPacket, "Ping") == 0){
      const char* reply = "Pong";
      udp.beginPacket(udp.remoteIP(), udp.remotePort());
      udp.write((const uint8_t*)reply, strlen(reply));
      udp.endPacket();
    }
  }
}

void sendMPUData(){
  const int samplesPerPacket = SAMPLE_RATE_HZ / SEND_RATE_HZ;
  Sample packet[samplesPerPacket];
  int count = 0;

  while (!sampleBuffer.isEmpty() && count < samplesPerPacket) {
    packet[count++] = sampleBuffer.shift();
  }

  if (count > 0) {
    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.write((uint8_t*)packet, count * sizeof(Sample));
    udp.endPacket();
  }
}


// read MPU6050 sample and buffer
void readMPUSensor() {
  sensors_event_t a, g, temp_event;
  mpu.getEvent(&a, &g, &temp_event);

  counter  = counter + 1;

  Sample s;
  s.timestamp_ms = millis();
  s.ax = a.acceleration.x;
  s.ay = a.acceleration.y;
  s.az = a.acceleration.z;
  s.gx = g.gyro.x;
  s.gy = g.gyro.y;
  s.gz = g.gyro.z;

  // Add to buffer
  if (!sampleBuffer.isFull()) {
    sampleBuffer.push(s);
  } else {
    sampleBuffer.shift();  // drop oldest
    sampleBuffer.push(s);
  }
} 

void setup() {
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(115200);

  Wire.begin(21, 22);
  Wire.setClock(1000000);

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found!");
    while (1) delay(10);
  }

  // Start ESP32 as an access point
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("Access Point started. IP address: ");
  Serial.println(myIP);

  // Start UDP
  udp.begin(localUdpPort);
  Serial.printf("Listening on UDP port %d\n", localUdpPort);

  beep(200);
  delay(50);
  beep(200);
  delay(50);
  beep(200);
}

void loop() {
  unsigned long nowMicros = micros();
  unsigned long nowMillis = millis();

  // If packet recieved, read it and potentially change mode
  handleIncomingPacket();

  if (nowMicros - lastSampleMicros >= 1000000UL / SAMPLE_RATE_HZ) {
    lastSampleMicros = nowMicros;
    readMPUSensor();
  }

  // Send data
  if (status == 1 && (nowMillis - lastSendMillis >= 1000/SEND_RATE_HZ)) {
    lastSendMillis = nowMillis;
    sendMPUData();
  }
}
