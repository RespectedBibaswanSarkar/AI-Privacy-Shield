import cv2

class FaceDetector:
    def __init__(self):
        # Using Haar Cascades for maximum compatibility across Python versions
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_faces(self, image):
        if image is None: return []
        # Less aggressive downscale for better recognition
        height, width = image.shape[:2]
        new_width = 500
        scale = new_width / width
        small_img = cv2.resize(image, (new_width, int(height * scale)))
        
        gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
        # Lower minNeighbors (4) for higher sensitivity (detects faces easier)
        faces_detected = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        faces = []
        for (x, y, w, h) in faces_detected:
            # Scale coordinates back
            faces.append({
                "bbox": (int(x/scale), int(y/scale), int(w/scale), int(h/scale)),
                "score": 1.0
            })
        return faces

    def get_face_crops(self, image, faces):
        crops = []
        for face in faces:
            x, y, w, h = face["bbox"]
            crop = image[y:y+h, x:x+w]
            if crop.size > 0:
                crops.append(crop)
        return crops
