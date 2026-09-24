"""
AutoChain AI - Delivery Delay Risk Prediction Web App
------------------------------------------------------
Flask backend that serves trained XGBoost + LSTM models
behind a simple REST API and friendly single-page dashboard.

Usage:
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000
"""
import os
import math
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

# Optional: only needed if the LSTM model is available.
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Feature schema (must match training notebook)
NUMERIC_FEATURES = [
    "shipping_days_scheduled", "order_item_quantity", "product_price", "sales",
    "order_item_discount", "order_item_discount_rate",
    "avg_delay_1d", "avg_delay_2d", "avg_delay_3d", "avg_delay_5d",
    "late_rate_1d", "late_rate_2d", "late_rate_3d", "late_rate_5d",
    "order_volume_1d", "order_volume_2d", "order_volume_3d", "order_volume_5d",
    "order_month", "order_dayofweek", "order_dayofmonth", "order_weekofyear",
    "month_sin", "month_cos", "dow_sin", "dow_cos",
    "active_disaster_count", "known_disaster_count",
    "current_max_disaster_magnitude", "current_max_affected", "current_max_deaths",
]

CATEGORY_BASES = [
    "shipping_mode", "order_country", "customer_country",
    "order_region", "market", "department_name", "category_name", "customer_segment",
]

SEQUENCE_LENGTH = 30

# Fallback dropdown values (used when model is not available)
FALLBACK_OPTIONS = {
    "shipping_mode": ["Standard Class", "First Class", "Second Class", "Same Day"],
    "order_region": ["Western Europe", "Central America", "South America", "Southeast Asia",
                      "Eastern Asia", "South Asia", "West Africa", "North Africa", "US Center"],
    "market": ["Europe", "LATAM", "Pacific Asia", "USCA", "Africa"],
    "department_name": ["Fan Shop", "Apparel", "Golf", "Footwear", "Fitness", "Outdoors"],
    "category_name": ["Cleats", "Men's Footwear", "Women's Apparel", "Indoor/Outdoor Games",
                       "Fishing", "Camping & Hiking", "Water Sports"],
    "customer_segment": ["Consumer", "Corporate", "Home Office"],
    "order_country": ["United States", "Vietnam", "Germany", "France", "Brazil", "Mexico",
                       "Australia", "China", "India", "Japan"],
    "customer_country": ["United States", "Puerto Rico"],
}

# Risk presets based on shipping trend
RISK_PRESETS = {
    "good":   dict(avg_delay=0.3, late_rate=0.10, volume=15),
    "normal": dict(avg_delay=0.8, late_rate=0.28, volume=25),
    "bad":    dict(avg_delay=2.0, late_rate=0.55, volume=40),
}

# Risk thresholds
RISK_LOW_THRESHOLD = 0.5
RISK_MEDIUM_THRESHOLD = 1.5

# Safety stock calculation parameters
SAFETY_STOCK_MULTIPLIER = 1.5
SAFETY_STOCK_BASE = 1

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__, template_folder="templates")

# ============================================================================
# MODEL LOADING & MANAGEMENT
# ============================================================================

class ModelBundle:
    """
    Manages loading and caching of XGBoost and LSTM models.
    Handles fallback when models are not available.
    """
    
    def __init__(self):
        self.xgb_model = None
        self.scaler = None
        self.lstm_model = None
        self.feature_names = None
        self.category_options = {}
        self.load()

    def load(self):
        """Load models and scalers from disk."""
        xgb_path = os.path.join(MODELS_DIR, "xgboost_delay_model.pkl")
        scaler_path = os.path.join(MODELS_DIR, "sequence_scaler.pkl")
        lstm_path = os.path.join(MODELS_DIR, "lstm_delay_model.keras")

        # Load XGBoost model
        if os.path.exists(xgb_path):
            try:
                self.xgb_model = joblib.load(xgb_path)
                try:
                    self.feature_names = list(self.xgb_model.get_booster().feature_names)
                except Exception:
                    self.feature_names = list(getattr(self.xgb_model, "feature_names_in_", []))
                print(f"✓ XGBoost model loaded: {len(self.feature_names)} features")
            except Exception as e:
                print(f"✗ Failed to load XGBoost: {e}")
        else:
            print(f"⚠ XGBoost model not found: {xgb_path}")

        # Load Scaler
        if os.path.exists(scaler_path):
            try:
                self.scaler = joblib.load(scaler_path)
                print("✓ Scaler loaded")
            except Exception as e:
                print(f"✗ Failed to load scaler: {e}")
        else:
            print(f"⚠ Scaler not found: {scaler_path}")

        # Load LSTM model (optional)
        if TF_AVAILABLE and os.path.exists(lstm_path):
            try:
                self.lstm_model = tf.keras.models.load_model(lstm_path)
                print("✓ LSTM model loaded")
            except Exception as e:
                print(f"✗ Failed to load LSTM: {e}")
        else:
            if os.path.exists(lstm_path):
                print(f"⚠ LSTM not available (TensorFlow not installed)")
            else:
                print(f"⚠ LSTM model not found: {lstm_path}")

        self._build_category_options()

    def _build_category_options(self):
        """Extract category options from feature names."""
        options = {b: set() for b in CATEGORY_BASES}
        
        if self.feature_names:
            for col in self.feature_names:
                if col in NUMERIC_FEATURES:
                    continue
                base = max(
                    (b for b in CATEGORY_BASES if col.startswith(b + "_")),
                    key=len, default=None,
                )
                if base:
                    options[base].add(col[len(base) + 1:])
        
        for b in CATEGORY_BASES:
            vals = sorted(options[b]) if options[b] else FALLBACK_OPTIONS.get(b, [])
            options[b] = vals
        
        self.category_options = options

    @property
    def ready(self):
        """Check if model is ready for predictions."""
        return self.xgb_model is not None


# Load models at startup
bundle = ModelBundle()

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def build_feature_row(payload):
    """
    Build feature vector from user input.
    
    Args:
        payload: Dict containing form data from user
    
    Returns:
        (row, numeric_values): Feature dict and raw numeric values
    """
    row = {f: 0.0 for f in (bundle.feature_names or [])}

    # Parse input values with defaults
    price = float(payload.get("product_price") or 0)
    qty = float(payload.get("order_item_quantity") or 1)
    discount_rate = float(payload.get("discount_rate") or 0) / 100.0

    # Numeric features
    numeric_values = {
        "shipping_days_scheduled": float(payload.get("shipping_days_scheduled") or 4),
        "order_item_quantity": qty,
        "product_price": price,
        "sales": price * qty,
        "order_item_discount": price * qty * discount_rate,
        "order_item_discount_rate": discount_rate,
    }

    # Apply trend-based risk presets
    preset = RISK_PRESETS.get(payload.get("trend", "normal"), RISK_PRESETS["normal"])
    for w in (1, 2, 3, 5):
        numeric_values[f"avg_delay_{w}d"] = preset["avg_delay"]
        numeric_values[f"late_rate_{w}d"] = preset["late_rate"]
        numeric_values[f"order_volume_{w}d"] = preset["volume"]

    # Parse and encode date
    order_date_str = payload.get("order_date") or datetime.today().strftime("%Y-%m-%d")
    try:
        order_date = datetime.strptime(order_date_str, "%Y-%m-%d")
    except ValueError:
        order_date = datetime.today()

    month = order_date.month
    dow = order_date.weekday()
    numeric_values.update({
        "order_month": month,
        "order_dayofweek": dow,
        "order_dayofmonth": order_date.day,
        "order_weekofyear": int(order_date.isocalendar()[1]),
        "month_sin": math.sin(2 * math.pi * month / 12),
        "month_cos": math.cos(2 * math.pi * month / 12),
        "dow_sin": math.sin(2 * math.pi * dow / 7),
        "dow_cos": math.cos(2 * math.pi * dow / 7),
    })

    # Disaster features
    if payload.get("disaster_toggle"):
        numeric_values.update({
            "active_disaster_count": float(payload.get("disaster_magnitude", 1) or 1),
            "known_disaster_count": float(payload.get("disaster_magnitude", 1) or 1),
            "current_max_disaster_magnitude": float(payload.get("disaster_magnitude") or 5),
            "current_max_affected": float(payload.get("disaster_affected") or 10000),
            "current_max_deaths": float(payload.get("disaster_deaths") or 0),
        })
    else:
        numeric_values.update({
            "active_disaster_count": 0.0,
            "known_disaster_count": 0.0,
            "current_max_disaster_magnitude": 0.0,
            "current_max_affected": 0.0,
            "current_max_deaths": 0.0,
        })

    # Fill numeric features
    for key, val in numeric_values.items():
        if key in row:
            row[key] = val

    # One-hot encode categorical features
    for base in CATEGORY_BASES:
        val = payload.get(base)
        if val:
            col = f"{base}_{val}"
            if col in row:
                row[col] = 1.0

    return row, numeric_values


def risk_label(days):
    """
    Classify delay days into risk levels.
    
    Args:
        days: Predicted delay days
    
    Returns:
        (risk_level, risk_label_vn): Tuple of (css_class, Vietnamese label)
    """
    if days < RISK_LOW_THRESHOLD:
        return "low", "Thấp"
    elif days < RISK_MEDIUM_THRESHOLD:
        return "medium", "Trung bình"
    return "high", "Cao"


def top_factors(n=6):
    """
    Extract top N important features.
    
    Args:
        n: Number of top factors to return
    
    Returns:
        List of dicts with feature name and importance share
    """
    if bundle.xgb_model is None or bundle.feature_names is None:
        return []
    
    try:
        importances = bundle.xgb_model.feature_importances_
    except Exception:
        return []
    
    # Sort by importance and take top N
    pairs = sorted(zip(bundle.feature_names, importances), key=lambda x: -x[1])
    pairs = [p for p in pairs if p[1] > 0][:n]
    
    # Normalize to percentages
    total = sum(p[1] for p in pairs) or 1.0
    return [
        {"feature": f, "share": round(float(v) / total * 100, 1)}
        for f, v in pairs
    ]


def safety_stock_days(delay_days):
    """
    Calculate safety stock buffer based on predicted delay.
    
    Rule: buffer = max(0, delay_days) * 1.5 + 1
    """
    return round(max(0.0, delay_days) * SAFETY_STOCK_MULTIPLIER + SAFETY_STOCK_BASE, 1)


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route("/")
def index():
    """Render main dashboard."""
    return render_template(
        "index.html",
        options=bundle.category_options,
        model_ready=bundle.ready,
        lstm_ready=bundle.lstm_model is not None,
        today=datetime.today().strftime("%Y-%m-%d"),
    )


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    API endpoint for predictions.
    
    Accepts JSON payload with order details, returns JSON with predictions.
    """
    if not bundle.ready:
        return jsonify({"error": "Mô hình chưa sẵn sàng trên máy chủ."}), 503

    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

    # Build feature row
    row, numeric_values = build_feature_row(payload)

    # Prepare dataframe for XGBoost
    X = pd.DataFrame([row])
    if bundle.feature_names:
        X = X.reindex(columns=bundle.feature_names, fill_value=0.0)

    # XGBoost prediction
    try:
        xgb_pred = float(bundle.xgb_model.predict(X)[0])
        xgb_pred = max(0.0, xgb_pred)
    except Exception as e:
        return jsonify({"error": f"XGBoost prediction failed: {str(e)}"}), 500

    result = {
        "xgboost": {"delay_days": round(xgb_pred, 2)},
        "top_factors": top_factors(),
        "safety_stock_days": safety_stock_days(xgb_pred),
    }

    # LSTM prediction (optional)
    if bundle.lstm_model is not None and bundle.scaler is not None:
        try:
            # Extract numeric features in order
            vec = np.array([[numeric_values.get(f, 0.0) for f in NUMERIC_FEATURES]])
            
            # Scale
            scaled = bundle.scaler.transform(vec)
            
            # Create sequence by repeating
            seq = np.repeat(scaled[:, np.newaxis, :], SEQUENCE_LENGTH, axis=1)
            
            # Predict
            lstm_pred = float(bundle.lstm_model.predict(seq, verbose=0)[0][0])
            result["lstm"] = {"delay_days": round(max(0.0, lstm_pred), 2)}
        except Exception as e:
            result["lstm"] = {"error": str(e)}

    # Determine risk level
    level, level_label = risk_label(xgb_pred)
    result["risk_level"] = level
    result["risk_label"] = level_label

    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "model_ready": bundle.ready,
        "lstm_ready": bundle.lstm_model is not None,
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AutoChain AI - Delivery Delay Risk Prediction")
    print("=" * 70)
    print(f"Starting Flask app at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    app.run(debug=True, port=5000, host="127.0.0.1")
