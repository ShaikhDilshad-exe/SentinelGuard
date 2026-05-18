# SentinelGuard - AI Real-Time Antivirus System

A scalable, modern antivirus system powered by machine learning and real-time monitoring. SentinelGuard provides comprehensive threat detection, file monitoring, and process analysis capabilities.

## 📋 Project Overview

SentinelGuard is an AI-driven antivirus solution that combines:
- **Real-time System Monitoring** - Files, processes, and system events
- **Machine Learning Detection** - Behavioral and signature-based threat detection
- **Alert Management** - Intelligent alerting and notifications
- **Web Dashboard** - Intuitive React-based user interface
- **Desktop Application** - Optional Electron wrapper for native OS integration

## 🏗️ Project Structure

```
SentinelGuard/
├── backend/                    # FastAPI backend server
│   ├── monitoring/            # Real-time system monitoring modules
│   │   ├── file_monitor.py   # File system monitoring
│   │   └── process_monitor.py # Process monitoring
│   ├── detection/             # Threat detection modules
│   │   ├── threat_detector.py # Core threat detection
│   │   └── heuristic_analyzer.py # Behavior-based analysis
│   ├── alerts/                # Alert management
│   │   ├── alert_manager.py   # Alert creation and management
│   │   └── notification_service.py # Multi-channel notifications
│   ├── routes/                # API endpoints
│   │   ├── auth_routes.py    # Authentication
│   │   ├── monitoring_routes.py # Monitoring data endpoints
│   │   ├── alerts_routes.py  # Alert endpoints
│   │   └── scan_routes.py    # File/process scanning endpoints
│   ├── utils/                 # Utility functions
│   │   ├── logger.py         # Logging configuration
│   │   ├── config.py         # Configuration management
│   │   └── __init__.py
│   ├── main.py               # FastAPI application entry point
│   └── requirements.txt       # Python dependencies
│
├── ml-model/                  # Machine Learning module
│   ├── threat_classifier.py   # ML classification model
│   ├── feature_extractor.py   # Feature extraction from files/processes
│   ├── model_training.py      # Model training and evaluation
│   ├── __init__.py
│   └── requirements.txt       # ML dependencies
│
├── frontend/                  # React web interface
│   ├── src/                   # React source code
│   ├── public/                # Static assets
│   ├── package.json           # npm dependencies
│   └── README.md              # Frontend setup guide
│
├── electron/                  # Electron desktop application (optional)
│   ├── main.js               # Electron main process
│   ├── preload.js            # IPC bridge
│   ├── renderer/             # React frontend
│   ├── package.json          # npm dependencies
│   └── README.md             # Electron setup guide
│
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 📁 Folder Descriptions

### Backend (`backend/`)
FastAPI-based REST API server that coordinates all antivirus operations.

**Subfolders:**
- **monitoring/** - Tracks file system and process activities
  - `file_monitor.py` - Monitors file creation, modification, deletion events
  - `process_monitor.py` - Tracks running processes and resource usage

- **detection/** - Identifies and analyzes potential threats
  - `threat_detector.py` - Signature-based and ML-based threat identification
  - `heuristic_analyzer.py` - Behavioral pattern analysis

- **alerts/** - Manages threat notifications
  - `alert_manager.py` - Creates, stores, and retrieves alerts
  - `notification_service.py` - Sends alerts via email, SMS, webhooks

- **routes/** - API endpoint handlers
  - `auth_routes.py` - User login/registration
  - `monitoring_routes.py` - System monitoring data endpoints
  - `alerts_routes.py` - Alert retrieval and management
  - `scan_routes.py` - File and process scanning endpoints

- **utils/** - Helper functions
  - `logger.py` - Centralized logging configuration
  - `config.py` - Environment and application settings

### ML Model (`ml-model/`)
Machine learning components for intelligent threat detection.

**Contents:**
- `threat_classifier.py` - RandomForest-based threat classification model
- `feature_extractor.py` - Extracts features from files and processes (entropy, file type, metadata)
- `model_training.py` - Training pipeline with evaluation metrics
- `requirements.txt` - ML-specific Python packages (scikit-learn, TensorFlow, etc.)

### Frontend (`frontend/`)
React web application providing real-time monitoring dashboard.

**Features:**
- Authentication and user management
- Real-time threat alerts
- System statistics visualization
- File scanning interface
- Process monitoring view

### Electron (`electron/`)
Optional native desktop application wrapper.

**Features:**
- System tray integration
- Native OS notifications
- Auto-update capability
- Cross-platform support (Windows/macOS/Linux)

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- pip and npm package managers

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Run the backend server:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### ML Model Setup

1. **Install ML dependencies:**
```bash
cd ml-model
pip install -r requirements.txt
```

2. **Train or load a model:**
```python
from threat_classifier import ThreatClassifier

# Load pre-trained model
classifier = ThreatClassifier("path/to/model.pkl")

# Or train new model
classifier.train(X_train, y_train)
classifier.save_model("path/to/model.pkl")
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### Electron Setup (Optional)

1. **Install dependencies:**
```bash
cd electron
npm install
```

2. **Run Electron app:**
```bash
npm start
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout

### Monitoring
- `GET /api/monitoring/processes` - List running processes
- `GET /api/monitoring/processes/{pid}` - Process details
- `GET /api/monitoring/system-stats` - System statistics
- `POST /api/monitoring/monitor/start` - Start monitoring
- `POST /api/monitoring/monitor/stop` - Stop monitoring

### Scanning
- `POST /api/scan/file` - Scan single file
- `POST /api/scan/directory` - Scan directory
- `POST /api/scan/process/{pid}` - Analyze process
- `GET /api/scan/status` - Scan status

### Alerts
- `GET /api/alerts/` - List alerts
- `GET /api/alerts/{alert_id}` - Alert details
- `POST /api/alerts/{alert_id}/resolve` - Resolve alert
- `GET /api/alerts/stats/summary` - Alert statistics

## 🔧 Configuration

Create a `.env` file (based on `.env.example`) with:

```env
# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DB_URL=sqlite:///sentinel_guard.db

# ML Model
ML_MODEL_PATH=./models/threat_detector.pkl
SIGNATURE_DB_PATH=./data/signatures.db

# Monitoring
MONITORING_INTERVAL=5
WATCH_PATHS=/

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/sentinel_guard.log

# JWT
JWT_SECRET=your-secret-key-change-in-production
```

## 🛡️ Security Features

- Real-time file and process monitoring
- Machine learning-based threat classification
- Signature-based detection
- Heuristic behavior analysis
- Multi-channel alert notifications (email, SMS, webhooks)
- JWT-based API authentication
- CORS protection

## 📊 Monitoring Capabilities

- **File Monitoring** - Tracks file creation, modification, deletion, access
- **Process Monitoring** - CPU, memory, network usage analysis
- **System Statistics** - CPU, memory, disk utilization
- **Behavioral Analysis** - Detects suspicious activity patterns
- **Real-time Alerts** - Immediate threat notifications

## 🤖 Machine Learning

- **Feature Extraction** - Entropy, file type, metadata analysis
- **Classification** - RandomForest model for threat prediction
- **Training Pipeline** - Train on labeled malware/benign datasets
- **Model Evaluation** - Accuracy, ROC-AUC, confusion matrix metrics

## 📝 Development

### Code Structure Best Practices
- Modular design with clear separation of concerns
- Async/await for I/O operations
- Comprehensive logging throughout
- Configuration management via environment variables
- Type hints for better code clarity

### Adding New Features
1. Create feature in appropriate module
2. Add API endpoint in routes
3. Update frontend components
4. Document changes in relevant README

## 📄 License

[Add your license information here]

## 👥 Contributing

[Add contribution guidelines here]

## 📞 Support

For issues, questions, or contributions, please contact the development team.

---

**SentinelGuard** - Protecting Systems with AI-Powered Threat Detection
