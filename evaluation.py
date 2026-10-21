
from anomaly_detector import detect_anomaly, reset_history


def run_evaluation():
    reset_history()

    # Each case: description, baseline readings, test reading, expected result
    cases = [
        {
            "name": "Stable temperature",
            "baseline": [45, 46, 45, 46, 45, 46],
            "test": 46,
            "expected": "NORMAL",
        },
        {
            "name": "Sudden temperature rise",
            "baseline": [45, 46, 45, 46, 45, 46],
            "test": 60,
            "expected": "ANOMALY",
        },
        {
            "name": "High GPU core temperature",
            "baseline": [70, 71, 70, 71, 70, 71],
            "test": 86,
            "expected": "ANOMALY",
        },
    ]

    passed = 0
    total = len(cases)

    print("\nTHERMAL ANOMALY DETECTOR EVALUATION")
    print("=" * 55)

    for case in cases:
        reset_history()
        device = "Evaluation GPU"
        sensor = "GPU Core"

        for value in case["baseline"]:
            detect_anomaly(device, sensor, value)

        result = detect_anomaly(
            device,
            sensor,
            case["test"],
        )

        actual = result["status"]
        success = actual == case["expected"]
        passed += int(success)

        print(f"\nTest: {case['name']}")
        print(f"Expected: {case['expected']}")
        print(f"Actual:   {actual}")
        print(f"Result:   {'PASS' if success else 'FAIL'}")

    accuracy = (passed / total) * 100

    print("\n" + "=" * 55)
    print(f"Tests passed: {passed}/{total}")
    print(f"Test-case pass rate: {accuracy:.1f}%")
    print(
        "Note: This is a small rule-based test suite, "
        "not a real-world model accuracy measurement."
    )


if __name__ == "__main__":
    run_evaluation()
