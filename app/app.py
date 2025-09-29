# StudentScoreAI Flask App
# Author: Mubasshir Ahmed
# Purpose: Serve ML predictions from trained model via web form.

from flask import Flask, request, render_template
import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "student_mark_prediction.pkl"
LOG_PATH = BASE_DIR.parent / "data" / "predictions_log.csv"

# Initialize Flask app
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))

# Load model
try:
    model = joblib.load(MODEL_PATH)
    logging.info(f"Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    raise RuntimeError(f"Could not load model from {MODEL_PATH}: {e}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Fetch input safely
        hours_str = request.form.get("study_hours", "").strip()
        hours = float(hours_str)

        # Validate input
        if hours < 0 or hours > 24:
            return render_template("index.html", prediction_text="❌ Please enter valid study hours between 0 and 24.")

        # Predict
        X = np.array([[hours]])
        pred = float(model.predict(X).item())
        pred = max(0.0, min(100.0, round(pred, 2)))  # clamp between 0–100

        # Log to CSV
        log_entry = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "study_hours": hours,
            "predicted_marks": pred
        }])
        if not LOG_PATH.exists():
            log_entry.to_csv(LOG_PATH, index=False)
        else:
            log_entry.to_csv(LOG_PATH, mode="a", header=False, index=False)
        logging.info(f"Logged prediction: hours={hours}, pred={pred}")

        return render_template("index.html",
                               prediction_text=f"📊 Predicted Marks: {pred}% for {hours} study hours/day")
    except Exception as e:
        logging.error(f"Error in prediction: {e}")
        return render_template("index.html",
                               prediction_text="⚠️ An error occurred while processing your request.")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
