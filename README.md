# Module Đối Chiếu Biển Số Xe (RFID vs Camera OCR)

Hệ thống so sánh và đánh giá độ tương đồng giữa thông tin biển số xe lưu trong thẻ RFID (ground truth) và biển số xe nhận diện qua Camera OCR tại các trạm thu phí / bãi đỗ xe thông minh.

Sử dụng thuật toán **Weighted Levenshtein Distance (Wagner–Fischer)** kết hợp kỹ thuật **Truy vết ngược (Backtracking)** để phân loại mức độ phạt thông minh và không bị lệch hàng khi camera đọc thiếu hoặc thừa ký tự.

---

## 🌟 Tính Năng Nổi Bật

- **Phạt thông minh theo hình dạng ký tự:** Các lỗi nhận diện do hình dạng tương tự ($8 \leftrightarrow B$, $0 \leftrightarrow O$, $1 \leftrightarrow I$, $5 \leftrightarrow S$...) bị phạt nhẹ hơn rất nhiều so với các lỗi sai khác hoàn toàn ($X \leftrightarrow B$).
- **Không xô lệch hàng khi thiếu/thừa ký tự:** Sử dụng ma trận quy hoạch động (DP) và truy vết ngược để chỉ ra chính xác vị trí ký tự bị thiếu/thừa mà không báo lỗi dây chuyền sang các ký tự phía sau.
- **RESTful API chuẩn hóa:** Đóng gói bằng FastAPI, hỗ trợ test tương tác trực tiếp qua Swagger UI.
- **Vị trí ký tự thân thiện:** Đánh số vị trí ký tự bắt đầu từ 1, dễ dàng tích hợp và hiển thị cho người vận hành/bảo vệ.

---

## 📁 Cấu Trúc Dự Án

```text
đối chiếu biển số xe/
├── core/                        # Package thuật toán lõi
│   ├── __init__.py              # Khởi tạo package core
│   ├── config.py                # Ma trận chi phí nhầm lẫn & cấu hình ngưỡng phạt
│   ├── models.py                # Định nghĩa Dataclass & Enum LoaiThaoTac
│   ├── distance.py              # Thuật toán Weighted Levenshtein & Backtracking
│   └── matcher.py               # Tiền xử lý chuỗi & tính điểm tương đồng
├── api.py                       # REST API Server (FastAPI)
├── benchmark.py                 # Script chạy kiểm thử 100 test case
├── benchmark_ket_qua.xlsx       # Báo cáo kết quả benchmark chi tiết
├── requirements.txt             # Danh sách thư viện phụ thuộc
└── README.md                    # Tài liệu hướng dẫn dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### 1. Yêu cầu hệ thống
- Python 3.10 trở lên.

### 2. Cài đặt thư viện phụ thuộc
Mở terminal tại thư mục dự án và chạy:
```bash
pip install fastapi uvicorn openpyxl
```
*(Hoặc `pip install -r requirements.txt` nếu có file requirements.txt)*

### 3. Khởi động API Server
```bash
uvicorn api:app --reload --port 8000
```
Server sẽ chạy tại địa chỉ: `http://localhost:8000`

### 4. Kiểm thử giao diện Swagger UI
Truy cập trực tiếp trên trình duyệt web:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 📡 Tài Liệu API

### Endpoint: `POST /so-sanh`

#### 1. Request Body (JSON)
```json
{
  "bien_so_rfid": "29-B1 224.56",
  "bien_so_camera": "29-81 234.66"
}
```

#### 2. Response Body (JSON)
```json
{
  "bien_so_rfid": "29-B1 224.56",
  "bien_so_camera": "29-81 234.66",
  "rfid_chuan_hoa": "29B122456",
  "camera_chuan_hoa": "298123466",
  "chi_phi_phat": 1.5,
  "do_chinh_xac": 0.8333,
  "so_loi": 3,
  "chi_tiet_loi": [
    {
      "loai": "THAY_THẾ",
      "vi_tri_rfid": 3,
      "vi_tri_camera": 3,
      "ky_tu_rfid": "B",
      "ky_tu_camera": "8",
      "chi_phi": 0.2
    },
    {
      "loai": "THAY_THẾ",
      "vi_tri_rfid": 6,
      "vi_tri_camera": 6,
      "ky_tu_rfid": "2",
      "ky_tu_camera": "3",
      "chi_phi": 1.0
    },
    {
      "loai": "THAY_THẾ",
      "vi_tri_rfid": 8,
      "vi_tri_camera": 8,
      "ky_tu_rfid": "5",
      "ky_tu_camera": "6",
      "chi_phi": 0.3
    }
  ]
}
```

#### 3. Test nhanh bằng `curl`
```bash
curl -X POST http://localhost:8000/so-sanh \
  -H "Content-Type: application/json" \
  -d "{\"bien_so_rfid\": \"29-B1 234.56\", \"bien_so_camera\": \"29-81 234.56\"}"
```

---

## 📊 Chạy Benchmark Đánh Giá
Dự án có sẵn script mô phỏng 100 tình huống camera đọc biển số và tự động xuất ra file Excel:

```bash
python benchmark.py
```
Kết quả được lưu tại: `benchmark_ket_qua.xlsx`