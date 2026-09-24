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

## ⚡ Khởi chạy nhanh (Một chạm trên Windows)

Hệ thống đã tự động cấu hóa môi trường Python an toàn tránh xung đột đa nền tảng. Bạn chỉ cần chạy hai file tự động hóa:
- **Khởi chạy Web App**: Double-click vào [**`run.bat`**](./run.bat) (hoặc tệp PowerShell [**`run.ps1`**](./run.ps1)).
- **Hướng dẫn triển khai chi tiết**: Tham khảo [**`SETUP.md`**](./SETUP.md).

---

## 💡 Đề xuất các VS Code Extension bổ trợ đọc dự án này

Để duyệt và đọc mã nguồn đồ án này mượt mà nhất, bạn nên cài đặt ngay các tiện ích mở rộng sau đây trong VS Code (bấm tổ hợp phím `Ctrl + Shift + X` để tìm kiếm và cài đặt):

1. **Python** (`ms-python.python`) & **Pylance** (`ms-python.vscode-pylance`): Bộ đôi phân tích cú pháp tĩnh siêu mạnh (giúp hết báo Warning giả).
2. **GitLens — Git supercharged** (`eamodio.gitlens`): Thuận tiện kiểm tra nhật ký lịch sử dòng code của đồ án.`
3. **Prettier - Code formatter** (`esbenp.prettier-vscode`): Định dạng HTML/CSS của giao diện Dashboard tự động cân chỉnh lề dòng.
4. **Graphviz Preview** (`joaompinto.vscode-graphviz`): Hỗ trợ trực quan hóa sơ đồ mối quan hệ thực thể nếu có viết mã biểu đồ.
5. **Path Autocomplete** (`ionutvmi.path-autocomplete`): Tự động điền nhanh đường dẫn tệp tin khi viết mã import/export.
