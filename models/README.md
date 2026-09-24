# 🧠 Models Binaries (Kho trọng số học máy và chuẩn hóa)

Nơi lưu trữ các mô hình sau khi qua giai đoạn đào tạo (training), sẵn sàng cho tiến trình ước toán thời gian thực (inference).

---

## 📄 Chi tiết các tài nguyên AI hiện có

1. **`lstm_delay_model.keras`**: Mô hình mạng hồi quy tuần tự sâu 3 lớp LSTM giúp nắm bắt các quy luật suy diễn của chuỗi thời gian thực.
2. **`xgboost_delay_model.joblib`**: Mô hình rừng phân nhánh tăng cường cực kỳ chuẩn xác cho phân tích dữ liệu dạng bảng có cấu trúc lớn.
3. **`scaler_delay.joblib`**: Đối tượng chuẩn hóa dữ liệu số về phân vùng truyền tuyến tính của mạng học sâu.

*Lưu ý: Bạn không nên chỉnh sửa hoặc thay đổi tên các tệp nhị phân này để công cụ ModelsLoader tự động liên kết thành công.*
