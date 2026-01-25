class RiskEngine:
    def __init__(self, confidence_threshold=70.0):
        self.confidence_threshold = confidence_threshold

    def analyze(self, num_faces, recognitions, gazes):
        """
        Logic Implementation:
        Trigger privacy mode if:
        - More than one face detected
        - Authorized face NOT found and someone is looking at the screen
        """
        risk_score = 0
        reasons = []

        # Rule 1: Multi-person detection
        if num_faces > 1:
            risk_score = 1.0
            reasons.append("Multiple people detected")

        # Rule 2: Non-authorized face looking at screen
        # recognitions: list of (label, confidence)
        # gazes: list of boolean (True if looking)
        authorized_person_looking = False
        unauthorized_person_looking = False

        for (label, conf), looking in zip(recognitions, gazes):
            if label == 1 and conf < self.confidence_threshold:
                if looking:
                    authorized_person_looking = True
            else:
                if looking:
                    unauthorized_person_looking = True
                    reasons.append("Unauthorized person looking at screen")

        if unauthorized_person_looking and risk_score < 1.0:
            risk_score = 1.0
            
        return {
            "risk_level": "HIGH" if risk_score >= 1.0 else "LOW",
            "score": risk_score,
            "reasons": reasons,
            "authorized_present": any(label == 1 and conf < self.confidence_threshold for label, conf in recognitions)
        }
