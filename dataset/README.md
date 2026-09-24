# 📊 Dataset Sandbox (Kho lưu trữ dữ liệu kiểm nghiệm chuỗi thời gian)

Thư mục này chứa bộ dữ liệu mẫu thực tế, đóng vai trò bản lề cung cấp thông số đầu vào kiểm nghiệm hệ thống và phục vụ cho mục đích thực nghiệm chuỗi thời gian thực.

---

## 📄 Thống kê thông tin tệp tin

### `test_dataset.csv`
- **Số lượng bản ghi**: Hơn **27,078 dòng dữ liệu** lịch sử đơn hàng chuỗi cung ứng thực tế.
- **Mục đích sử dụng**: 
  - Phục vụ chức năng **"Ingest Live Telemetry Batch"** tại màn hình điều khiển.
  - Khi người dùng bấm kích hoạt, Webserver Flask sẽ truy xuất ngẫu nhiên một đơn hàng thực, tiến hành ánh xạ danh mục sang linh kiện ô tô (ví dụ: `Fishing` -> `Cùm phanh đĩa hiệu năng cao`).
  - Toàn bộ tham số số học thực của dòng đó bao gồm Ngày mua, Giá cả, Số lượng, các mốc trễ hạn thực tế và các chỉ số dồn ứ lịch sử (rolling delay)... sẽ được tự động điền trực quan vào form để kiểm định độ tiệm cận chính xác tuyệt vời giữa ước tính AI và ghi nhận thực tế.
