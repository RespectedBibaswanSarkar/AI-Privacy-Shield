from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import os
import time
from camera_service import CameraService
from face_detection import FaceDetector
from gaze_detection import GazeDetector
from face_recognition import FaceRecognizer
from risk_engine import RiskEngine

import threading
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
camera = CameraService()
detector = FaceDetector()
gaze_detector = GazeDetector()
recognizer = FaceRecognizer()
risk_engine = RiskEngine()

MODEL_PATH = "authorized_user.xml"
if os.path.exists(MODEL_PATH):
    recognizer.load_model(MODEL_PATH)

SYSTEM_STATUS = "IDLE" # IDLE, ENROLLING, MONITORING
LATEST_RISK_DATA = {"num_faces": 0, "risk": {"risk_level": "LOW", "score": 0, "reasons": []}}
LATEST_FRAME_B64 = ""

import cv2
import base64

def stream_loop():
    global LATEST_FRAME_B64, LATEST_RISK_DATA
    while True:
        frame = camera.get_frame()
        if frame is not None:
            # 1. Run AI Detections
            faces = detector.detect_faces(frame)
            crops = detector.get_face_crops(frame, faces)
            recognitions = [recognizer.identify(crop) for crop in crops]
            gazes = gaze_detector.process_frame(frame, faces)
            
            # 2. Update Risk Engine
            LATEST_RISK_DATA = risk_engine.analyze(len(faces), recognitions, gazes)
            risk_level = LATEST_RISK_DATA.get("risk_level", "LOW")

            # 3. DRAW TRACKING CIRCLES & LABELS
            display_frame = frame.copy()
            for i, face in enumerate(faces):
                x, y, w, h = face["bbox"]
                # LBPH Label 1 = Authorized, Confidence < 70 = Good match
                is_auth = (recognitions[i][0] == 1 and recognitions[i][1] < 70)
                color = (0, 255, 0) if is_auth else (0, 0, 255) # Green vs Red
                
                # Draw Box and Label
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
                gaze_label = "Looking" if gazes[i] else "Away"
                cv2.putText(display_frame, f"{'Auth' if is_auth else 'Unknown'} | {gaze_label}", 
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 4. BLUR IF RISK IS HIGH
            if risk_level == "HIGH":
                display_frame = cv2.GaussianBlur(display_frame, (99, 99), 0)

            # 5. Encode to Base64 for the Frontend
            _, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            LATEST_FRAME_B64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
        
        time.sleep(0.03) # Match camera FPS

def ai_loop():
    """Lower-frequency loop for heavy AI processing."""
    global LATEST_RISK_DATA
    while True:
        frame = camera.get_frame()
        if frame is not None:
            # Run detection on a copy to prevent locking contentions
            faces = detector.detect_faces(frame)
            num_faces = len(faces)
            
            recognitions = []
            crops = detector.get_face_crops(frame, faces)
            for crop in crops:
                label, conf = recognizer.identify(crop)
                recognitions.append((label, conf))
            
            gazes = gaze_detector.process_frame(frame, faces)
            while len(gazes) < len(recognitions):
                gazes.append(False)
            
            risk_data = risk_engine.analyze(num_faces, recognitions, gazes[:len(recognitions)])
            
            LATEST_RISK_DATA = {
                "num_faces": num_faces,
                "risk": risk_data
            }
        time.sleep(0.1) # 10 AI checks per second is plenty

@app.on_event("startup")
async def startup_event():
    camera.start()
    threading.Thread(target=stream_loop, daemon=True).start()
    threading.Thread(target=ai_loop, daemon=True).start()

@app.on_event("shutdown")
async def shutdown_event():
    camera.stop()

@app.get("/status")
def get_status():
    return {
        "status": SYSTEM_STATUS,
        "frame": LATEST_FRAME_B64,
        **LATEST_RISK_DATA
    }

@app.post("/enroll")
def start_enrollment():
    global SYSTEM_STATUS
    SYSTEM_STATUS = "ENROLLING"
    
    # Capture 10 faces (faster than 15)
    captured_faces = []
    start_time = time.time()
    
    while len(captured_faces) < 10 and (time.time() - start_time) < 15:
        frame = camera.get_frame()
        if frame is not None:
            faces = detector.detect_faces(frame)
            if len(faces) == 1:
                crops = detector.get_face_crops(frame, faces)
                if crops:
                    captured_faces.append(crops[0])
                    # No artificial delay here for speed
        time.sleep(0.05)
        
    if len(captured_faces) >= 10:
        recognizer.train(captured_faces)
        recognizer.save_model(MODEL_PATH)
        SYSTEM_STATUS = "MONITORING"
        return {"message": "Enrollment success"}
    else:
        SYSTEM_STATUS = "IDLE"
        return {"error": "Enrollment failed - could not capture enough clear face images"}

@app.post("/start-monitoring")
def start_monitoring():
    global SYSTEM_STATUS
    if recognizer.is_trained:
        SYSTEM_STATUS = "MONITORING"
        return {"message": "Monitoring started"}
    return {"error": "User not enrolled"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
