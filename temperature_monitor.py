
import csv
import os
import time
from datetime import datetime

from HardwareMonitor.Util import OpenComputer
from anomaly_detector import detect_anomaly

OUTPUT_DIR = "outputs"
LOG_FILE = os.path.join(OUTPUT_DIR, "temperature_log.csv")
POLL_INTERVAL_SECONDS = 2

os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_FIELDS = [
    "timestamp",
    "device",
    "sensor",
    "temperature_c",
    "baseline_c",
    "status",
    "alerts",
]


def collect_temperatures(computer):
    """Read available temperature sensors from hardware devices."""
    readings = []
    computer.Update()

    def inspect_hardware(hardware):
        device_name = str(hardware.Name)

        for sensor in hardware.Sensors:
            sensor_type = str(sensor.SensorType).lower()
            value = sensor.Value

            if "temperature" not in sensor_type or value is None:
                continue

            try:
                temperature = float(value)
            except (TypeError, ValueError):
                continue

            readings.append({
                "device": device_name,
                "sensor": str(sensor.Name),
                "temperature_c": round(temperature, 2),
            })

        for child in hardware.SubHardware:
            inspect_hardware(child)

    for hardware in computer.Hardware:
        inspect_hardware(hardware)

    return readings


def append_log(writer, file_handle, row):
    """Write one reading to the CSV log immediately."""
    writer.writerow(row)
    file_handle.flush()


def main():
    file_exists = (
        os.path.exists(LOG_FILE)
        and os.path.getsize(LOG_FILE) > 0
    )

    computer = None

    try:
        # Sensor access may require administrator privileges.
        computer = OpenComputer(cpu=True, gpu=True)

        with open(
            LOG_FILE,
            "a",
            newline="",
            encoding="utf-8",
        ) as file_handle:

            writer = csv.DictWriter(
                file_handle,
                fieldnames=CSV_FIELDS,
            )

            if not file_exists:
                writer.writeheader()

            print("=" * 65)
            print("AI-DRIVEN THERMAL MONITORING")
            print("Live CPU/GPU temperature anomaly detection")
            print(f"Polling interval: {POLL_INTERVAL_SECONDS} seconds")
            print(f"CSV log: {LOG_FILE}")
            print("Press Ctrl+C to stop.")
            print("=" * 65)

            while True:
                timestamp = datetime.now().astimezone().isoformat(
                    timespec="seconds"
                )

                readings = collect_temperatures(computer)

                if not readings:
                    print(
                        "No temperature sensors found. "
                        "Check permissions and sensor support."
                    )

                for reading in readings:
                    result = detect_anomaly(
                        reading["device"],
                        reading["sensor"],
                        reading["temperature_c"],
                    )

                    alerts = result["alerts"]
                    status = result["status"]
                    baseline = result["baseline_c"]

                    baseline_text = (
                        f"{baseline:.2f} °C"
                        if baseline is not None
                        else "collecting baseline"
                    )

                    print(
                        f'{reading["device"]} | '
                        f'{reading["sensor"]}: '
                        f'{reading["temperature_c"]:.2f} °C | '
                        f'{status} | baseline: {baseline_text}'
                    )

                    if alerts:
                        print("  ALERT:", ", ".join(alerts))

                    row = {
                        "timestamp": timestamp,
                        "device": reading["device"],
                        "sensor": reading["sensor"],
                        "temperature_c": reading["temperature_c"],
                        "baseline_c": (
                            baseline if baseline is not None else ""
                        ),
                        "status": status,
                        "alerts": ";".join(alerts),
                    }

                    append_log(writer, file_handle, row)

                print("-" * 65)
                time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")

    except Exception as error:
        print(f"\nMonitoring error: {error}")
        print(
            "Check the HardwareMonitor installation and permissions. "
            "Run CMD as administrator if required."
        )

    finally:
        if computer is not None:
            try:
                computer.Close()
            except Exception:
                pass

        print("Monitor closed.")


if __name__ == "__main__":
    main()
