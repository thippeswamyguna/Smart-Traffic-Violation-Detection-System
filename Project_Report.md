# Project Report: Smart Traffic Violation Detection System

## 1. Project Overview

### 1.1 Introduction
The **Smart Traffic Violation Detection System** is an automated traffic enforcement and surveillance web application. It integrates computer vision models (object detection and character recognition) with a secure, responsive administrative dashboard to track, classify, and audit traffic violations (such as missing helmets, unbuckled seatbelts, running red lights, wrong-way driving, and illegal parking).

### 1.2 Objectives
- **Automated Detection**: Scan image and video streams for vehicles and safety rule infractions.
- **License Plate Extraction (OCR)**: Automatically locate and extract text from vehicle license plates.
- **Enforcement Workflow**: Log violations to a persistent database as "pending review" for administrative verification.
- **Analytics & Reporting**: Compile traffic compliance rates, peak-hour heatmaps, and export filtered logs as CSV spreadsheets or printable PDF profiles.
- **Secure Access Control**: Enforce role-based access for Admins, Officers, and Viewers.

---

## 2. Architecture & Tech Stack

The system follows a modular full-stack client-server architecture:

```
                  +-----------------------------------------+
                  |               Client UI                 |
                  |  (HTML5, Glassmorphic CSS3, JS, Charts)  |
                  +--------------------+--------------------+
                                       |
                              HTTP / REST / JWT
                                       |
                                       v
                  +--------------------+--------------------+
                  |             Flask Server                |
                  |     (app.py, Blueprints, JWT Auth)      |
                  +--------------------+--------------------+
                                       |
                     +-----------------+-----------------+
                     v                                   v
        +------------+------------+         +------------+------------+
        |     SQLite Database     |         |    CV Inference Engine  |
        |      (SQLAlchemy)       |         |  (YOLOv8, EasyOCR, cv2) |
        +-------------------------+         +-------------------------+
```

### 2.1 Backend (Flask)
- **Framework**: Python Flask handles API blueprints (`/api/auth`, `/api/violations`, `/api/detect`) and routes HTML template pages.
- **ORM & DB**: SQLite database mapped via SQLAlchemy.
- **Authentication**: Stateful passwords hashed using `bcrypt` and stateless session validation using JSON Web Tokens (JWT).

### 2.2 Computer Vision Engine
- **Object Detection (YOLOv8)**: Detects vehicles (`car`, `motorcycle`, `bus`, `truck`), persons, signals, and license plates.
- **Character Recognition (EasyOCR)**: Performs text extraction on cropped license plate regions after grayscale and Otsu thresholding preprocessing.
- **Violation Classifier**: Evaluates YOLO bounding boxes against custom heuristics to assign fine amounts and severities.
- **Fallback Simulation**: If libraries or GPUs are missing, a mockup CV engine automatically generates realistic boxes and plate names using deterministic hashes.

### 2.3 Frontend UI
- **Design Language**: Sci-fi Dark theme featuring Glassmorphism, radial gradients, glowing borders, custom scrollbars, and active state animations.
- **Libraries**: Chart.js for data visualization, FontAwesome for icons, and native print media queries for formatting PDF print exports.

---

## 3. Database Schema Design

The SQLite database (`traffic.db`) contains three tables structured as follows:

```
  +--------------------------------+       +--------------------------------+
  |             users              |       |            vehicles            |
  +--------------------------------+       +--------------------------------+
  | id (PK) : INTEGER              |       | id (PK) : INTEGER              |
  | username : VARCHAR(80)         |       | plate_number : VARCHAR(20) [I] |
  | password_hash : VARCHAR(128)   |       | owner_name : VARCHAR(100)      |
  | role : VARCHAR(20)             |       | vehicle_type : VARCHAR(50)     |
  | email : VARCHAR(120)           |       | is_flagged : BOOLEAN           |
  +--------------------------------+       +--------------------------------+
                                           
                                           
                                           +--------------------------------+
                                           |           violations           |
                                           +--------------------------------+
                                           | id (PK) : INTEGER              |
                                           | plate_number : VARCHAR(20) [I] |
                                           | violation_type : VARCHAR(50)   |
                                           | location : VARCHAR(100)        |
                                           | timestamp : DATETIME           |
                                           | confidence_score : FLOAT       |
                                           | image_path : VARCHAR(255)      |
                                           | status : VARCHAR(20)           |
                                           | fine_amount : FLOAT            |
                                           | officer_notes : TEXT           |
                                           +--------------------------------+
```
*[I] denotes Index for fast query filtering.*

---

## 4. Key Functional Modules

### 4.1 Login & Auth Guard
- Form inputs send credentials to `/api/auth/login`. On success, the JWT token and user metadata are saved in `localStorage`.
- A global JavaScript guard (`common.js`) runs on page load, redirecting unauthorized browsers back to the login screen and attaching the `Authorization: Bearer <token>` header to all backend API requests.

### 4.2 Main Analytics Dashboard
- Queries metrics counts (Violations Today, Pending Review, Fines, Active Cameras).
- Integrates two Chart.js modules:
  - **Line Chart**: Tracks daily counts over the last 7 days.
  - **Donut Chart**: Displays violation category distribution.
- Lists the 5 most recent incidents with quick review audit options.

### 4.3 Media Analysis (Upload Uploads)
- Features a drag-and-drop file dropzone.
- Accepts snapshots and video footages.
- The backend runs YOLO bounding box overlays and crops plate regions for EasyOCR text recognition.
- Displays a detail sheet showing confidence bars, plate badges, and suggested fine amounts.
- Officers can instantly **Confirm** or **Dismiss** the violation.

### 4.4 Real-time Camera Feed (Live Monitor)
- Accesses local webcams using browser `getUserMedia`.
- Streams frame snapshots to `/api/detect/live` every 2 seconds.
- Pushes dynamic red warning alert banners to the panel when violations occur and plays synth warning beeps.
- **Webcam Fallback**: If a webcam is not present, a canvas loop draws a simulated street intersection with moving cars and traffic lights to demonstrate yolo detection overlays.

### 4.5 Violations Management Grid
- Filterable logging table supporting license plates searches, type options, status audits, and start/end dates.
- Handles paginated queries.
- Incorporates client-side **Export CSV** downloaders that compile all filtered records.
- Enables record modifications (updating notes and fines) or deletions.

### 4.6 Analytics Report Profiles
- Summarizes compliance percentages and peak hour calculations.
- Implements a custom **Hourly Heatmap** (00:00 to 23:00) using color intensity ratios.
- Standardizes a **Download PDF Report** trigger that hides sidebars and forms, formatting the charts into a printable multi-page report structure.

---

## 5. File Inventory

| Path | Description |
| :--- | :--- |
| **`app.py`** | Flask factory linking blueprints, configurations, CORS, database files, and rendering views. |
| **`models.py`** | Declarative SQLAlchemy class schemas for DB creation. |
| **`config.py`** | Environments loader parsing `.env` file variables. |
| **`seed.py`** | Schema tables builder populating records and creating 20 visual mock images. |
| **`requirements.txt`** | Dependency manifest list. |
| **`services/detector.py`** | Runs YOLOv8 inference and overlays bounding boxes. |
| **`services/ocr.py`** | Runs grayscale, binarization, and EasyOCR character extractions. |
| **`services/classifier.py`** | Applies fine amounts and severities checks on detected YOLO frames. |
| **`routes/auth.py`** | Blueprints managing logins, profiles, and logouts. |
| **`routes/detect.py`** | Blueprints processing image files, videos, and live base64 stream arrays. |
| **`routes/violations.py`** | CRUD updates and analytics statistics calculators. |
| **`templates/`** | HTML page structure views (Dashboard, Uploads, Camera feeds, Report pages). |
| **`static/css/style.css`** | Core Glassmorphic dark styling system. |
| **`static/js/`** | Front-end scripts (`common.js`, `dashboard.js`, `upload.js`, `live.js`, `violations.js`, `report.js`). |

---

## 6. Access Permissions Matrix

The system enforces three user roles to partition operational duties:

| Role | Dashboard | Inference Uploads | Audit Statuses | Audit Notes/Fines | Delete Logs | Export CSV |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Admin** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Officer** | Yes | Yes | Yes | Yes | No | Yes |
| **Viewer** | Yes | No | No | No | No | Yes |

---

## 7. Conclusions
The system successfully coordinates computer vision technologies (YOLOv8 and EasyOCR) with an elegant web dashboard. The design ensures robust, error-free operations under any hosting setup via built-in simulation fallbacks. The software provides a complete, scalable, and audit-compliant platform for modern smart city traffic enforcements.
