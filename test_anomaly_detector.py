
from anomaly_detector import detect_anomaly, reset_history

reset_history()

device = "Test GPU"
sensor = "GPU Core"

# Establish a stable baseline using simulated readings.
for temperature in [45, 46, 45, 46, 45, 46]:
    result = detect_anomaly(device, sensor, temperature)
    print(f"{temperature} C -> {result['status']}")

# Simulate a sudden rise; this does not affect your real hardware.
temperature = 60
result = detect_anomaly(device, sensor, temperature)

print(f"\nSimulated spike: {temperature} C")
print("Result:", result)

assert result["status"] == "ANOMALY", (
    "Expected the simulated temperature spike to be detected."
)

print("\nPASS: Simulated spike detected successfully.")
