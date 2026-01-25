# AI Privacy Shield for Screens

A hackathon demo for intruder detection and real-time screen privacy.

## Features
- **One-Time Enrollment**: Captures user face and trains a local model.
- **Background Monitoring**: Silent operation in the system tray.
- **Multi-Threat Detection**: 
    - Multiple people detected.
    - Unauthorized person looking at the screen.
- **Privacy Overlay**: Automatic full-screen blur when threats are detected.
- **Fully Local**: No data sent to the cloud.

## Setup Instructions

### Backend
1. Navigate to `/backend`.
2. Activate virtual environment: `.\venv\Scripts\activate`.
3. Start FastAPI server: `python main.py`.

### Frontend
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Start the Vite dev server: `npm run dev` (in one terminal).
4. Run Electron: `npm run electron` (in another terminal).

## How it Works
1. **Enrollment**: Capture 15 face samples. OpenCV trains an LBPH model locally.
2. **Monitoring**: FastAPI service processes camera feed using MediaPipe (detection) and OpenCV (recognition).
3. **Trigger**: If `Risk Engine` detects a threat, it notifies the Electron frontend.
4. **Action**: Electron displays a transparent, "always-on-top" blur overlay.
