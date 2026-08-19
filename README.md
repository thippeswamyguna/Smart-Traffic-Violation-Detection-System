# 🛡️ SENTINEL: Smart Traffic Violation Detection System

An AI-powered, 3D particle-driven telemetry dashboard and intelligent traffic enforcement hub featuring real-time object detection (YOLOv8), license plate character extraction (EasyOCR), rule-based violation classification, and audit workflow management.

Designed and developed inside **Anti-Gravity IDE**.

---

## 🌟 Overview & Key Features

- **Interactive 3D Particle Telemetry**: Real-time canvas telemetry rendering simulated neural inference nodes, vehicle flow trajectories, and radar scanning rings.
- **YOLOv8 & EasyOCR AI Core**: Automatic detection of vehicles (`car`, `motorcycle`, `bus`, `truck`) and safety violations (`no_helmet`, `no_seatbelt`, `red_light`, `wrong_way`, `illegal_parking`) with EasyOCR license plate character extraction.
- **Glassmorphic Sci-Fi HUD UI**: Futuristic dark mode aesthetic (`#070A14`) with specular glass cards (`backdrop-filter: blur(20px)`), glowing neon accents, and smooth micro-animations.
- **Live CCTV & Intersection Simulator**: Real-time surveillance feed with dual-mode switcher (Physical WebCam or 2D Intersection Canvas Simulator with synth warning audio alerts).
- **Interactive Verification Scanner**: File dropzone supporting drag-and-drop uploads, target reticle HUD overlays, vehicle owner verification, and instant officer audit controls.
- **24-Hour Peak-Hour Heatmap & PDF Reporting**: Traffic compliance percentage ring meter, 24-hour violation density heatmap matrix (00:00 to 23:00), CSV log export, and printable PDF dialog formatting.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend UI** | HTML5, Vanilla CSS3 (Glassmorphism, CSS Grid/Flexbox), Vanilla ES6 JavaScript |
| **Visualizations** | Canvas 2D / WebGL Particle Telemetry, Chart.js Data Analytics, FontAwesome 6 |
| **Backend API** | Python 3.10+ Flask, Blueprints (`auth`, `violations`, `detect`), CORS |
| **Database & Auth** | SQLite, Flask-SQLAlchemy ORM, bcrypt Password Hashing, PyJWT Authentication |
| **Computer Vision** | OpenCV 4, Ultralytics YOLOv8, EasyOCR (with built-in CV feature fallback) |

---

## 📁 Repository File Structure

```
STVDS/
└── app/
    ├── app.py                  # Flask Application Entry Point & Web Router
    ├── config.py               # Environment Variables & Path Configuration
    ├── models.py               # SQLAlchemy Database Schemas (User, Vehicle, Violation)
    ├── seed.py                 # SQLite Table Initializer & Visual Seeder
    ├── batch.py                # Batch Dataset Processor Script
    ├── requirements.txt        # Python Dependency Manifest
    ├── yolov8n.pt              # YOLOv8 Computer Vision Weights
    ├── services/
    │   ├── detector.py         # YOLOv8 Detector with OpenCV Contour Fallback
    │   ├── ocr.py              # EasyOCR Plate Extractor with Binarization Preprocessing
    │   └── classifier.py       # Violation Rules & Vehicle Owner Database Matcher
    ├── routes/
    │   ├── auth.py             # JWT Login & Role Middleware (Admin, Officer, Viewer)
    │   ├── violations.py       # Metrics Aggregation, CRUD Audit Grid, CSV & Reports
    │   └── detect.py           # Image Upload & Live Stream Inference Endpoints
    ├── templates/
    │   ├── base.html           # Master Sentri OS Layout Wrapper & Dock Sidebar
    │   ├── index.html          # Biometric Login Portal with 1-Click Demo Accounts
    │   ├── dashboard.html      # Command Center Metrics & Chart.js Visualizations
    │   ├── upload.html         # Media Detector Scanner HUD & Verification Form
    │   ├── live.html           # CCTV Monitor with Canvas Intersection Simulator
    │   ├── violations.html     # Filterable Audit Grid with Pagination & CSV Export
    │   └── report.html         # 24-Hour Peak-Hour Heatmap & Printable PDF Report
    └── static/
        ├── css/
        │   └── style.css       # Complete Glassmorphic Dark Theme System
        └── js/
            ├── common.js       # Auth Guard, API Wrapper, Digital Clock, Toast Engine
            ├── dashboard.js    # Chart.js Loaders & Audit Review Modal
            ├── upload.js       # Dropzone Scanner & Interactive Form Submitter
            ├── live.js         # Video Stream, Canvas Simulator & Audio Beeper
            ├── violations.js   # Table Filter Manager & CSV Exporter
            └── report.js       # Heatmap Matrix Renderer & PDF Print Trigger
```

---

## 🚀 Quickstart / Local Setup

### 1. Clone & Prepare Virtual Environment
```bash
git clone https://github.com/your-username/SENTINEL-Traffic-AI.git
cd SENTINEL-Traffic-AI/app
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Run the seed script to create the SQLite database (`traffic.db`), initialize user credentials, register vehicles, and generate mock visual traffic snapshot images:
```bash
python seed.py
```

### 4. Launch Flask Server
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🔑 Pre-Seeded System Accounts

| Role | Username | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `adminpassword` | Full command access, audit verification, delete records, export logs |
| **Officer** | `officer` | `officerpassword` | Run scans, review pending incidents, update notes & fines |
| **Viewer** | `viewer` | `viewerpassword` | Read-only analytics, charts, and peak-hour report matrix |

---

## 🌐 Deployment Guide

### Vercel Deployment (`vercel.json`)
For serverless Flask deployment on Vercel:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### Netlify Deployment (`netlify.toml`)
For static frontend showcase hosting:
```toml
[build]
  publish = "static"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```
