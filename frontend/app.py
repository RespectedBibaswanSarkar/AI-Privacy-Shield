import streamlit as st
import cv2
import numpy as np
import time
import os
from datetime import datetime
import sys

# Direct imports from your existing backend logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from camera_service import CameraService
from face_detection import FaceDetector
from face_recognition import FaceRecognizer
from gaze_detection import GazeDetector
from risk_engine import RiskEngine
from privacy_shield import PrivacyShield

# --- UI SETTINGS & THEMING ---
st.set_page_config(page_title="Synapse AI Shield", layout="wide", initial_sidebar_state="collapsed")

# Injecting Custom CSS for the "Blackout", Cyberpunk HUD, and Landing Page
st.markdown("""
    <style>
    /* Global Styles & Reset */
    .stApp {
        background: radial-gradient(circle at center, #1a1f35 0%, #050511 100%);
        font-family: 'Inter', sans-serif;
        color: white;
    }
    
    /* Hide ALL Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stStatusWidget"] {visibility: hidden;} /* Wheelchair/Running Man */
    .stDeployButton {display:none;}
    
    /* Custom Button Styling - Cupertino/Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 15px; /* Slightly larger radius */
        padding: 20px 45px; /* Bigger button */
        font-size: 1.2rem; /* Larger text */
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        display: block;
        margin: 0 auto !important; /* Force center */
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.6);
    }

    /* Landing Page Specifics */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 50vh; /* Reduced height to pull content up slightly */
        text-align: center;
    }
    .hero-title {
        font-size: 6rem; /* Bigger Title */
        font-weight: 900;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 25px;
        text-shadow: 0 0 40px rgba(0, 242, 254, 0.4);
    }
    .hero-subtitle {
        font-size: 1.8rem; /* Bigger Subtitle */
        color: #b0b5c0;
        margin-bottom: 50px;
        font-weight: 400;
    }

    /* Cards Grid */
    .card-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 30px; /* Bigger Gap */
        padding: 40px 8%; /* More breathing room */
    }
    .feature-card {
        background: linear-gradient(145deg, #101522 0%, #0a0e17 100%);
        border-radius: 25px; /* Rounder */
        padding: 40px; /* MUCH BIGGER PADDING */
        color: white;
        border: 1px solid #2a3548;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
        min-height: 220px; /* Taller cards */
    }
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0, 242, 254, 0.15);
        border-color: #00f2fe;
    }
    .card-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 8px 15px; /* Bigger badge */
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-title {
        font-size: 1.6rem; /* Bigger Title */
        font-weight: 800;
        margin-bottom: 15px;
        color: white;
        margin-top: 10px;
    }
    .card-text {
        font-size: 1.1rem; /* Bigger Body */
        color: #b0b5c0;
        margin-bottom: 25px;
        line-height: 1.5;
    }
    .card-bullet {
        font-size: 0.95rem;
        color: #4facfe;
        font-weight: 500;
    }

    /* Badges Colors */
    .badge-blue { background-color: rgba(79, 172, 254, 0.2); color: #4facfe; }
    .badge-pink { background-color: rgba(255, 0, 128, 0.2); color: #ff0080; }
    .badge-purple { background-color: rgba(138, 43, 226, 0.2); color: #8a2be2; }
    .badge-teal { background-color: rgba(0, 255, 195, 0.2); color: #00ffc3; }
    .badge-orange { background-color: rgba(255, 165, 0, 0.2); color: #ffa500; }

    /* App Screen Styling */
    .app-header {
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
    }
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    /* Video Feed Container */
    img {
        border-radius: 15px;
        border: 2px solid #00f2fe; /* Cyan Border */
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetricLabel"] {
        color: #888;
        font-size: 0.8rem;
    }
    div[data-testid="stMetricValue"] {
        color: #fff;
        font-size: 1.5rem;
    }
    
    /* Privacy Overlay */
    .blackout-overlay {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #000; z-index: 999999; display: flex;
        align-items: center; justify-content: center; color: #ff3131;
        font-family: 'Courier New', Courier, monospace; flex-direction: column; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SERVICE INITIALIZATION (Singleton) ---
@st.cache_resource
def load_services():
    services = {
        "camera": CameraService(),
        "detector": FaceDetector(),
        "recognizer": FaceRecognizer(),
        "gaze": GazeDetector(),
        "risk": RiskEngine(),
        "shield": PrivacyShield()
    }
    try:
        services["camera"].start()
        services["shield"].start()
    except:
        pass
    
    if os.path.exists("authorized_user.xml"):
        services["recognizer"].load_model("authorized_user.xml")
    return services

def landing_page():
    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">AI Privacy Shield</h1>
            <p class="hero-subtitle">Visual Privacy Protection for the Real World</p>
            <p class="hero-credit">By – NON_NULL_POINTERS</p>
        </div>
    """, unsafe_allow_html=True)

    # Call to Action Button - Centered and Styled
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("LIVE DEMO - START ENROLLMENT"):
            st.session_state.page = "APP"
            st.session_state.enrolling = True
            st.rerun()

    st.markdown("<p style='text-align: center; color: #666; margin-top: 10px; font-size: 0.9rem;'>System Idle</p>", unsafe_allow_html=True)

    # Feature Cards Grid - Exact Match to Image
    st.markdown("""
<div class="card-grid">
    <div class="feature-card">
        <span class="card-badge badge-pink">BANK USER</span>
        <div class="card-title">Online Banking Safety</div>
        <div class="card-text">Protects credentials in public spaces.</div>
        <div class="card-bullet">• Instant Transaction Blur</div>
    </div>
    <div class="feature-card">
        <span class="card-badge badge-purple">EXAM AUTHORITY</span>
        <div class="card-title">Anti-Cheating Control</div>
        <div class="card-text">Detects gaze deviation during exams.</div>
        <div class="card-bullet">• Gaze Deviation Alerts</div>
    </div>
    <div class="feature-card">
        <span class="card-badge badge-teal">CORPORATE EMPLOYEE</span>
        <div class="card-title">Confidential Business Intel</div>
        <div class="card-text">Protects internal documents & emails.</div>
        <div class="card-bullet">• Strategic Content Frosting</div>
    </div>
    <div class="feature-card">
        <span class="card-badge badge-blue">HEALTHCARE</span>
        <div class="card-title">Patient Data Protection</div>
        <div class="card-text">Masks EHR data in real time.</div>
        <div class="card-bullet">• Dynamic PII Masking</div>
    </div>
    <div class="feature-card">
        <span class="card-badge badge-orange">REMOTE WORKER</span>
        <div class="card-title">Remote Work Security</div>
        <div class="card-text">Auto shields screen in coffee shops.</div>
        <div class="card-bullet">• Public Space Blackout</div>
    </div>
    <div class="feature-card">
        <span class="card-badge badge-blue">GENERAL USER</span>
        <div class="card-title">Personal Privacy</div>
        <div class="card-text">Protects personal chats and media.</div>
        <div class="card-bullet">• Smart Shoulder-Surfing Defense</div>
    </div>
</div>
    """, unsafe_allow_html=True)

def main_app(services):
    # --- HEADER ---
    st.markdown("""
        <div class="app-header">
            <div class="app-title">Privacy Shield Active</div>
        </div>
    """, unsafe_allow_html=True)

    # --- MAIN UI ---
    col_vid, col_panel = st.columns([3, 1])
    
    with col_vid:
        video_feed = st.empty()
        
    with col_panel:
        # Minimal Controls in Panel instead of Sidebar
        st.markdown("### Controls")
        
        # Cupertino-style Toggles and Buttons
        st.session_state.shield_on = st.toggle("Privacy Shield", value=st.session_state.shield_on)
        
        if st.button("Re-Enroll Identity"):
            st.session_state.enrolling = True
            st.rerun()
            
        st.markdown("---")
        st.markdown("### Status")
        risk_m = st.empty()
        face_m = st.empty()
        gaze_m = st.empty()
        fps_m = st.empty()
        log_box = st.empty()
        
        if st.button("Exit Demo"):
            st.session_state.page = "LANDING"
            st.rerun()

    blackout_overlay = st.empty()

    # --- MAIN PROCESSING LOOP ---
    prev_time = 0
    
    while True:
        # Check navigation state
        if st.session_state.page != "APP":
            break

        # 1. Fetch raw frame from CameraService
        frame = services["camera"].get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        # 2. AI Logic (Direct Function Calls)
        faces = services["detector"].detect_faces(frame)
        crops = services["detector"].get_face_crops(frame, faces)
        recognitions = [services["recognizer"].identify(crop) for crop in crops]
        gazes = services["gaze"].process_frame(frame, faces)
        
        risk_data = services["risk"].analyze(len(faces), recognitions, gazes)
        risk_level = risk_data.get("risk_level", "LOW")

        # 3. Visual Overlays (Circles & Labels)
        display_img = frame.copy()
        
        # Draw Borders on Video Feed logic happens in CSS, but we need high quality image here
        
        for i, face in enumerate(faces):
            x, y, w, h = face["bbox"]
            is_auth = (recognitions[i][0] == 1 and recognitions[i][1] < 70)
            color = (195, 255, 0) if is_auth else (0, 0, 255) # Cyan vs Red (BGR)
            
            # Draw HUD elements - minimalist
            cv2.rectangle(display_img, (x, y), (x+w, y+h), color, 2)
            
            # Minimal Status Label
            label = "AUTH" if is_auth else "UNKNOWN"
            
            # Gaze indicator
            gaze_status = "FOCUS" if gazes[i] else "AWAY"
            
            cv2.putText(display_img, f"{label} | {gaze_status}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 4. Privacy Shield Activation
        if st.session_state.shield_on and risk_level == "HIGH":
            services["shield"].activate()
            # Blur video feed
            display_img = cv2.GaussianBlur(display_img, (99, 99), 0)
            # Full Screen Blackout HTML
            blackout_overlay.markdown("""
                <div class="blackout-overlay">
                    <h1 style='font-size: 70px;'>REDACTED</h1>
                    <p>UNAUTHORIZED VIEW DETECTED</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            services["shield"].deactivate()
            blackout_overlay.empty()

        # 5. Display Video with Border Container
        # We wrap the image in the styled container via st.markdown if we could, 
        # but st.image is easier. We already added .video-container style globally.
        # But st.image creates its own img tag. We can't wrap it easily. behavior:
        # We will just rely on the feed being good.
        
        video_feed.image(display_img, channels="BGR", use_container_width=True)
        
        # Metrics
        face_m.metric("People", len(faces))
        risk_m.metric("Security", "Secured" if risk_level == "LOW" else "Breach", 
                      delta_color="normal" if risk_level == "LOW" else "inverse")
        gaze_m.metric("Attention", "Focused" if any(gazes) else "Distracted")
        
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time
        fps_m.caption(f"Latency: {1000/fps:.0f}ms ({fps:.1f} FPS)")

        # Handle Enrollment logic inside the loop
        if st.session_state.enrolling:
            perform_enrollment(services, video_feed, log_box)
            st.session_state.enrolling = False
            st.rerun()

        time.sleep(0.02)

def perform_enrollment(services, vid_spot, log_spot):
    log_spot.info("📸 Positioning for Enrollment...")
    time.sleep(1)
    
    samples = []
    max_samples = 15
    
    while len(samples) < max_samples:
        frame = services["camera"].get_frame()
        if frame is not None:
            faces = services["detector"].detect_faces(frame)
            if len(faces) == 1:
                crops = services["detector"].get_face_crops(frame, faces)
                samples.append(crops[0])
                
                # Visual Feedback
                h, w, c = frame.shape
                cv2.circle(frame, (w//2, h//2), 100, (0, 255, 0), 2)
                cv2.putText(frame, f"{len(samples)}/{max_samples}", (w//2 - 20, h//2 + 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                vid_spot.image(frame, channels="BGR", caption="Scaning Biometrics...")
            else:
                vid_spot.image(frame, channels="BGR", caption="Ensure only YOUR face is visible")
        
        time.sleep(0.1)
    
    log_spot.success("Processing Biometric Template...")
    services["recognizer"].train(samples)
    services["recognizer"].save_model("authorized_user.xml")
    log_spot.success("Enrollment Complete! You are now the authorized user.")
    time.sleep(2)

def main():
    # Initialize Session State
    if 'page' not in st.session_state:
        st.session_state.page = "LANDING"
    if 'shield_on' not in st.session_state:
        st.session_state.shield_on = False
    if 'enrolling' not in st.session_state:
        st.session_state.enrolling = False
        
    services = load_services()
    
    if st.session_state.page == "LANDING":
        landing_page()
    elif st.session_state.page == "APP":
        main_app(services)

if __name__ == "__main__":
    main()