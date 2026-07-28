# Anode Tracking System

> An OCR-based industrial tracking application for automated identification, logging, and monitoring of anode numbers using computer vision.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python\&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-orange)
![MySQL](https://img.shields.io/badge/Database-MySQL-blue?logo=mysql\&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

## Overview

The **Anode Tracking System** is a Python-based desktop application developed for the **Jawaharlal Nehru Aluminium Research Development and Design Centre (JNARDDC), Nagpur**.

The system automates the identification and tracking of anode numbers using **Optical Character Recognition (OCR)** and **computer vision**.

A live camera feed is processed using **OpenCV** and **EasyOCR** to detect anode numbers. Recognised numbers can then be stored in a **MySQL database**, allowing the system to maintain entry and exit timestamps for individual anodes.

The application also provides a graphical interface for monitoring detections, viewing historical records, and exporting tracking data to Excel.

---

## Key Features

* **Real-Time Camera Processing**
  Continuously captures and processes video frames from a connected camera.

* **OCR-Based Anode Detection**
  Uses EasyOCR to identify anode numbers directly from camera frames.

* **Confidence Filtering**
  Filters OCR detections using a configurable confidence threshold.

* **Visual Detection Feedback**
  Displays recognised text with bounding boxes directly on the live camera feed.

* **Entry and Exit Tracking**
  Automatically manages anode entry and exit timestamps.

* **MySQL Database Integration**
  Stores tracking records persistently using a structured relational database.

* **Record Management**
  Displays stored tracking records through the application interface.

* **Excel Export**
  Exports tracking data to `.xlsx` files for reporting and further analysis.

* **Configurable Environment**
  Database, OCR, camera, export, and application settings can be controlled through environment variables.

* **Modular Architecture**
  Separates camera handling, OCR, database operations, GUI components, configuration, and utility functions.

---

## How the System Works

The overall processing pipeline is:

```text
Camera Feed
     │
     ▼
OpenCV Frame Capture
     │
     ▼
EasyOCR Processing
     │
     ▼
Confidence Filtering
     │
     ▼
Anode Number Detection
     │
     ▼
User Confirmation / Save
     │
     ▼
MySQL Database
     │
     ├── First Scan  → Entry Time
     │
     └── Next Scan   → Exit Time
     │
     ▼
Record Viewer / Excel Export
```

### Tracking Logic

When an anode number is detected and saved:

**First scan**

A new database record is created containing:

```text
Anode Number
Date Entry
Time In
```

**Subsequent scan next time**

The corresponding record is updated with:

```text
Date Out
Time Out
```

This allows the application to track both the **entry and exit time** of an anode.

---

## System Architecture

```text
┌───────────────────────────────────────────────────────┐
│                    GUI Layer                          │
│                    Tkinter                            │
│                                                       │
│  Camera Feed    Anode Number    Actions / Records     │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│                  Processing Layer                     │
│                                                       │
│       Camera Handler          OCR Engine              │
│         OpenCV                EasyOCR                 │
└─────────────────────────┬─────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────┐
│                     Data Layer                        │
│                                                       │
│                 Database Manager                      │
│                      MySQL                            │
│                                                       │
│       INSERT       UPDATE       SELECT                │
└───────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Technology        | Purpose                             |
| ----------------- | ----------------------------------- |
| **Python 3.8+**   | Core application development        |
| **Tkinter**       | Desktop graphical user interface    |
| **OpenCV**        | Camera capture and image processing |
| **EasyOCR**       | Optical character recognition       |
| **MySQL**         | Persistent tracking database        |
| **NumPy**         | Image and numerical operations      |
| **Pillow**        | OpenCV-to-Tkinter image conversion  |
| **Pandas**        | Data processing and export          |
| **OpenPyXL**      | Excel file generation               |
| **python-dotenv** | Environment configuration           |

---

## Project Structure

```text
anode_tracker/
│
├── README.md
├── requirements.txt
├── .env.example
├── config.py
├── main.py
│
├── camera/
│   ├── __init__.py
│   └── camera_handler.py
│
├── database/
│   ├── __init__.py
│   └── db_manager.py
│
├── ocr/
│   ├── __init__.py
│   └── ocr_engine.py
│
├── gui/
│   ├── __init__.py
│   ├── app.py
│   └── styles.py
│
├── utils/
│   ├── __init__.py
│   └── helpers.py
│
└── tests/
    └── test_ocr.py
```

### Module Responsibilities

| Module      | Responsibility                             |
| ----------- | ------------------------------------------ |
| `main.py`   | Application entry point                    |
| `config.py` | Centralised application configuration      |
| `camera/`   | Camera initialisation and frame capture    |
| `ocr/`      | OCR detection and confidence filtering     |
| `database/` | MySQL connections and tracking operations  |
| `gui/`      | Tkinter interface and application workflow |
| `utils/`    | Helper and validation functions            |
| `tests/`    | Automated tests                            |

---

## Prerequisites

Before running the application, ensure that the following are installed:

* Python **3.8 or later**
* MySQL Server **5.7+** or MariaDB **10.3+**
* Working USB or built-in webcam
* `pip`
* Git

Optional:

* Basler industrial camera
* Pylon SDK
* CUDA-compatible GPU for OCR acceleration

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/0ye0m/anode-tracker-jnarddc.git
cd anode-tracker-jnarddc
```


### 2. Create a Virtual Environment

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file using `.env.example`.

### Linux / macOS

```bash
cp .env.example .env
```

### Windows

```cmd
copy .env.example .env
```

Configure the required settings:

```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=jnarddc

# OCR
OCR_CONFIDENCE_THRESHOLD=0.5
OCR_LANGUAGES=en

# Camera
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# Export
DOWNLOAD_DIR=~/Downloads

# Application
APP_TITLE=Anode Tracker
APP_BG_COLOR=#FBEEC1
```

> Do not commit your real `.env` file or database credentials to GitHub.

---

## Database Setup

Start MySQL and create the required database.

```sql
CREATE DATABASE IF NOT EXISTS jnarddc;

USE jnarddc;
```

Create the tracking table:

```sql
CREATE TABLE IF NOT EXISTS stem_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pot_number VARCHAR(100) NOT NULL,
    date_entry DATE NOT NULL,
    time_in TIME NOT NULL,
    date_out DATE NULL,
    time_out TIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_pot_date (pot_number, date_entry)
);
```

---

## Database Schema

### `stem_analysis`

| Column       | Type           | Description               |
| ------------ | -------------- | ------------------------- |
| `id`         | `INT`          | Primary key               |
| `pot_number` | `VARCHAR(100)` | Detected anode/pot number |
| `date_entry` | `DATE`         | Entry date                |
| `time_in`    | `TIME`         | Entry time                |
| `date_out`   | `DATE`         | Exit date                 |
| `time_out`   | `TIME`         | Exit time                 |
| `created_at` | `TIMESTAMP`    | Record creation timestamp |

The combination of the anode number and entry date is indexed to improve lookup performance.

---

## Running the Application

Once the environment and database are configured:

```bash
python main.py
```

The application will initialise:

1. Application configuration
2. OCR engine
3. MySQL connection pool
4. Camera
5. Tkinter interface
6. Real-time OCR processing

---

## Usage

### Detect an Anode

Position the anode number clearly in front of the camera.

The application continuously processes incoming frames using EasyOCR.

When valid text is detected, a bounding box and the recognised number are displayed on screen.

### Save a Detection

Once the correct anode number appears:

```text
Anode Number: <detected-number>
```

Click **Save**.

If the number has not been recorded that day, the system creates an **entry record**.

If the number already exists for that day, the system updates its **exit information**.

### View Tracking Records

Click:

```text
Info
```

A separate window displays:

* Pot/Anode Number
* Entry Date
* Entry Time
* Exit Date
* Exit Time

### Export Records

Inside the information window, click:

```text
Download
```

The application exports the records to an Excel file using a timestamped filename such as:

```text
stem_analysis_20260728_183000.xlsx
```

---

## Configuration

| Variable                   | Description                     | Default         |
| -------------------------- | ------------------------------- | --------------- |
| `DB_HOST`                  | MySQL host                      | `localhost`     |
| `DB_USER`                  | MySQL username                  | `root`          |
| `DB_PASSWORD`              | MySQL password                  | Required        |
| `DB_NAME`                  | Database name                   | `jnarddc`       |
| `OCR_CONFIDENCE_THRESHOLD` | Minimum accepted OCR confidence | `0.5`           |
| `OCR_LANGUAGES`            | EasyOCR languages               | `en`            |
| `CAMERA_INDEX`             | Camera device index             | `0`             |
| `CAMERA_WIDTH`             | Camera frame width              | `640`           |
| `CAMERA_HEIGHT`            | Camera frame height             | `480`           |
| `DOWNLOAD_DIR`             | Excel export location           | `~/Downloads`   |
| `APP_TITLE`                | Window title                    | `Anode Tracker` |
| `APP_BG_COLOR`             | Application background          | `#FBEEC1`       |

---

## OCR Processing

The OCR module uses **EasyOCR** to analyse each frame captured by OpenCV.

A detection contains:

```text
Bounding Box
Recognised Text
Confidence Score
```

Detections below the configured threshold are ignored.

For example:

```env
OCR_CONFIDENCE_THRESHOLD=0.5
```

Only detections with a confidence score of at least `0.5` are treated as valid.

The system can also select the detection with the highest confidence when multiple text regions are present.

---

## Camera Support

The default configuration uses OpenCV:

```python
cv2.VideoCapture(0)
```

The camera index can be changed through:

```env
CAMERA_INDEX=1
```

Common values are:

```text
0 → Default camera
1 → Secondary camera
2 → Additional connected camera
```

The architecture can also be extended for industrial cameras such as **Basler cameras** using the Pylon SDK and `pypylon`.

---

## Excel Export

Tracking records are converted to a Pandas DataFrame and exported using Excel format.

Generated files follow the naming pattern:

```text
stem_analysis_YYYYMMDD_HHMMSS.xlsx
```

This prevents previous exports from being overwritten and makes generated reports easy to organise chronologically.

---

## Error Handling & Logging

The application includes logging and error handling for:

* Database connection failures
* SQL operation failures
* Camera initialisation errors
* OCR processing failures
* Excel export errors
* File operations
* Application shutdown

Example log format:

```text
2024-03-28 12:30:00 - database.db_manager - INFO - Database connection pool initialized successfully
```

---

## Testing

The project includes a testable OCR architecture with mockable dependencies.

Run tests using:

```bash
python -m pytest tests/
```

The OCR tests cover functionality such as:

* OCR engine initialisation
* Bounding-box processing
* Failed OCR processing
* Empty detection results

---

## Development Tools

### Code Formatting

```bash
black .
isort .
```

### Linting

```bash
flake8 .
pylint .
```

### Testing

```bash
pytest
```

---

## Troubleshooting

### Camera Does Not Open

Check whether another application is currently using the camera.

Try another camera index:

```env
CAMERA_INDEX=1
```

You can test `0`, `1`, or `2` depending on the available devices.

Also verify that the required camera drivers are installed.

### OCR Is Not Detecting the Number

Ensure:

* The number is clearly visible
* Lighting is sufficient
* The camera is focused
* Motion blur is minimal
* The number has sufficient contrast from its background

You can also reduce:

```env
OCR_CONFIDENCE_THRESHOLD=0.4
```

A lower threshold increases sensitivity but can also increase false detections.

> EasyOCR may download language model files during its first run.

### Database Connection Error

Verify that MySQL is running and confirm:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=jnarddc
```

Also verify that the configured MySQL user has access to the `jnarddc` database.

### Poor Performance

Possible improvements include:

* Enable GPU acceleration when CUDA is available
* Reduce camera resolution
* Process OCR at intervals rather than on every frame
* Close unnecessary background applications
* Use an industrial camera for stable image capture

---

## Security Considerations

Sensitive credentials should always be stored in `.env`:

```env
DB_PASSWORD=your_secure_password
```

Add `.env` to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
.pytest_cache/
captured_text.txt
*.xlsx
```

Never commit production credentials or database passwords to the repository.

---

## Future Improvements

Potential extensions include:

* Automatic anode detection without manual confirmation
* OCR preprocessing for industrial environments
* Duplicate-detection protection
* OCR result validation
* Basler industrial camera integration
* GPU-accelerated OCR
* Dashboard analytics
* Search and filtering of historical records
* CSV and PDF report generation
* Role-based authentication
* Centralised server database
* REST API integration
* Web-based monitoring dashboard
* Real-time alerts
* Anode movement history
* Improved OCR accuracy under low-light conditions

---

## Authors

**Ms. Shruti N. Pethe**
**Mr. Om P. Mandwade**
**Mr. Ritesh G. Nayase**

Department of Information Technology
Government Polytechnic, Nagpur

---

## Acknowledgments

Special acknowledgement to:

**Dr. Anupam Agnihotri**
Director, JNARDDC

**Mr. Manoj Nimje**
Head of Department, Information Technology

**Mr. V. K. Jha**
Senior Scientist, JNARDDC — Project Guide

---

## Organisation

**Jawaharlal Nehru Aluminium Research Development and Design Centre (JNARDDC)**
Nagpur, Maharashtra, India

*An Autonomous Body under the Ministry of Mines, Government of India*

---

## License

This project was developed as part of an **industrial training programme at JNARDDC, Nagpur**.

Usage, distribution, or modification should follow the applicable institutional and organisational guidelines.

---

## Project Summary

The **Anode Tracking System** demonstrates the integration of:

```text
Computer Vision
       +
Optical Character Recognition
       +
Desktop GUI
       +
Database Management
       +
Automated Reporting
```

to create a practical industrial tracking solution.

The modular architecture separates **camera acquisition, OCR processing, database management, configuration, GUI functionality, and utility operations**, making the application easier to maintain, test, and extend.
