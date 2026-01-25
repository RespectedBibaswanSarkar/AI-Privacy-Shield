import cv2
import numpy as np

class FaceRecognizer:
    def __init__(self):
        # Using a simple ORB or LBPH fallback if deep-learning embeddings fail
        # But let's try to use a more robust approach: OpenCV's FaceRecognizer
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.is_trained = False

    def train(self, face_images):
        """
        Trains the LBPH recognizer with a single user's images.
        Note: OpenCV LBPH needs labels. We use 1 for the authorized user.
        """
        if not face_images:
            return
            
        labels = np.ones(len(face_images), dtype=np.int32)
        gray_faces = [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) for img in face_images]
        # Resize all to same size
        gray_faces = [cv2.resize(img, (200, 200)) for img in gray_faces]
        
        self.recognizer.train(gray_faces, labels)
        self.is_trained = True
        
    def save_model(self, path):
        if self.is_trained:
            self.recognizer.save(path)
            
    def load_model(self, path):
        import os
        if os.path.exists(path):
            self.recognizer.read(path)
            self.is_trained = True

    def identify(self, face_image):
        """
        Returns (label, confidence). 
        Lower confidence value means better match for LBPH.
        """
        if not self.is_trained:
            return None, 100
            
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (200, 200))
        label, confidence = self.recognizer.predict(gray)
        
        # For LBPH, a 'good' match is usually < 50-70
        return label, confidence
