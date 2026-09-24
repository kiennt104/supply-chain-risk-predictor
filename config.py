"""
AutoChain AI - Configuration Module
Manages environment-specific settings and model/feature configurations.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '127.0.0.1')
    
    # Models Directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, os.getenv('MODELS_DIR', 'models'))
    
    # Model Files
    XGBOOST_MODEL_PATH = os.path.join(MODELS_DIR, 'xgboost_delay_model.pkl')
    SCALER_PATH = os.path.join(MODELS_DIR, 'sequence_scaler.pkl')
    LSTM_MODEL_PATH = os.path.join(MODELS_DIR, 'lstm_delay_model.keras')
    
    # Feature Configuration
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
    
    # Fallback Options (used when model is not available)
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
    
    # Risk Presets based on trend
    RISK_PRESETS = {
        "good": dict(avg_delay=0.3, late_rate=0.10, volume=15),
        "normal": dict(avg_delay=0.8, late_rate=0.28, volume=25),
        "bad": dict(avg_delay=2.0, late_rate=0.55, volume=40),
    }
    
    # Risk Thresholds
    RISK_LOW_THRESHOLD = 0.5
    RISK_MEDIUM_THRESHOLD = 1.5
    
    # Safety Stock Calculation
    SAFETY_STOCK_MULTIPLIER = 1.5
    SAFETY_STOCK_BASE = 1

    # Dynamic Semantic Automotive Mapping Layer
    AUTOMOTIVE_MAP = {
        "departments": {
            "Fan Shop": "Hệ thống Động cơ & Truyền chuyển động (Engine & Drivetrain)",
            "Apparel": "Hệ thống Nội thất & Khung thân vỏ (Cab Interior & Body Shell)",
            "Golf": "Thiết bị Điện tử & Hộp đen ECU (Electrical & ECU Modules)",
            "Footwear": "Hệ thống Treo & Trục bánh xe (Suspension & Wheel Assemblies)",
            "Fitness": "Khung gầm & Bộ giảm chấn lực (Chassis & Damper Elements)",
            "Outdoors": "Cơ cấu Truyền phanh & Thủy lực (Braking & Hydraulics Core)",
            "Technology": "Màn hình đa thông tin & ADAS (Sensor & ADAS Integration)",
            "Discs Shop": "Đĩa ly hợp & Cơ cấu truyền lực (Clutch Plates & Friction Discs)",
            "Book Store": "Sách hướng dẫn chuẩn hóa kỹ thuật SAE (Standardized SAE Manuals)",
            "Health and Beauty": "Hộp lọc khí & Điều hòa nhiệt độ Cabin (Cabin Filters & HVAC)",
            "Sports": "Hệ thống Lò xo & Trục truyền lực cơ cấu (Suspension Springs & Shafts)",
            "Toys": "Phụ kiện trang trí & Ốp trang trí (Aesthetic Cabin Trim Panels)",
        },
        "categories": {
            "Cleats": "Cùm kẹp phanh đĩa hiệu năng cao (Ceramic Disk Brake Calipers)",
            "Men's Footwear": "Lốp mâm đúc hợp kim gia cường tải trọng (All-terrain Radial Tires)",
            "Women's Apparel": "Hệ thống ghế bọc da chống cháy Ergo (Fire-retardant Leather Seats)",
            "Indoor/Outdoor Games": "Trục các-đăng truyền động đồng tốc (Constant Velocity CV Joints)",
            "Fishing": "Cảm biến oxy khí thải & Đo dòng nạp (O2 Sensor & MAF Sensors)",
            "Camping & Hiking": "Hệ thống treo khí nén chủ động (Adaptive Pneumatic Struts)",
            "Water Sports": "Thanh xoắn xi lanh trợ lực lái thủy lực (Torsion Bar & Steering Cylinder)",
            "Cardio Equipment": "Vỏ đầu máy block động cơ nhôm nguyên khối (Block Engine Heads)",
            "Boxing Gear": "Két làm mát tản nhiệt két nhôm bản rộng (Coolant Heat Radiators)",
            "Hunting & Shooting": "Bộ pít tông đúc hợp kim siêu nén (Forged Pistons & Rings)",
            "Accessories": "Gioăng cao su hộp số & Vòng đệm O-Ring (Transmission O-Rings)",
            "Asics Onitsuka Tiger": "Bánh đà ly hợp bù dao động lực kéo (Dual-mass Flywheels)",
            "Board Games": "Cơ cấu gương chiếu hậu gập điện sấy nhiệt (Side-view Heated Mirrors)",
            "Computers": "Bảng mạch trung tâm vi xử lý ECU (ECU Control Motherboard)",
            "Electronics": "Hộp cầu chì thông minh phân mạch tải (Smart Junction Fuse Box)",
            "Shop By Sport": "Bơm dầu bôi trơn trục cam cưỡng bức (Pressure Camshaft Oil Pumps)",
            "Sporting Goods": "Trục khuỷu động cơ gia tải tôi lực cơ (Tensile Crankshaft Rods)",
            "Girls' Apparel": "Tấm cách âm giảm chấn mút trần cabin (Ceiling Acoustic Dampers)",
            "Boys' Apparel": "Bộ thảm lót cao su dẻo nguyên sinh (Hydrophobic Rubber Liners)",
            "Men's Clothing": "Đai an toàn 3 điểm siết chủ động (Pre-tensioned Seat Belts)",
            "Women's Clothing": "Kính chắn gió nhiều lớp chống ồn UV (Laminated Acoustic Windshields)",
            "Cardio": "Cổ hút nạp khí giảm xóc cơ cấu truyền (Intake Exhaust Manifold)",
            "Air Sports": "Khối sấy khí nạp tăng áp Turbocharger (High-boost Turbochargers)",
            "Golf Balls": "Vòng bi côn moay-ơ bánh trước chính xác (Tapered Hub Bearings)",
            "Golf Bags": "Bình nhiên liệu bọc nhôm mạ niken (Alloy Coated Fuel Reserve)",
            "Golf Clubs": "Thanh rô-bốt cơ cấu lái ngoài (Steering Outer Tie Rods)",
            "Golf Apparel": "Vô lăng trợ lực điện tử bọc Alcantara (Electronic EPS Steering Wheel)",
            "Trade-In": "Cánh quạt làm mát kép tản nhiệt dầu (Dual Radiator Blowers)",
            "Tennis & Racquet": "Hộp số ly hợp kép truyền động 7 cấp (7-Speed Dual Clutch Gearbox)",
            "Hockey": "Khớp các-đăng liên kết trục cầu sau (Axle Propeller Couplers)",
            "Soccer": "Lá thép nhíp chịu tải bán tải hạng nặng (Reinforced Leaf Springs)",
            "Lacrosse": "Thanh cân bằng ngang chống vặn xoắn gầm (Chassis Anti-roll Sway Bars)",
            "Fitness Accessories": "Ống dẫn truyền dầu phanh lõi thép (Steel-braided Brake Hoses)",
            "Strength Training": "Bán trục dẫn động vi sai cầu trước (Differential Drive Shafts)",
            "Pet Supplies": "Bộ lọc gió điều hòa hoạt tính khử mùi (Active Carbon Filters)",
            "Crafts": "Keo gốc Polyurethane dán lắp ráp kính (Adhesive Glass Sealants)",
            "Garden": "Cụm van hằng nhiệt điều khiển nước làm mát (Thermostatic Coolant Valves)",
            "Baby": "Ghế trẻ em an toàn định vị ISOFIX (ISOFIX Anchorage Child Seats)",
            "Music": "Hệ thống loa dải âm kết nối điều phối (Infotainment Sound Array)",
            "DVDs": "Đầu cắm chuẩn đoán xe thông minh OBD-II (OBD-II Smart Interface)",
            "Cameras": "Hệ thống cảm biến đỗ xe & Camera 360 độ (Acoustic Sonar & 360 CAM)",
        }
    }

    # AUTOMOTIVE BUSINESS-METRIC TRANSLATION MATRIX
    # Maps retail constraints to realistic automotive quantities & values
    # e.g., low unit prices (~$10) are mapped to spare parts bulk boxes (Pack of 50/100) or high-grade components.
    # Scheduled days are aligned to global supply contract timelines (Intermodal ocean, CKD/SKD, Express Air Courier)
    # Quantity is mapped to Pack Sizes or Containerized pallets (Units per Batch)
    @staticmethod
    def map_numeric_to_automotive(raw_price, raw_qty, raw_days, doc_category):
        """
        Translates retail-oriented numbers to realistic automotive commercial variables.
        Keeps models happy while showing realistic numbers on UI.
        """
        # 1. Price Translation: Automotive single unit vs packaging size
        # If price is low, assume it represents a box of fast-moving spare parts (Pack of 50 screws/O-rings)
        # If price is high, it represents high-value parts like engine block or ECU motherboard.
        bulk_factor = 1
        pack_type = "Cá thể (Single Unit)"
        scaled_unit_price = raw_price
        
        if raw_price < 25:
            # Low price -> fast-moving parts packed in boxes of 100
            bulk_factor = 100
            scaled_unit_price = raw_price * 1.5
            pack_type = "Kiện hộp 100 linh kiện (Pack of 100)"
        elif raw_price < 100:
            # Mid price -> packaging of 10 unit components
            bulk_factor = 10
            scaled_unit_price = raw_price * 1.2
            pack_type = "Khay chống tĩnh điện 10 linh kiện (Tray of 10)"
        else:
            # High price -> valuable single component
            bulk_factor = 1
            scaled_unit_price = raw_price * 2.5 # Scale premium value
            pack_type = "Thùng chứa bảo vệ chuyên dụng (Single Protective Case)"
            
        automotive_price_per_item = scaled_unit_price
        automotive_total_value = scaled_unit_price * raw_qty
        
        # 2. Quantity Translation: Pallets or Container volume mapping
        # In automotive, we order in cargo pallets or shipping batches
        auto_quantity = raw_qty
        measurement_unit = "Cụm chi tiết (Modules)"
        if raw_qty > 5:
            measurement_unit = "Khay liên kết Pallet (Pallet Trays)"
            auto_quantity = max(1, int(raw_qty // 2))
        else:
            measurement_unit = "Thùng bảo ôn chuyên dụng (Crates)"
            
        # 3. Scheduled days mapping to Global Supply Chain Contract standards:
        # 0-2 days: "Express Air Freight - Hỏa tốc hàng không khẩn cấp (AOG)"
        # 3-5 days: "Fast Air Cargo - Vận chuyển hàng hải siêu tốc hoặc Hàng không tiêu chuẩn"
        # 6+ days: "Intermodal Maritime Freight - Vận tải thủy đa phương thức (Ocean CKD Container)"
        lead_time_classification = ""
        shipping_route = "Tuyến Logistics nội địa vùng"
        
        if raw_days <= 2:
            lead_time_classification = "Hợp đồng ưu tiên khẩn cấp Just-In-Time (JIT-AOG)"
            shipping_route = "Không vận khẩn cấp dải biên hàng không quốc tế"
        elif raw_days <= 5:
            lead_time_classification = "Hợp đồng Vận chuyển Tiêu chuẩn Tier-1 (Standard Contract)"
            shipping_route = "Vận tải Đa phương thức (Đường bộ liên tỉnh + Đường biển nhanh)"
        else:
            lead_time_classification = "Tuyến Vận chuyển Linh kiện Lắp ráp Rời lớn (CKD Ocean Freight)"
            shipping_route = "Hải trình Thủy nội địa / Vận tải Container Viễn dương"
            
        return {
            "auto_unit_price": round(automotive_price_per_item, 2),
            "auto_total_value": round(automotive_total_value, 2),
            "pack_type": pack_type,
            "auto_qty": auto_quantity,
            "qty_unit": measurement_unit,
            "contract_type": lead_time_classification,
            "actual_carrier_route": shipping_route,
            "bulk_factor": bulk_factor
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig


# Export active configuration
config = get_config()
