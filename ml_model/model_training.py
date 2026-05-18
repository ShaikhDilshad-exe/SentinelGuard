import numpy as np
import os
from threat_classifier import ThreatClassifier

class ModelTrainer:
    def __init__(self):
        self.classifier = ThreatClassifier()

    def generate_simulated_data(self, samples=1000):
        np.random.seed(42)
        # Normal Activity
        normal_X = np.random.normal(loc=[15, 20, 10, 3], scale=[5, 5, 2, 0.5], size=(samples, 4))
        normal_y = np.zeros(samples)

        # Malicious Activity[cite: 9]
        malicious_X = np.random.normal(loc=[85, 70, 80, 7.5], scale=[10, 15, 20, 0.4], size=(int(samples*0.1), 4))
        malicious_y = np.ones(int(samples*0.1))

        X = np.vstack([normal_X, malicious_X])
        y = np.hstack([normal_y, malicious_y])
        return X, y

    def run_training(self):
        X, y = self.generate_simulated_data()
        
        # This now fits the scaler properly
        self.classifier.train(X, y)
        
        # Save to the local directory[cite: 9]
        model_path = os.path.join(os.path.dirname(__file__), "sentinel_model.pkl")
        self.classifier.save_model(model_path)
        print(f"[+] SUCCESS: Model and Fitted Scaler saved at {model_path}")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run_training()