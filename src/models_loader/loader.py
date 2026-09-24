import os
import joblib
from config import Config

try:
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except ImportError:
    print("Warning: TensorFlow not available")
    TF_AVAILABLE = False
    load_model = None

class ModelsLoader:
    def __init__(self):
        self.lstm_model = None
        self.xgboost_model = None
        self.scaler = None
        self.model_ready = False
        self.error_message = ''

    def load_all_models(self):
        try:
            print('[INFO] Initializing models load routine...')
            if TF_AVAILABLE and os.path.exists(Config.LSTM_MODEL_PATH):
                try:
                    self.lstm_model = load_model(Config.LSTM_MODEL_PATH)
                    print(f'✓ LSTM model loaded')
                except Exception as e:
                    print(f'✗ LSTM error: {e}')
            elif not TF_AVAILABLE:
                print('⚠ TensorFlow not available, skipping LSTM model')
            
            if os.path.exists(Config.XGBOOST_MODEL_PATH):
                try:
                    self.xgboost_model = joblib.load(Config.XGBOOST_MODEL_PATH)
                    print(f'✓ XGBoost model loaded')
                except Exception as e:
                    print(f'✗ XGBoost error: {e}')
                    self.xgboost_model = None
            
            if os.path.exists(Config.SCALER_PATH):
                try:
                    self.scaler = joblib.load(Config.SCALER_PATH)
                    print(f'✓ Scaler loaded')
                except Exception as e:
                    print(f'✗ Scaler error: {e}')
                    self.scaler = None
            
            if self.xgboost_model and self.scaler:
                self.model_ready = True
                print('\n✓✓✓ All models loaded successfully into Central Loader! ✓✓✓\n')
            else:
                self.model_ready = False
                missing = []
                if not self.xgboost_model: missing.append('XGBoost')
                if not self.scaler: missing.append('Scaler')
                self.error_message = f'Missing: {", ".join(missing)}'
                print(f'\n⚠ WARNING: {self.error_message}\n')
        except Exception as e:
            self.model_ready = False
            self.error_message = str(e)
            print(f'\n✗ CRITICAL ERROR in ModelsLoader: {self.error_message}\n')
        return self
