# AI-Driven Thermal Monitoring & Anomaly Detection System

Python/OpenCV prototype for highlighting unusually bright regions in thermal-style images or video, raising threshold-based warnings, and logging candidate anomalies to CSV.

> **Important limitation:** Included examples are synthetic. This prototype detects image-intensity hotspots, not calibrated temperature. A standard RGB webcam does not measure thermal radiation. Real temperature alarms require compatible radiometric thermal hardware, its data interface, and calibration.

## Features
- Threshold-based hotspot candidate detection
- Morphological filtering and contour-based region extraction
- Bounding boxes and `WARNING` / `HIGH` labels
- Batch image-folder processing and optional video/webcam input
- Annotated output images and timestamped CSV event logs
- Synthetic data generator for repeatable testing

## Pipeline
1. Load a frame.
2. Convert to grayscale intensity.
3. Apply fixed/adaptive thresholding.
4. Clean the mask with morphological operations.
5. Extract candidate regions and calculate area/intensity features.
6. Annotate detections and append events to a CSV log.

## Project structure
```text
thermal-monitoring-anomaly-detection/
├── main.py
├── generate_demo.py
├── requirements.txt
├── README.md
├── LICENSE
├── sample_data/
└── outputs/
```

## Setup (Windows CMD)
```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run
```bat
python main.py --image sample_data\single_hotspot.png
python main.py --folder sample_data --no-display
python main.py --image sample_data\multiple_hotspots.png --threshold 220 --min-area 120
```

Regenerate sample data:
```bat
python generate_demo.py
```

Optional webcam (ordinary visible-light video, **not actual thermal data**):
```bat
python main.py --source 0
```
Press `q` to quit. A video file can be passed as `--source path\to\video.mp4`. For a compatible stream, pass its URL but do not commit credentials or private camera addresses.

## Outputs
- Annotated frames in `outputs/`
- Event log in `outputs/anomaly_log.csv`
- Features: timestamp, source, severity, bounding box, area, peak intensity and mean intensity

Intensity is 0–255 and **is not degrees Celsius**.

## Evaluation and next steps
This baseline is rule-based, not a trained deep-learning model. Evaluate with labeled normal/anomalous thermal frames and report precision, recall, false-alarm rate, and latency before making accuracy claims. Future improvements include radiometric camera input, calibrated application-specific limits, temporal alert debounce, and a learned anomaly detector.

## Safety
Treat detections as candidates requiring verification. Do not use this prototype alone for fire prevention, equipment protection, medical decisions, or other safety-critical monitoring.

## License
MIT. See `LICENSE`.
