#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebSocketsServer.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

// Create WiFi network
const char *ssid = "ESP32_Accelerometer";
const char *password = "justJumpQuickly395";

// Setup UDP
WiFiUDP udp;
unsigned int localUdpPort = 4210; // UDP port
char incomingPacket[255];
char replyPacket[] = "Hello from ESP32 AP!";

int sendDelay = 100;
int status = 0;
int counter = 0;
bool debug = false;

const int buzzerPin = 33;

void beep(int time)
{
  digitalWrite(buzzerPin, HIGH);
  delay(time);
  digitalWrite(buzzerPin, LOW);
}

void setup()
{
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(115200);

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
}

void loop()
{
  counter ++;
  // If packet recieved, read it and potentially change mode
  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    int len = udp.read(incomingPacket, 255);
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
    }

    else if (strcmp(incomingPacket, "End") == 0){
      beep(500);
      Serial.printf("Set status to 0");
      status = 0;
    }

    else{
      Serial.printf("Set send delay");
      sendDelay = atoi(incomingPacket);
    }
  }

  if (status == 1){
    // Send accelerometer data
    Serial.println("send");

    float data[7];
    getAccelData(data);

    udp.beginPacket(udp.remoteIP(), udp.remotePort());
    udp.write((uint8_t*)data, 7 * sizeof(float));  // send as raw bytes
    udp.endPacket();

    if (counter % 10 == 0){
      beep(1);
    }

    delay(sendDelay);
  }

  if (status == 0){
    delay(10);
  }
}

void getAccelData(float* data) {
  sensors_event_t a, g, temp_event;
  mpu.getEvent(&a, &g, &temp_event);

  data[0] = millis();

  data[1] = a.acceleration.x;
  data[2] = a.acceleration.y;
  data[3] = a.acceleration.z;

  data[4] = g.gyro.x;
  data[5] = g.gyro.y;
  data[6] = g.gyro.z;

  data[7] = temp_event.temperature;
} 
