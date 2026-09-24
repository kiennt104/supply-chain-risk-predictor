# 🚀 Hướng Dẫn Cài Đặt Chi Tiết

## Prerequisites (Điều Kiện Tiên Quyết)

- **Python 3.8+** (khuyến nghị 3.10+)
  - Windows: Tải từ https://www.python.org/downloads/
  - Đảm bảo chọn "Add Python to PATH" khi cài đặt
- **pip** (đi kèm với Python)
- **Git** (tùy chọn, để clone repo)

## Bước 1: Chuẩn Bị Môi Trường

### Trên Windows (PowerShell):

```powershell
# Di chuyển vào thư mục project
cd c:\Users\trknguyen\Documents\3.UIT\IMP!_DATN\web_app

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\Activate.ps1
```

**Lưu ý**: Nếu gặp lỗi "execution of scripts is disabled", chạy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Bước 2: Cài Đặt Dependencies

```powershell
# Nâng cấp pip
python -m pip install --upgrade pip

# Cài đặt tất cả dependencies
pip install -r requirements.txt
```

## Bước 3: Chuẩn Bị Mô Hình

Tạo folder `models` nếu chưa có:
```powershell
mkdir models
```

Đặt các file mô hình vào folder này:
- `xgboost_delay_model.pkl` (bắt buộc)
- `sequence_scaler.pkl` (bắt buộc cho LSTM)
- `lstm_delay_model.keras` (tùy chọn)

**Nếu không có file mô hình**:
- Ứng dụng vẫn chạy được nhưng sẽ hiển thị thông báo "Mô hình chưa tải"
- Bạn vẫn có thể kiểm tra giao diện và API endpoints

## Bước 4: Chạy Ứng Dụng

```powershell
# Chắc chắn virtual environment đã được kích hoạt
python app.py
```

Output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

## Bước 5: Truy Cập Ứng Dụng

Mở trình duyệt web và truy cập:
- **URL**: http://127.0.0.1:5000
- **Port mặc định**: 5000
- Có thể thay đổi trong code `app.py` dòng cuối cùng

## Cấu Trúc Thư Mục Sau Cài Đặt

```
web_app/
├── .env.example              # Tệp cấu hình mẫu
├── .gitignore                # Git ignore patterns
├── App.py                     # Flask application
├── README.md                  # Tài liệu chính
├── SETUP.md                   # File này
├── requirements.txt           # Python dependencies
├── models/                    # Thư mục chứa mô hình
│   ├── xgboost_delay_model.pkl
│   ├── sequence_scaler.pkl
│   └── lstm_delay_model.keras
├── templates/                 # HTML templates
│   └── index.html
└── venv/                      # Virtual environment (được tạo tự động)
```

## Khắc Phục Sự Cố

### Lỗi: "ModuleNotFoundError: No module named 'flask'"

**Nguyên nhân**: Chưa cài đặt dependencies

**Giải pháp**:
```powershell
pip install -r requirements.txt
```

### Lỗi: "Port 5000 is already in use"

**Nguyên nhân**: Port 5000 đã được sử dụng bởi ứng dụng khác

**Giải pháp**: Sửa port trong `app.py`
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Đổi sang 5001
```

### Lỗi: "Models not found"

**Nguyên nhân**: Các file mô hình không tồn tại

**Giải pháp**: 
- Tạo folder `models` và thêm các file
- Hoặc bỏ qua nếu chỉ muốn test UI

### Lỗi: "tensorflow not installed"

**Giải pháp** (nếu LSTM không cần):
- Sửa `app.py` dòng 23-25 để bỏ qua lỗi TensorFlow
- Hoặc cài đặt: `pip install tensorflow`

## Tối Ưu Hóa (Optional)

### 1. Sử dụng Production Server

Thay Flask development server bằng Gunicorn:
```powershell
pip install gunicorn
gunicorn app:app --bind 127.0.0.1:5000
```

### 2. Thêm CORS (nếu cần gọi từ domain khác)

```powershell
pip install flask-cors
```

Thêm vào `app.py`:
```python
from flask_cors import CORS
CORS(app)
```

### 3. Logging

Thêm logging để debug:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Kiểm Tra Cài Đặt

Chạy script kiểm tra:
```powershell
python -c "import flask, pandas, numpy, xgboost, joblib; print('All dependencies OK!')"
```

## Hỗ Trợ Thêm

- **Flask Documentation**: https://flask.palletsprojects.com/
- **XGBoost Documentation**: https://xgboost.readthedocs.io/
- **TensorFlow/Keras**: https://www.tensorflow.org/
- **Pandas**: https://pandas.pydata.org/

## Tiếp Theo

Sau khi cài đặt thành công:
1. Đọc `README.md` để hiểu cấu trúc API
2. Mở `http://127.0.0.1:5000` để test giao diện
3. Kiểm tra các endpoint API trong `app.py`
4. Huấn luyện và thêm mô hình của bạn vào folder `models/`
