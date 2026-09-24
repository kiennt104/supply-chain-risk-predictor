# 📦 supply-chain-risk-predictor · Hệ thống Kiểm soát & Dự báo Rủi ro Chuỗi cung ứng Ô tô (GNN)

Ứng dụng Web dự báo thời gian trễ giao hàng và cảnh báo đứt gãy chuỗi cung ứng linh kiện ô tô (Automotive Logistics & Delay Forecasting System). Hệ thống sử dụng mô hình học máy phối hợp (Ensemble Setup) giữa bộ đại hồi quy **XGBoost Regressor** và kiến trúc mạng thần kinh hồi quy tuần tự **Long Short-Term Memory (LSTM)** nhằm đưa ra các kịch bản dự án thời gian thực.

---

## 📂 Tổ chức mã nguồn & Tài liệu chi tiết

Hệ thống được cấu trúc theo mô hình Modular hóa tối giản đạt tiêu chuẩn Enterprise nhằm tăng khả năng mở rộng và đơn giản hóa bảo trì. Bạn có thể bấm trực tiếp vào các liên kết thư mục dưới đây để xem tài liệu nghiệp vụ chi tiết của từng phân vùng:

1. [**`src/handlers/` (Bộ xử lý dữ liệu và đặc trưng)**](./src/handlers/README.md)
   - Nơi đóng gói logic trích xuất đặc trưng chuỗi thời gian bổ sung (`features.py`).
   - Lớp dự báo hợp nhất tính toán trọng số GNN (`predictor.py`).
2. [**`src/models_loader/` (Thành phần quản lý nạp mô hình)**](./src/models_loader/README.md)
   - Lớp trừu tượng hóa tiến trình tải cô lập các trọng số của LSTM & XGBoost (`loader.py`).
3. [**`dataset/` (Cơ sở dữ liệu thử nghiệm thời gian thực)**](./dataset/README.md)
   - Kho chứa mẫu kiểm định dữ liệu ô tô và lịch sử chu kỳ Logistics (`test_dataset.csv`).
4. [**`models/` (Bộ nhớ trọng số kiểm định AI)**](./models/README.md)
   - Lưu trữ các tệp nhị phân mô hình XGBoost (`.joblib`), LSTM (`.keras`) và MinMaxScaler scaler.

---

## ⚡ Khởi chạy nhanh trên local

Hệ thống đã tự động cấu hóa môi trường Python an toàn tránh xung đột đa nền tảng. Bạn chỉ cần chạy hai file tự động hóa:
- **Khởi chạy Web App**: Double-click vào [**`run.bat`**](./run.bat) (hoặc tệp PowerShell [**`run.ps1`**](./run.ps1)).
- **Hướng dẫn triển khai chi tiết**: Tham khảo [**`SETUP.md`**](./SETUP.md).
