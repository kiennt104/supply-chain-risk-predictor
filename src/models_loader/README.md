# 📥 Models Loader (Thành phần quản lý tài nguyên mô hình AI)

Phân hệ đảm nhiệm tải tải song song và lưu trữ các tệp nhị phân nạp từ bộ nhớ vật lý lên bộ nhớ RAM hệ thống.

---

## 📄 Kiến trúc hoạt động của `loader.py`

- **Sử dụng cơ chế Đóng gói an toàn (Class-Based Structuring)**: Toàn bộ quá trình tải mô hình được gói gọn trong thực thể `ModelsLoader`.
- **Chương trình phòng vệ (Robust Skippers)**: 
  - Do thư viện học sâu `TensorFlow` thường rất nặng và có khả năng xung đột cao trên môi trường Windows mặc định, `loader.py` áp dụng kỹ thuật kiểm tra và chặn lỗi import (`TF_AVAILABLE`). 
  - Nếu TensorFlow bị vô hiệu hóa trên toàn cục hoặc chưa được cấu hình, hệ thống sẽ bỏ qua LSTM và chuyển hẳn sang sử dụng XGBoost làm bộ dự án đơn lẻ trung tâm mà không làm đứng hay sập tiến trình khởi động của Flask Webserver.
