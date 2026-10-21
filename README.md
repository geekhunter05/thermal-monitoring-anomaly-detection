# AI-Driven Thermal Monitoring & Anomaly Detection System

A Python-based prototype combining hardware temperature monitoring, rule-based anomaly detection, and computer vision to identify unusual image-intensity regions.

## Features

- Real-time GPU temperature monitoring using HardwareMonitor.
- Threshold-based GPU temperature alerts.
- Sudden temperature spike detection using a rolling baseline.
- Webcam-based bright-region detection using OpenCV.
- CSV logging of hardware readings and detected events.
- Synthetic demo images and automated anomaly detector tests.
- Live monitoring dashboard combining webcam and hardware sensor data.

## Technology Stack

- **Language:** Python
- **Computer Vision:** OpenCV
- **Hardware Monitoring:** HardwareMonitor
- **Data Processing:** CSV, Python collections
- **Version Control:** Git and GitHub

## System Workflow

1. Read available hardware temperature sensors.
2. Compare sensor readings against configurable thresholds.
3. Track recent readings to detect sudden temperature spikes.
4. Capture webcam frames and identify unusually bright regions.
5. Display detection results and system status.
6. Record sensor readings and candidate events in CSV files.

## Project Structure

```text
thermal-monitoring-anomaly-detection/
├── main.py
├── integrated_monitor.py
├── temperature_monitor.py
├── anomaly_detector.py
├── evaluation.py
├── test_anomaly_detector.py
├── check_sensors.py
├── generate_demo.py
├── requirements.txt
├── sample_data/
└── outputs/
```

## Setup on Windows

Open CMD in the project directory and run:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If a hardware monitoring dependency is not installed by `requirements.txt`, install the required dependency specified by the project code.

## Run the Project

Run the hardware temperature monitor:

```bat
python temperature_monitor.py
```

Run the integrated webcam and hardware monitor:

```bat
python integrated_monitor.py
```

Run image-based detection:

```bat
python main.py --image sample_data\single_hotspot.png
```

Generate synthetic demo images:

```bat
python generate_demo.py
```

Run the anomaly detector test:

```bat
python test_anomaly_detector.py
```

Run the evaluation script:

```bat
python evaluation.py
```

Use `Ctrl+C` to stop terminal-based monitoring. Use `q` to quit the webcam window when supported.

## Anomaly Detection

The