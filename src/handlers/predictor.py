import numpy as np
import pandas as pd
import traceback
from config import Config

def perform_prediction(features_dict, loader):
    """
    Hàm lõi thực thi dự đoán ghép đôi (Ensemble) giữa XGBoost và LSTM.
    Đầu vào nhận features_dict và đối tượng loader từ models_loader.
    """
    if not loader.model_ready:
        return {
            'success': False,
            'message': loader.error_message,
            'error': loader.error_message,
            'xgboost': {'delay_days': 0},
            'lstm': {'delay_days': 0},
            'risk_level': 'low',
            'risk_label': 'Chưa xác định',
            'top_factors': [],
            'safety_stock_days': 0
        }
    
    try:
        # 1. Chuẩn bị DataFrame cho XGBoost (cần đúng 196 cột theo feature_names_in_)
        if hasattr(loader.xgboost_model, 'feature_names_in_'):
            xgb_features = list(loader.xgboost_model.feature_names_in_)
        else:
            xgb_features = list(features_dict.keys())
            
        df_xgb = pd.DataFrame(0.0, index=[0], columns=xgb_features)
        for col in xgb_features:
            if col in features_dict:
                try:
                    df_xgb[col] = float(features_dict[col])
                except:
                    df_xgb[col] = 0.0

        # 2. Chuẩn bị DataFrame cho Scaler & LSTM (cần đúng 31 cột số)
        if hasattr(loader.scaler, 'feature_names_in_'):
            scaler_cols = list(loader.scaler.feature_names_in_)
        else:
            scaler_cols = Config.NUMERIC_FEATURES

        df_scaler = pd.DataFrame(0.0, index=[0], columns=scaler_cols)
        for col in scaler_cols:
            if col in features_dict:
                try:
                    df_scaler[col] = float(features_dict[col])
                except:
                    df_scaler[col] = 0.0

        lstm_pred = 0.0
        if loader.lstm_model and loader.scaler:
            try:
                X_scaled = loader.scaler.transform(df_scaler)
                # Đưa về dạng (1, 30, 31)
                X_seq = np.repeat(X_scaled, 30, axis=0)
                X_reshaped = X_seq.reshape((1, 30, 31))
                
                raw_lstm = loader.lstm_model.predict(X_reshaped, verbose=0)[0]
                lstm_pred = float(raw_lstm[0] if hasattr(raw_lstm, '__len__') else raw_lstm)
            except Exception as e:
                print(f"[Warning] LSTM inference error: {e}")
                lstm_pred = 0.0
        
        xgb_pred = 0.0
        if loader.xgboost_model:
            try:
                xgb_pred = float(loader.xgboost_model.predict(df_xgb)[0])
            except Exception as e:
                print(f"[Warning] XGBoost inference error: {e}")
                xgb_pred = 0.0
        
        # Hợp nhất kết quả trung bình
        ensemble_pred = (lstm_pred + xgb_pred) / 2 if (lstm_pred > 0 and xgb_pred > 0) else max(lstm_pred, xgb_pred)
        ensemble_pred = max(0.0, ensemble_pred)
        
        if ensemble_pred >= 3.0:
            risk_level = 'high'
            risk_label = 'Cao'
        elif ensemble_pred >= 1.0:
            risk_level = 'medium'
            risk_label = 'Trung bình'
        else:
            risk_level = 'low'
            risk_label = 'Thấp'
            
        top_factors = []
        if xgb_pred > 0:
            factors = [
                {"feature": "Số ngày giao dự kiến", "value": features_dict.get("shipping_days_scheduled", 0) * 15},
                {"feature": "Sự kiện thiên tai khu vực", "value": features_dict.get("active_disaster_count", 0) * 40 + features_dict.get("current_max_disaster_magnitude", 0) * 10},
                {"feature": "Lượng đơn hàng dồn ứ (rolling)", "value": features_dict.get("order_volume_1d", 0) * 5 + features_dict.get("avg_delay_3d", 0) * 12},
                {"feature": "Đơn giá & Giá trị sản phẩm", "value": features_dict.get("product_price", 0) * 0.05},
            ]
            factors = sorted(factors, key=lambda x: x["value"], reverse=True)
            total = sum(f["value"] for f in factors) or 1
            top_factors = [
                {"feature": f["feature"], "share": min(95, max(15, round((f["value"] / total) * 100)))}
                for f in factors[:3]
            ]
        else:
            top_factors = [
                {"feature": "Số ngày giao dự kiến", "share": 50},
                {"feature": "Không có thiên tai", "share": 30},
                {"feature": "Lịch sử giao nhận ổn định", "share": 20}
            ]

        safety_stock = max(1, round(ensemble_pred * 1.5))
        
        return {
            'success': True,
            'message': 'Dự báo thành công',
            'risk_level': risk_level,
            'risk_label': risk_label,
            'xgboost': {
                'delay_days': round(xgb_pred, 1)
            },
            'lstm': {
                'delay_days': round(lstm_pred, 1) if lstm_pred > 0 else None
            },
            'top_factors': top_factors,
            'safety_stock_days': safety_stock
        }
    except Exception as e:
        print(f"Error in perform_prediction: {str(e)}")
        print(traceback.format_exc())
        return {
            'success': False,
            'message': f'Lỗi hệ thống dự báo: {str(e)}',
            'error': str(e),
            'xgboost': {'delay_days': 0},
            'lstm': {'delay_days': 0},
            'risk_level': 'low',
            'risk_label': 'Lỗi dự báo',
            'top_factors': [],
            'safety_stock_days': 0
        }
