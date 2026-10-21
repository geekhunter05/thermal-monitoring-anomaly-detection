import argparse, csv, time
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
LOG = OUT / "anomaly_log.csv"

def detect(frame, threshold=220, min_area=120):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    adaptive = int(min(250, max(threshold, float(gray.mean() + 2 * gray.std()))))
    _, mask = cv2.threshold(gray, adaptive, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotated = frame.copy() if frame.ndim == 3 else cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    found = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area: continue
        x, y, w, h = cv2.boundingRect(c)
        roi = gray[y:y+h, x:x+w]
        peak, mean = int(roi.max()), float(roi.mean())
        severity = "HIGH" if peak >= 245 or mean >= 235 else "WARNING"
        item = dict(severity=severity, x=x, y=y, width=w, height=h, area_px=int(area),
                    peak_intensity=peak, mean_intensity=round(mean, 2))
        found.append(item)
        color = (0, 0, 255) if severity == "HIGH" else (0, 165, 255)
        cv2.rectangle(annotated, (x,y), (x+w,y+h), color, 2)
        cv2.putText(annotated, f"{severity} | peak={peak}", (x,max(22,y-8)),
                    cv2.FONT_HERSHEY_SIMPLEX, .55, color, 2)
    label = f"ANOMALY CANDIDATES: {len(found)}" if found else "STATUS: NORMAL"
    cv2.putText(annotated, label, (12,28), cv2.FONT_HERSHEY_SIMPLEX, .7, (255,255,255), 2)
    return annotated, found

def log_results(source, items):
    OUT.mkdir(exist_ok=True)
    fields = ["timestamp","source","severity","x","y","width","height","area_px","peak_intensity","mean_intensity"]
    new = not LOG.exists()
    with LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if new: writer.writeheader()
        for item in items:
            writer.writerow({"timestamp":datetime.now().isoformat(timespec="seconds"),"source":source,**item})

def image_mode(path, threshold, min_area, display):
    path = Path(path)
    frame = cv2.imread(str(path))
    if frame is None: raise SystemExit(f"Could not read image: {path}")
    annotated, items = detect(frame, threshold, min_area)
    OUT.mkdir(exist_ok=True)
    dest = OUT / f"{path.stem}_analyzed.jpg"
    cv2.imwrite(str(dest), annotated)
    log_results(path.name, items)
    print(f"{path.name}: {len(items)} candidate region(s). Saved: {dest}")
    if display:
        cv2.imshow("Thermal Anomaly Detection (press any key to close)", annotated)
        cv2.waitKey(0); cv2.destroyAllWindows()

def stream_mode(source, threshold, min_area):
    src = int(source) if source.isdigit() else source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened(): raise SystemExit(f"Cannot open source: {source}")
    last_log = 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        annotated, items = detect(frame, threshold, min_area)
        if items and time.time() - last_log >= 1:
            log_results(str(source), items); last_log = time.time()
        cv2.imshow("Thermal Anomaly Detection (Q to quit)", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"): break
    cap.release(); cv2.destroyAllWindows()

def main():
    p = argparse.ArgumentParser(description="Thermal-style hotspot monitoring prototype")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--image")
    g.add_argument("--folder")
    g.add_argument("--source", help="Video file, webcam index (0), or camera stream URL")
    p.add_argument("--threshold", type=int, default=220)
    p.add_argument("--min-area", type=int, default=120)
    p.add_argument("--no-display", action="store_true")
    a = p.parse_args()
    if a.image: image_mode(a.image, a.threshold, a.min_area, not a.no_display)
    elif a.folder:
        folder = Path(a.folder)
        paths = sorted(x for x in folder.iterdir() if x.suffix.lower() in {".jpg",".jpeg",".png",".bmp",".tif",".tiff"})
        if not paths: raise SystemExit("No supported images found.")
        for path in paths: image_mode(path, a.threshold, a.min_area, not a.no_display)
    else: stream_mode(a.source, a.threshold, a.min_area)

if __name__ == "__main__": main()
