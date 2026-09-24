import numpy as np
import pandas as pd
from datetime import datetime
from config import Config

def extract_date_features(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        date = datetime.now()
    
    features = {
        'order_month': date.month,
        'order_dayofweek': date.weekday(),
        'order_dayofmonth': date.day,
        'order_weekofyear': date.isocalendar()[1],
    }
    
    features['month_sin'] = np.sin(2 * np.pi * features['order_month'] / 12)
    features['month_cos'] = np.cos(2 * np.pi * features['order_month'] / 12)
    features['dow_sin'] = np.sin(2 * np.pi * features['order_dayofweek'] / 7)
    features['dow_cos'] = np.cos(2 * np.pi * features['order_dayofweek'] / 7)
    
    return features

def prepare_features(form_data):
    features = {}
    
    # 1. Thu thập numeric features trực tiếp từ form
    for key in Config.NUMERIC_FEATURES:
        try:
            features[key] = float(form_data.get(key, 0))
        except:
            features[key] = 0.0
            
    # Thêm giá trị sales (doanh số = số lượng * giá)
    try:
        qty = float(form_data.get("order_item_quantity", 1))
        price = float(form_data.get("product_price", 0))
        features["sales"] = qty * price
    except:
        features["sales"] = 0.0
        
    # Giảm giá và tỉ lệ
    try:
        disc_rate = float(form_data.get("discount_rate", 0)) / 100.0
        features["order_item_discount_rate"] = disc_rate
        features["order_item_discount"] = features["sales"] * disc_rate
    except:
        features["order_item_discount_rate"] = 0.0
        features["order_item_discount"] = 0.0

    # 2. Xử lý kịch bản thiên tai REALTIME từ form
    is_disaster = form_data.get("disaster_toggle") == 'true' or form_data.get("disaster_toggle") == True
    if is_disaster:
        features["active_disaster_count"] = float(form_data.get("active_disaster_count_real", 1.0) or 1.0)
        features["known_disaster_count"] = float(form_data.get("known_disaster_count_real", 1.0) or 1.0)
        try:
            features["current_max_disaster_magnitude"] = float(form_data.get("disaster_magnitude", 5))
            features["current_max_affected"] = float(form_data.get("disaster_affected", 10000))
            features["current_max_deaths"] = float(form_data.get("disaster_deaths", 0))
        except:
            pass
    else:
        features["active_disaster_count"] = 0.0
        features["known_disaster_count"] = 0.0
        features["current_max_disaster_magnitude"] = 0.0
        features["current_max_affected"] = 0.0
        features["current_max_deaths"] = 0.0

        if "avg_delay_1d" in form_data and "late_rate_1d" in form_data:
            features["avg_delay_1d"] = float(form_data.get("avg_delay_1d", 0))
            features["avg_delay_2d"] = float(form_data.get("avg_delay_2d", 0))
            features["avg_delay_3d"] = float(form_data.get("avg_delay_3d", 0))
            features["avg_delay_5d"] = float(form_data.get("avg_delay_5d", 0))
            
            features["late_rate_1d"] = float(form_data.get("late_rate_1d", 0))
            features["late_rate_2d"] = float(form_data.get("late_rate_2d", 0))
            features["late_rate_3d"] = float(form_data.get("late_rate_3d", 0))
            features["late_rate_5d"] = float(form_data.get("late_rate_5d", 0))
            
            features["order_volume_1d"] = float(form_data.get("order_volume_1d", 0))
            features["order_volume_2d"] = float(form_data.get("order_volume_2d", 0))
            features["order_volume_3d"] = float(form_data.get("order_volume_3d", 0))
            features["order_volume_5d"] = float(form_data.get("order_volume_5d", 0))
        else:
            trend = form_data.get("trend", "normal")
            if trend == "good":
                features["avg_delay_1d"] = 0.1
                features["avg_delay_3d"] = 0.2
                features["avg_delay_5d"] = 0.2
                features["late_rate_1d"] = 0.05
                features["order_volume_3d"] = 2.0
            elif trend == "bad":
                features["avg_delay_1d"] = 3.5
                features["avg_delay_3d"] = 4.2
                features["avg_delay_5d"] = 3.8
                features["late_rate_1d"] = 0.75
                features["order_volume_3d"] = 45.0
            else:
                features["avg_delay_1d"] = 1.2
                features["avg_delay_3d"] = 1.4
                features["avg_delay_5d"] = 1.3
                features["late_rate_1d"] = 0.35
                features["order_volume_3d"] = 15.0

    # 4. Trích xuất các thuộc tính ngày tháng
    date_features = extract_date_features(form_data.get('order_date', datetime.now().strftime('%Y-%m-%d')))
    features.update(date_features)
    
    # 5. One-hot encoding các categorical features
    for category in Config.CATEGORY_BASES:
        value = form_data.get(category, '')
        for option in Config.FALLBACK_OPTIONS.get(category, []):
            features[f'{category}_{option}'] = 1.0 if value == option else 0.0
            
    return features
