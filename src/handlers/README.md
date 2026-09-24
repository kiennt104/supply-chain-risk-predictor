# ⚙️ Business Handlers (Bộ xử lý đặc trưng & Dự báo cốt lõi)

Thư mục này chịu trách nhiệm trực tiếp thu nhận thông số biểu mẫu từ giao diện người dùng, làm sạch, biến đổi chúng thành các vectơ toán học và tiến hành tích hợp mô hình dự báo.

---

## 📄 Danh sách tệp tin nghiệp vụ

### 1. `features.py` (Lớp xử lý và làm giàu đặc trưng)
- **Trích xuất thuộc tính chu kỳ ngày tháng (`extract_date_features`)**: Nghiệm pháp sử dụng hàm lượng giác tuần hoàn Sine/Cosine biểu diễn thuộc tính của Ngày phát sinh yêu cầu (`month_sin`, `month_cos`, `dow_sin`, `dow_cos`). Việc này đảm bảo máy học nhận diện đúng tính chất liên mạch xoay vòng của thời gian (ví dụ: tháng 12 đứng sát cạnh tháng 1).
- **Giả lập thông số nghẽn Localized (`prepare_features`)**: Căn cứ vào trạng thái thông suốt của tuyến đường do người dùng khai báo, hệ thống tự động tính toán và phun các giá trị dồn ứ trung bình trượt (rolling metrics 1d, 3d, 5d) thích ứng hoàn hảo với bộ quy chuẩn của tập dữ liệu huấn luyện cơ sở.

### 2. `predictor.py` (Bộ dự báo phối hợp Ensemble Engine)
- **Chuẩn bị vectơ shape khớp song song**:
  - **XGBoost**: Tự động dải đều vectơ đặc trưng đầu vào thành một mảng chính xác **196 cột** khớp tuyệt đối với đầu ra huấn luyện của mô hình cây quyết định (`feature_names_in_`).
  - **LSTM**: Chuyển đổi dữ liệu chuỗi số 31 chiều qua bộ chuẩn hóa `MinMaxScaler` và nhân rộng thành cấu trúc chuỗi thời gian ba chiều có hình dạng **`(1, 30, 31)`** đại diện cho chuỗi liên mạch 30 bước quan sát tuần tự.
- **Biện pháp dung hòa kết quả**: Nếu tiến trình giải mã LSTM bị gián đoạn, hệ thống thông minh tự động dự phòng lấy tiến trình XGBoost làm kết quả dự toán trung tâm, đảm bảo độ chịu lỗi của dự án đạt mức tối đa.
