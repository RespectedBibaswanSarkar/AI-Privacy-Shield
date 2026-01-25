import cv2
import threading
import time

class CameraService:
    def __init__(self):
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            return
        # Use CAP_DSHOW for faster startup/capture on Windows
        # and set a reasonable resolution for performance
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Internal buffer to 1 to prevent lag
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def get_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
