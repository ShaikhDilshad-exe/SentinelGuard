import logging
import joblib
import os
from pathlib import Path
from typing import Dict
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class ThreatClassifier:
    def __init__(self, model_path: str = "ml_model/sentinel_model.pkl"):
        # 1. ALWAYS initialize the basic structures first
        self.scaler = StandardScaler() 
        self.feature_names = ['cpu_percent', 'memory_percent', 'num_threads', 'entropy']
        
        # 2. ALWAYS initialize the model object so it's never None
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # 3. If a path is provided, build an absolute path and load the model
        if model_path:
            # Dynamically construct the absolute path from this file's location
            try:
                # Get the directory of the current file (threat_classifier.py)
                base_dir = Path(__file__).resolve().parent.parent
                # Join with the provided relative path
                absolute_model_path = base_dir / model_path
                self.load_model(str(absolute_model_path))
            except Exception as e:
                logger.error(f"Error constructing model path: {e}")

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Fits the scaler and then trains the model[cite: 5]."""
        logger.info("Training threat classifier model...")
        # Fit the scaler to the training data
        X_train_scaled = self.scaler.fit_transform(X_train) 
        # Now self.model is guaranteed to exist
        self.model.fit(X_train_scaled, y_train) 
        logger.info("Model training completed successfully.")

    def predict(self, data: Dict) -> Dict:
        """Predict if system behavior is anomalous."""
        try:
            # DEFENSIVE CHECK: If scaler isn't fitted, try one last emergency load
            if not hasattr(self.scaler, 'mean_'):
                model_dir = os.path.dirname(os.path.abspath(__file__))
                scaler_path = os.path.join(model_dir, "sentinel_model_scaler.pkl")
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                else:
                    return {"is_anomaly": False, "anomaly_score": 0.0}

            features = np.array([[
                data.get('cpu_percent', 0.0),
                data.get('memory_percent', 0.0),
                data.get('num_threads', 0),
                data.get('entropy', 3.0)
            ]])
            
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)[0]
            confidence = self.model.predict_proba(features_scaled)[0][1]
            
            return {
                "is_anomaly": bool(prediction == 1),
                "anomaly_score": round(float(confidence) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Prediction Error: {e}")
            return {"is_anomaly": False, "anomaly_score": 0.0}

    def save_model(self, model_path: str) -> bool:
        """Saves the model and the scaler state[cite: 5]."""
        try:
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, model_path.replace('.pkl', '_scaler.pkl'))
            return True
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False

    def load_model(self, model_path: str) -> bool:
        """Loads model and scaler from disk and ensures they are ready for use."""
        try:
            scaler_path = model_path.replace('.pkl', '_scaler.pkl')
            if Path(model_path).exists() and Path(scaler_path).exists():
                # Load and explicitly assign to self.model and self.scaler
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Successfully loaded fitted Model and Scaler from a new path.")
                return True
            
            logger.error(f"Fitted model files not found at path: {model_path}")
            return False
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return False