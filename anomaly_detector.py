
from collections import defaultdict, deque

# Number of recent readings used for baseline comparison
WINDOW_SIZE = 10

# Alert if the temperature rises this much above its baseline
SPIKE_THRESHOLD_C = 8.0

# Minimum historical readings required before spike detection
MIN_BASELINE_READINGS = 5

# Initial configurable thresholds for the NVIDIA laptop GPU
GPU_CORE_LIMIT_C = 85.0
GPU_HOTSPOT_LIMIT_C = 100.0
GPU_MEMORY_LIMIT_C = 95.0

# Store history separately for every device and sensor
_history = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))


def detect_anomaly(device, sensor, temperature_c):
    """
    Detect high temperatures and sudden temperature increases.

    Args:
        device: Hardware device name.
        sensor: Sensor name.
        temperature_c: Current temperature in Celsius.

    Returns:
        Dictionary containing status, alerts and baseline.
    """
    key = (device, sensor)
    sensor_name = sensor.lower()
    previous = list(_history[key])
    alerts = []

    # Fixed temperature threshold checks
    if "gpu core" in sensor_name:
        if temperature_c >= GPU_CORE_LIMIT_C:
            alerts.append("HIGH_GPU_CORE_TEMPERATURE")

    elif "gpu hot spot" in sensor_name:
        if temperature_c >= GPU_HOTSPOT_LIMIT_C:
            alerts.append("HIGH_GPU_HOTSPOT_TEMPERATURE")

    elif "gpu memory junction" in sensor_name:
        if temperature_c >= GPU_MEMORY_LIMIT_C:
            alerts.append("HIGH_GPU_MEMORY_TEMPERATURE")

    # Compare against the recent historical baseline
    baseline = None

    if len(previous) >= MIN_BASELINE_READINGS:
        baseline = sum(previous) / len(previous)

        if temperature_c - baseline >= SPIKE_THRESHOLD_C:
            alerts.append("SUDDEN_TEMPERATURE_SPIKE")

    # Save this reading after calculating the baseline
    _history[key].append(float(temperature_c))

    return {
        "status": "ANOMALY" if alerts else "NORMAL",
        "alerts": alerts,
        "baseline_c": round(baseline, 2) if baseline is not None else None,
    }


def reset_history():
    """Clear stored sensor history, useful for testing."""
    _history.clear()
