import cv2

class GazeDetector:
    def __init__(self):
        # Using Eye Cascade as a proxy for gaze detection in this setup
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def process_frame(self, image, faces=None):
        """
        Detects if eyes are present in the faces. 
        If eyes are detected, we assume the person is looking towards the screen.
        """
        if image is None: return []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gaze_data = []

        if faces is None or len(faces) == 0:
            # Fallback to whole frame if no faces provided
            eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 10, minSize=(30, 30))
            return [True] * len(eyes)

        for face in faces:
            x, y, w, h = face["bbox"]
            face_roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray, 1.1, 5)
            
            # Simple heuristic: if at least one eye is detected, gaze is 'screen-facing'
            gaze_data.append(len(eyes) > 0)
            
        return gaze_data
