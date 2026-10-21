from pathlib import Path
import cv2, numpy as np
OUT = Path(__file__).resolve().parent / "sample_data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(23)
def make(name, spots):
    h,w=480,640
    a=np.tile(np.linspace(45,110,w,dtype=np.float32),(h,1))
    a += rng.normal(0,3,(h,w)).astype(np.float32)
    yy,xx=np.mgrid[0:h,0:w]
    for cx,cy,r,peak in spots:
        d=np.sqrt((xx-cx)**2+(yy-cy)**2)
        a += (peak-100)*np.clip(1-d/r,0,1)**1.6
    image=cv2.applyColorMap(np.clip(a,0,255).astype(np.uint8),cv2.COLORMAP_INFERNO)
    cv2.putText(image,"SYNTHETIC DEMO - NOT REAL TEMPERATURE",(12,h-16),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2)
    cv2.imwrite(str(OUT/name),image)
make("normal_scene.png",[])
make("single_hotspot.png",[(330,230,85,255)])
make("multiple_hotspots.png",[(210,180,70,255),(470,315,55,245)])
print("Demo images generated.")
