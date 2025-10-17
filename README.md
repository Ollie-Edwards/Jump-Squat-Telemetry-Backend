# Jump Squat Telemetry

This project aims to **record, analyze, and display accelerometer-based sensor data** to measure athlete performance metrics such as **peak force**, **peak acceleration**, **rate of force development (RFD)**, and many other statistics. This kind of data is usually only available using **expensive force plates**, which can cost thousands of pounds and are not accessible to the majority of athletes. This project seeks to make this technology and insight **widely accessible at a low cost**.

It provides a complete end-to-end **IoT data acquisition and processing system**, including:
* **Data acquisition** using an **ESP32 microcontroller** paired with **accelerometer sensors**, capturing real-time movement data.
* **Data transmission and processing** through a **FastAPI backend**, storing and analyzing the information in a lightweight **SQLite database**.
* **Data visualization** with a **modern React.js and TypeScript frontend**, allowing athletes and coaches to view performance metrics, track improvements, and explore trends over time.
    
By combining affordable hardware, robust backend processing, and an intuitive frontend dashboard, this project brings elite-level performance measurement tools normally only available in sports science labs to any athlete, anywhere.


## Note
1) This project is still a work in progress, and I am still working on cleaning up the code, writing tests and adding a large number of features when I have time alongside my studies.
2) This repo only includes code for the hardware and API layer of the project, for front end code please see the following repo: https://github.com/Ollie-Edwards/Jump-Squat-Telemetry-Frontend

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

|     |  |
| -------- | ------- |
| <img width="1254" height="1284" alt="image" src="https://github.com/user-attachments/assets/905e940f-496a-4b75-85d4-64ed2306f4b1" /> | <img width="694" height="727" alt="image" src="https://github.com/user-attachments/assets/379009d2-f0f0-482c-af60-fcdd7fa86f09" />

 |

|     |  |
| -------- | ------- |
| <img width="1262" height="1303" alt="image" src="https://github.com/user-attachments/assets/ca2c3f3c-a9f8-42a2-9a3e-79d00059caab" />
  | <img width="1265" height="1301" alt="image" src="https://github.com/user-attachments/assets/7264c865-e0f6-4eb2-a2a6-154b7953bb2b" />
    |

See code here: https://github.com/Ollie-Edwards/Jump-Squat-Telemetry-Frontend

# Future improvements / Features

