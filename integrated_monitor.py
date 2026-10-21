
import argparse
import time
from datetime import datetime
from pathlib import Path

import cv2

from HardwareMonitor.Util import OpenComputer
from anomaly_detector import detect_anomaly

OUT = Path("outputs")
LOG = OUT / "integrated_anomaly_log.csv"

GPU_LIMITS = {
    "gpu core": 85.0,
    "gpu hot spot": 100.0,
    "gpu memory junction": 95.0,
}


def read_temperatures(computer):
    """Read available CPU/GPU temperature sensors."""
    computer.Update()
    readings = []

    def inspect(hardware):
        device = str(hardware.Name)

        for sensor in hardware.Sensors:
            if "temperature" not in str(sensor.SensorType).lower():
                continue

            value = sensor.Value
            if value is None:
                continue

            try:
                value = float(value)
            except (ValueError, TypeError):
                continue

            readings.append({
                "device": device,
                "sensor": str(sensor.Name),
                "temperature_c": round(value, 2),
            })

        for child in hardware.SubHardware:
            inspect(child)

    for hardware in computer.Hardware:
        inspect(hardware)

    return readings


def log_event(source, event_type, details):
    """Append a timestamped event to the integrated CSV log."""
    OUT.mkdir(parents=True, exist_ok=True)
    exists = LOG.exists() and LOG.stat().st_size > 0

    import csv

    with LOG.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["timestamp", "source", "event_type", "details"],
        )
        if not exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "source": source,
            "event_type": event_type,
            "details": details,
        })


def draw_temperature_panel(frame, readings, hardware_status):
    """Display real hardware readings on the webcam image."""
    panel = frame.copy()
    height, width = panel.shape[:2]

    # Dark overlay panel for readable text.
    overlay = panel.copy()
    cv2.rectangle(overlay, (8, 42), (min(width - 8, 540), min(height - 8, 250)),
                  (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, panel, 0.25, 0, panel)

    cv2.putText(
        panel, "HARDWARE TEMPERATURE MONITOR",
        (18, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
        (255, 255, 255), 2,
    )

    y = 92
    if not readings:
        cv2.putText(
            panel, "No temperature sensors available",
            (18, y), cv2.FONT_HERSHEY_SIMPLEX, 0.48,
            (0, 200, 255), 1,
        )
        y += 24
    else:
        for reading in readings[:5]:
            line = (
                f'{reading["sensor"]}: '
                f'{reading["temperature_c"]:.1f} C'
            )
            cv2.putText(
                panel, line, (18, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48,
                (255, 255, 255), 1,
            )
            y += 22

    cv2.putText(
        panel, f"Hardware status: {hardware_status}",
        (18, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.48,
        (0, 0, 255) if hardware_status == "ANOMALY" else (0, 255, 0),
        1,
    )

    cv2.putText(
        panel, "Webcam brightness is NOT thermal imaging",
        (12, height - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
        (255, 255, 255), 1,
    )

    return panel


def main():
    parser = argparse.ArgumentParser(
        description="Integrated webcam and hardware temperature monitor"
    )
    parser.add_argument("--source", default="0",
                        help="Webcam index, video path, or stream URL")
    parser.add_argument("--threshold", type=int, default=220)
    parser.add_argument("--min-area", type=int, default=120)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    capture = cv2.VideoCapture(source)

    if not capture.isOpened():
        raise SystemExit(f"Could not open webcam/video source: {args.source}")

    computer = None
    latest_readings = []
    latest_status = "UNKNOWN"
    last_sensor_poll = 0.0
    last_event_log = 0.0

    try:
        computer = OpenComputer(cpu=True, gpu=True)
        print("Integrated monitor started. Press Q to quit.")
        print(f"Integrated event log: {LOG}")

        while True:
            ok, frame = capture.read()
            if not ok:
                print("No more frames available.")
                break

            now = time.time()

            # Poll hardware less frequently than the video frame rate.
            if now - last_sensor_poll >= args.poll_seconds:
                last_sensor_poll = now

                try:
                    latest_readings = read_temperatures(computer)
                    statuses = []

                    for reading in latest_readings:
                        result = detect_anomaly(
                            reading["device"],
                            reading["sensor"],
                            reading["temperature_c"],
                        )

                        statuses.append(result["status"])

                        if result["alerts"]:
                            print(
                                f'ALERT: {reading["device"]} / '
                                f'{reading["sensor"]}: '
                                f'{reading["temperature_c"]:.1f} C — '
                                f'{", ".join(result["alerts"])}'
                            )
                            log_event(
                                reading["device"],
                                "HARDWARE_ANOMALY",
                                f'{reading["sensor"]}: '
                                f'{reading["temperature_c"]:.2f} C; '
                                f'{", ".join(result["alerts"])}',
                            )

                    latest_status = (
                        "ANOMALY" if "ANOMALY" in statuses else
                        "NORMAL" if latest_readings else "UNKNOWN"
                    )

                except Exception as error:
                    latest_status = "SENSOR ERROR"
                    print("Sensor read error:", error)

            # Basic visible-light brightness detection.
            # This does NOT measure real thermal radiation.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(
                gray, args.threshold, 255, cv2.THRESH_BINARY
            )
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            visual_count = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < args.min_area:
                    continue

                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 165, 255), 2)
                visual_count += 1

            cv2.putText(
                frame, f"Visual bright regions: {visual_count}",
                (12, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2,
            )

            frame = draw_temperature_panel(
                frame, latest_readings, latest_status
            )

            cv2.imshow("AI Thermal Monitoring Prototype", frame)

            # Log visual detections at most once per second.
            if visual_count and now - last_event_log >= 1:
                log_event(
                    str(args.source),
                    "VISUAL_BRIGHT_REGION",
                    f"{visual_count} bright region(s); "
                    "not a physical temperature measurement",
                )
                last_event_log = now

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except Exception as error:
        print("Could not initialize or run hardware monitoring:", error)
        print("If required, retry from an administrator CMD window.")

    finally:
        capture.release()
        cv2.destroyAllWindows()

        if computer is not None:
            try:
                computer.Close()
            except Exception:
                pass

        print("Integrated monitor stopped.")


if __name__ == "__main__":
    main()
