import os
import random
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import mimetypes
mimetypes.add_type('text/css', '.css')

# Insert 'src' into python search path to enable unified structured imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from config import Config
from models_loader.loader import ModelsLoader
from handlers.features import prepare_features
from handlers.predictor import perform_prediction

import pandas as pd

test_df_global = None
try:
    test_filepath = 'dataset/test_dataset.csv'
    if os.path.exists(test_filepath):
        test_df_global = pd.read_csv(test_filepath)
        print(f"✓ Test dataset loaded successfully: {test_df_global.shape[0]} rows")
    else:
        print("⚠ Test dataset not found at dataset/test_dataset.csv")
except Exception as e:
    print(f"⚠ Failed to load test dataset: {e}")

app = Flask(__name__)
app.config.from_object(Config)

# Initialize modular ModelsLoader
loader = ModelsLoader()
loader.load_all_models()

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template(
        'index.html', 
        today=today, 
        model_ready=loader.model_ready, 
        options=Config.FALLBACK_OPTIONS, 
        automotive_map=Config.AUTOMOTIVE_MAP,
        test_avail=(test_df_global is not None)
    )

@app.route('/api/random-test-order', methods=['GET'])
def get_random_test_order():
    """Lấy ngẫu nhiên 1 hàng từ file test_dataset.csv để tự động điền thử lý thuyết thực tế"""
    global test_df_global
    if test_df_global is None:
        return jsonify({'success': False, 'message': 'Dataset test chưa được kết nối.'}), 400
        
    try:
        idx = random.randint(0, len(test_df_global) - 1)
        row = test_df_global.iloc[idx].fillna("").to_dict()
        
        cat = row.get('category_name', 'Fishing')
        auto_product_name = Config.AUTOMOTIVE_MAP['categories'].get(cat, 'Cảm biến & Phụ tùng ô tô phụ thuộc (Dynamic OEM Component)')
        
        raw_price = float(row.get('product_price', row.get('order_item_product_price', 100.0)))
        raw_qty = int(row.get('order_item_quantity', 1))
        shipping_days_sched = int(row.get('shipping_days_scheduled', 4))
        
        auto_metrics = Config.map_numeric_to_automotive(raw_price, raw_qty, shipping_days_sched, cat)
        
        form_data = {
            'order_date': str(row.get('order_date', '')).split(' ')[0],
            'shipping_days_scheduled': shipping_days_sched,
            'shipping_mode': row.get('shipping_mode', 'Standard Class'),
            'market': row.get('market', 'Europe'),
            'order_region': row.get('order_region', 'Western Europe'),
            'customer_segment': row.get('customer_segment', 'Consumer'),
            'department_name': row.get('department_name', 'Fan Shop'),
            'category_name': row.get('category_name', 'Fishing'),
            'product_name_real': auto_product_name,
            'order_item_quantity': raw_qty,
            'product_price': round(raw_price, 2),
            'discount_rate': round(float(row.get('order_item_discount_rate', 0)) * 100),
            
            'auto_unit_price': auto_metrics['auto_unit_price'],
            'auto_total_value': auto_metrics['auto_total_value'],
            'pack_type': auto_metrics['pack_type'],
            'auto_qty': auto_metrics['auto_qty'],
            'qty_unit': auto_metrics['qty_unit'],
            'contract_type': auto_metrics['contract_type'],
            'actual_carrier_route': auto_metrics['actual_carrier_route'],
            
            'order_id_real': int(row.get('order_id', 0)),
            'shipping_days_real': int(row.get('shipping_days_real', 0)),
            'raw_delay_days_real': int(row.get('raw_delay_days', 0)),
            'delay_days_real': float(row.get('delay_days', 0.0)),
            'disaster_exposed_real': 1 if str(row.get('disaster_exposed', '0')).strip().lower() == 'true' else 0,
            'active_disaster_count_real': float(row.get('active_disaster_count', 0) or 0),

            'known_disaster_count_real': float(row.get('known_disaster_count', 0) or 0),
            'current_max_disaster_magnitude_real': float(row.get('current_max_disaster_magnitude', 0) or 0),
            'current_max_affected_real': float(row.get('current_max_affected', 0) or 0),
            'current_max_deaths_real': float(row.get('current_max_deaths', 0) or 0),
            'disaster_count_real': float(row.get('disaster_count', 0) or 0),
            'max_disaster_magnitude_real': float(row.get('max_disaster_magnitude', 0) or 0),
            'customer_disaster_country_real': str(row.get('customer_disaster_country_iso', '') or ''),
            'supplier_disaster_country_real': str(row.get('supplier_disaster_country_iso', '') or ''),
            'exposure_start_real': str(row.get('exposure_start', '') or ''),
            'exposure_end_real': str(row.get('exposure_end', '') or ''),
            
            'avg_delay_1d': float(row.get('avg_delay_1d', 0)),
            'avg_delay_2d': float(row.get('avg_delay_2d', 0)),
            'avg_delay_3d': float(row.get('avg_delay_3d', 0)),
            'avg_delay_5d': float(row.get('avg_delay_5d', 0)),
            'late_rate_1d': float(row.get('late_rate_1d', 0)),
            'late_rate_2d': float(row.get('late_rate_2d', 0)),
            'late_rate_3d': float(row.get('late_rate_3d', 0)),
            'late_rate_5d': float(row.get('late_rate_5d', 0)),
            'order_volume_1d': float(row.get('order_volume_1d', 0)),
            'order_volume_2d': float(row.get('order_volume_2d', 0)),
            'order_volume_3d': float(row.get('order_volume_3d', 0)),
            'order_volume_5d': float(row.get('order_volume_5d', 0)),
        }
        
        return jsonify({'success': True, 'data': form_data})
    except Exception as e:
        print(f"Error drawing random test order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Truy vấn danh sách đơn hàng thực tế kèm phân tích chi tiết thảm họa (Gom nhóm theo Order ID)"""
    global test_df_global
    if test_df_global is None:
        return jsonify({'success': False, 'message': 'Dataset không khả dụng.'}), 400

    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(1, min(100, int(request.args.get('per_page', 10))))
        hazard_filter = request.args.get('hazard_filter', 'all') # 'all', 'disaster', 'none'
        search = request.args.get('search', '').strip().lower()

        df_filtered = test_df_global.copy()

        if hazard_filter == 'disaster':
            df_filtered = df_filtered[df_filtered['disaster_exposed'].astype(str).str.strip().str.lower() == 'true']
        elif hazard_filter == 'none':
            df_filtered = df_filtered[df_filtered['disaster_exposed'].astype(str).str.strip().str.lower() != 'true']

        if search:
            mask = (
                df_filtered['order_id'].astype(str).str.contains(search) |
                df_filtered['product_name'].astype(str).str.lower().str.contains(search) |
                df_filtered['customer_city'].astype(str).str.lower().str.contains(search) |
                df_filtered['order_city'].astype(str).str.lower().str.contains(search) |
                df_filtered['category_name'].astype(str).str.lower().str.contains(search)
            )
            df_filtered = df_filtered[mask]

        if df_filtered.empty:
            return jsonify({
                'success': True,
                'orders': [],
                'page': page,
                'per_page': per_page,
                'total_records': 0,
                'total_pages': 0
            })

        grouped = df_filtered.groupby('order_id', sort=False)
        
        unique_order_ids = list(grouped.groups.keys())
        total_records = len(unique_order_ids)
        total_pages = (total_records + per_page - 1) // per_page

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        order_ids_slice = unique_order_ids[start_idx:end_idx]

        orders_list = []
        for order_id in order_ids_slice:
            df_order_sub = grouped.get_group(order_id)
            
            first_row = df_order_sub.iloc[0].fillna("").to_dict()
            
            products = []
            total_sales = 0.0
            
            for sub_idx, row in df_order_sub.iterrows():
                row_dict = row.fillna("").to_dict()
                
                cat = row_dict.get('category_name', 'Fishing')
                dept = row_dict.get('department_name', 'Fan Shop')
                auto_product = Config.AUTOMOTIVE_MAP['categories'].get(cat, 'Phụ tùng OEM chất lượng cao')
                
                raw_p = float(row_dict.get('product_price', row_dict.get('order_item_product_price', 100.0)))
                raw_q = int(row_dict.get('order_item_quantity', 1))
                days_sched = int(row_dict.get('shipping_days_scheduled', 4))
                
                auto_metrics = Config.map_numeric_to_automotive(raw_p, raw_q, days_sched, cat)
                sales_val = float(row_dict.get('sales', 0.0))
                total_sales += sales_val
                
                products.append({
                    'row_index': sub_idx,
                    'product_name': auto_product,
                    'product_name_original': str(row_dict.get('product_name', '') or ''),
                    'category_name': cat,
                    'department_name': dept,
                    'order_item_quantity': raw_q,
                    'sales': sales_val,
                    'product_price': raw_p,
                    'auto_metrics': auto_metrics,
                    
                    'avg_delay_1d': float(row_dict.get('avg_delay_1d', 0)),
                    'avg_delay_2d': float(row_dict.get('avg_delay_2d', 0)),
                    'avg_delay_3d': float(row_dict.get('avg_delay_3d', 0)),
                    'avg_delay_5d': float(row_dict.get('avg_delay_5d', 0)),
                    'late_rate_1d': float(row_dict.get('late_rate_1d', 0)),
                    'late_rate_2d': float(row_dict.get('late_rate_2d', 0)),
                    'late_rate_3d': float(row_dict.get('late_rate_3d', 0)),
                    'late_rate_5d': float(row_dict.get('late_rate_5d', 0)),
                    'order_volume_1d': float(row_dict.get('order_volume_1d', 0)),
                    'order_volume_2d': float(row_dict.get('order_volume_2d', 0)),
                    'order_volume_3d': float(row_dict.get('order_volume_3d', 0)),
                    'order_volume_5d': float(row_dict.get('order_volume_5d', 0)),
                })
            
            disaster_exposed_val = str(first_row.get('disaster_exposed', '0')).strip().lower() == 'true'
            disaster_count = int(float(first_row.get('disaster_count', 0) or 0))
            
            disasters = []
            if disaster_exposed_val and disaster_count > 0:
                cust_iso = str(first_row.get('customer_disaster_country_iso', '') or '').strip()
                supp_iso = str(first_row.get('supplier_disaster_country_iso', '') or '').strip()
                deaths = int(float(first_row.get('max_total_deaths', 0) or 0))
                affected = int(float(first_row.get('max_total_affected', 0) or 0))
                mag = float(first_row.get('max_disaster_magnitude', 0) or 0)
                
                if supp_iso and supp_iso != '0' and supp_iso != '':
                    country_names = {
                        'BRA': 'Brazil (Dòng chảy linh kiện gầm vỏ)',
                        'GBR': 'Vương Quốc Anh (Cụm truyền động trung tâm)',
                        'FRA': 'Pháp (Mạch điều hành cơ điện)',
                        'DEU': 'Đức (Trục truyền động truyền lực chính)',
                        'ITA': 'Ý (Vòng bi moay-ơ và phanh cơ cấu)',
                        'ESP': 'Tây Ban Nha (Cảm biến xúc tác khí thải)',
                        'NLD': 'Hà Lan (Cực trung chuyển linh kiện)',
                        'BEL': 'Bỉ (Rơ-le điện nguồn)',
                        'AUT': 'Áo (Trục bánh sau chịu lực)',
                        'IRL': 'Ireland (Cáp dẫn truyền tín hiệu ECU)',
                        'PRT': 'Bồ Đào Nha (Hệ thống sấy kính)',
                        'SWE': 'Thụy Điển (Kính chắn cường lực)'
                    }
                    c_name = country_names.get(supp_iso, supp_iso)
                    disasters.append({
                        'name': 'Mưa lũ cực đoan phát hủy hạ tầng sản xuất' if supp_iso == 'BRA' else 'Sự cố khí hậu gây phong tỏa cảng biển quốc tế',
                        'location': c_name,
                        'role': 'Trung tâm Nhà cung ứng (Supplier Source)',
                        'magnitude': f"{mag:,.2f}" if mag > 0 else 'N/A',
                        'deaths': f"{deaths:,}" if deaths > 0 else '0',
                        'affected': f"{affected:,}" if affected > 0 else '0',
                        'impact': 'Đình trệ cơ cấu đóng gói và lưu kho linh kiện, làm tăng nguy cơ chậm trễ lịch trình vận tải.'
                    })
                
                if cust_iso and cust_iso != '0' and cust_iso != '':
                    disasters.append({
                        'name': 'Bão nhiệt đới gây lụt ngập cục bộ hạ tầng' if cust_iso == 'PRI' else 'Siêu bão xáo động bưu chính & phân phối cục bộ',
                        'location': 'Puerto Rico' if cust_iso == 'PRI' else 'Hoa Kỳ (USA)',
                        'role': 'Thị trường Khách hàng (Customer End)',
                        'magnitude': f"{mag:,.2f}" if (mag > 0 and len(disasters) == 0) else 'N/A',
                        'deaths': f"{deaths:,}" if (deaths > 0 and len(disasters) == 0) else '0',
                        'affected': f"{affected:,}" if (affected > 0 and len(disasters) == 0) else '0',
                        'impact': 'Tê liệt dịch vụ bưu chính nội địa vùng tiêu thụ, phong tỏa giao nhận logistics chặng cuối.'
                    })
                    
                if len(disasters) < disaster_count:
                    diff = disaster_count - len(disasters)
                    for i in range(diff):
                        disasters.append({
                            'name': f'Áp lực kép: Tắc nghẽn mạng lưới cảng biển trung chuyển quốc tế (Compounding Incident #{i+1})',
                            'location': 'Không phận liên đại dương / Hub trung gian',
                            'role': 'Đầu mối Hải lộ sầm uất (Global Sea Lanes)',
                            'magnitude': 'N/A',
                            'deaths': '0',
                            'affected': 'N/A',
                            'impact': f'Sự cố dây chuyền từ {disaster_count} biến động ngoại cảnh gây mất cân bằng trọng tải logistics tàu biển.'
                        })

            orders_list.append({
                'order_id': int(order_id),
                'order_date': str(first_row.get('order_date', '')).split(' ')[0],
                'customer_city': str(first_row.get('customer_city', '') or ''),
                'customer_country': str(first_row.get('customer_country', '') or ''),
                'order_city': str(first_row.get('order_city', '') or ''),
                'order_country': str(first_row.get('order_country', '') or ''),
                'shipping_mode': str(first_row.get('shipping_mode', '') or ''),
                'market': str(first_row.get('market', '') or ''),
                'order_region': str(first_row.get('order_region', '') or ''),
                'customer_segment': str(first_row.get('customer_segment', '') or ''),
                
                'shipping_days_real': int(first_row.get('shipping_days_real', 0)),
                'shipping_days_scheduled': int(days_sched),
                'raw_delay_days_real': int(first_row.get('raw_delay_days', 0)),
                'delay_days_real': float(first_row.get('delay_days', 0.0)),
                
                'disaster_exposed_real': 1 if disaster_exposed_val else 0,
                'active_disaster_count_real': float(first_row.get('active_disaster_count', 0) or 0),
                'known_disaster_count_real': float(first_row.get('known_disaster_count', 0) or 0),
                'current_max_disaster_magnitude_real': float(first_row.get('current_max_disaster_magnitude', 0) or 0),
                'current_max_affected_real': float(first_row.get('current_max_affected', 0) or 0),
                'current_max_deaths_real': float(first_row.get('current_max_deaths', 0) or 0),
                'disaster_count_real': float(disaster_count),
                'max_disaster_magnitude_real': float(first_row.get('max_disaster_magnitude', 0) or 0),
                'customer_disaster_country_real': str(first_row.get('customer_disaster_country_iso', '') or ''),
                'supplier_disaster_country_real': str(first_row.get('supplier_disaster_country_iso', '') or ''),
                'exposure_start_real': str(first_row.get('exposure_start', '') or ''),
                'exposure_end_real': str(first_row.get('exposure_end', '') or ''),
                'pre_order_disaster_exposure': disaster_exposed_val,
                'active_disaster_exposure': str(first_row.get('active_disaster_exposure', '0')).strip().lower() == 'true',
                
                'products': products,
                'total_sales': total_sales,
                'disasters': disasters,
            })

        return jsonify({
            'success': True,
            'orders': orders_list,
            'page': page,
            'per_page': per_page,
            'total_records': total_records,
            'total_pages': total_pages
        })
    except Exception as e:
        print(f"Lỗi truy vấn dữ liệu đơn hàng: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        print(f"Lỗi truy vấn dữ liệu đơn hàng: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        features = prepare_features(data)
        result = perform_prediction(features, loader)
        
        cat_val = data.get("category_name", "")
        dept_val = data.get("department_name", "")
        
        raw_price = float(data.get("product_price", 100))
        raw_qty = int(data.get("order_item_quantity", 1))
        shipping_days_sched = int(data.get("shipping_days_scheduled", 4))
        
        auto_metrics = Config.map_numeric_to_automotive(raw_price, raw_qty, shipping_days_sched, cat_val)
        
        result["mapped_category"] = Config.AUTOMOTIVE_MAP["categories"].get(cat_val, cat_val)
        result["mapped_department"] = Config.AUTOMOTIVE_MAP["departments"].get(dept_val, dept_val)
        
        result["auto_metrics"] = auto_metrics
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi máy chủ: {str(e)}', 'delay_days': 0, 'risk_level': 'unknown', 'risk_score': 0}), 500

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'model_ready': loader.model_ready, 
        'error_message': loader.error_message, 
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/options', methods=['GET'])
def get_options():
    return jsonify(Config.FALLBACK_OPTIONS)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print('AutoChain AI - Delivery Delay Risk Prediction System')
    print(f'Starting server on {Config.HOST}:{Config.PORT}')
    print(f'Open browser at: http://{Config.HOST}:{Config.PORT}')
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.FLASK_DEBUG)
