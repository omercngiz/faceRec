# faceRec
 Pattern Recognition / Face Recognition Project | OpenCV & Insigthface

# Face Recognition Project

A modular real-time face recognition system built with Python, OpenCV, and InsightFace. This application can recognize known individuals, display their demographic information, and allows you to register new users through a simple graphical interface.

-----------------------

## Features

- Real-time face detection and recognition using webcam
- Age and gender estimation
- Displays name, age, and gender below detected faces
- Modular code structure for clarity and maintenance
- GUI-based interface for adding new people to the database
- Customizable person information (Name, Age, Gender)
- Requires 9 facial images from different angles during registration

-----------------------

# Project Structure

faceRec/
│

├── main.py # Main launcher script

├── recognize.py # Handles AI and recognition logic

├── local_db.py # Loads and manages face database

├── gui.py # GUI components (real-time camera + add user screen)

├── face_db/ # Face data storage per person (images + info.json)

│ └── John_Doe/

│ ├── 1.png ... 9.png

│ └── info.json

└── assets/

└── pose_guide.png # (Optional) Pose guide shown during registration

-----------------------

# Requirements

# Python & Packages

- Python `3.10.0`
- Cython `3.1.1`
- InsightFace `0.7.1`
- NumPy `2.2.6`
- OpenCV-Python `4.11.0.86`
- pip `21.2.6` or newer

# System Requirements

- **Visual Studio Build Tools**
  - Essential components:
    - C++ build tools
    - Windows 10 SDK

> Make sure your environment has C++ compilers installed. Some Python packages (like InsightFace) require compilation of native modules.

-----------------------

# How to Run

1. **Create a virtual environment**:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py

-----------------------

🐞 Known Bugs & Notes

🐌 The app may run slow initially — loading models and GUI pages can take a few seconds.

🖼️ During first registration, face images might not be saved to face_db/. This can cause errors on recognition. After one successful registration, it works as expected.

🔁 Performance may vary based on system hardware. CPU-only usage can be slow.

