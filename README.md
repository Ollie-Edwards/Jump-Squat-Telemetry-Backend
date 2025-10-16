# Jump-Squat-Telemetry

This project aims to **record, analyze, and display** accelerometer based sensor data to measure **athlete performance metrics** such as peak force, peak acceleration, rate of force development (RFD) and many other statistics. This data is usually only available using expensive force plates which can cost thousands of pounds, and are not accessible to the majority of athletes, this project seeks to make this technology and insight widely accessible at a low cost.

It provides a complete end-to-end IoT data acquisition and processing system built with ESP32, FastAPI, and SQLite, connected to a modern React.js and Typescript front end, to display data to the athlete/coaches.

## Note
1) This project is still a work in progress, and I am still working on cleaning up the code, writing tests and adding a large number of features when I have time alongside my studies.
2) This repo only includes code for the hardware and API layer of the project, for front end code please see link

# Project Architecture

<img width="902" height="546" alt="Untitled Diagram drawio (1)" src="https://github.com/user-attachments/assets/d0c71f60-a540-4ea3-a6f0-b5f089396f0e" />

# Hardware layer

The hardware unit is built around the ESP32 with the MPU6050 sensor, The MPU6050 combines a 3-axis accelerometer and 3-axis gyroscope with a 16-bit ADC, allowing for accurate motion tracking and force estimation. All of this is fitted inside a 3D printed enclosure and attached to a standard 50mm barbell sleeve. (this can be seen in the images below).

The hardware is powered by a 9v battery, stepped down using a buck converter to 3.3v, all the hardware including printed enclosure weighs just 90g in total. 

Data is transmitted on a closed network via the UDP protocol, the high frequency consumer loads accelerometer data into a circular queue at ~1000hz, and the low frequency consumer pops this data from the circular queue and sends it to the controller laptop at ~100hz via UDP.

|     |  |
| -------- | ------- |
| ![IMG_6790](https://github.com/user-attachments/assets/11599636-06c3-4c4a-9b0d-13ccc40465f0)  | ![IMG_6793](https://github.com/user-attachments/assets/87f0e1ad-aafe-4ff7-9266-9b840058762a)    |

# API and application layer

# Database layer

# Frontend

Aee code here: https://github.com/Ollie-Edwards/Jump-Squat-Telemetry-Frontend

# Future improvements / Features

