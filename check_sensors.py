
from HardwareMonitor.Util import OpenComputer

computer = None

try:
    computer = OpenComputer(cpu=True, gpu=True)
    computer.Update()

    def inspect(hardware):
        print(f"\nDEVICE: {hardware.Name}")

        for sensor in hardware.Sensors:
            value = sensor.Value
            sensor_type = str(sensor.SensorType)

            if "temperature" in sensor_type.lower():
                print(
                    f"  {sensor.Name} | "
                    f"Type: {sensor_type} | "
                    f"Value: {value}"
                )

        for child in hardware.SubHardware:
            inspect(child)

    for hardware in computer.Hardware:
        inspect(hardware)

finally:
    if computer is not None:
        computer.Close()
