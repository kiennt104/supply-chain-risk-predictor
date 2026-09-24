import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

print("Creating dummy models for testing...")

# Create a dummy scaler
print("\n1. Creating StandardScaler...")
scaler = StandardScaler()
dummy_data = np.random.randn(100, 30)
scaler.fit(dummy_data)
with open('models/sequence_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f, protocol=2)
print("✓ Scaler saved (protocol 2)")

# Create a dummy XGBoost model (using RandomForest as fallback)
print("\n2. Creating dummy XGBoost model...")
try:
    import xgboost as xgb
    model = xgb.XGBRegressor(n_estimators=10, max_depth=5, random_state=42)
    X = np.random.randn(50, 30)
    y = np.random.randn(50)
    model.fit(X, y)
    with open('models/xgboost_delay_model.pkl', 'wb') as f:
        pickle.dump(model, f, protocol=2)
    print("✓ XGBoost model saved")
except:
    print("⚠ XGBoost not available, using RandomForest fallback")
    model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
    X = np.random.randn(50, 30)
    y = np.random.randn(50)
    model.fit(X, y)
    with open('models/xgboost_delay_model.pkl', 'wb') as f:
        pickle.dump(model, f, protocol=2)
    print("✓ RandomForest model saved as xgboost_delay_model.pkl")

print("\n✓✓✓ Dummy models created successfully! ✓✓✓")

# Test loading
print("\nTesting load...")
try:
    with open('models/sequence_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print(f"✓ Scaler loaded: {type(scaler)}")
    
    with open('models/xgboost_delay_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print(f"✓ Model loaded: {type(model)}")
except Exception as e:
    print(f"✗ Error: {e}")
