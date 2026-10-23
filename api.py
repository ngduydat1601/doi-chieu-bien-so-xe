"""
REST API cho module so sánh biển số xe RFID vs Camera OCR.

Chạy:
    cd "D:\\Project\\thực tập epass_viettel\\đối chiếu biển số xe"
    uvicorn api:app --reload --port 8000

Swagger UI:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

from core.matcher import so_sanh_bien_so


# ──────────────────────────────────────────────
# Khởi tạo ứng dụng FastAPI
# ──────────────────────────────────────────────

app = FastAPI(
    title="API Đối Chiếu Biển Số Xe",
    description=(
        "So sánh biển số xe giữa thẻ RFID và Camera OCR "
        "bằng thuật toán Weighted Levenshtein Distance + Backtracking."
    ),
    version="1.0.0",
)


# ──────────────────────────────────────────────
# Định nghĩa cấu trúc Request / Response
# ──────────────────────────────────────────────

class YeuCauSoSanh(BaseModel):
    """Đầu vào: 2 biển số cần so sánh."""

    bien_so_rfid: str = Field(
        ...,
        min_length=1,
        description="Biển số xe từ thẻ RFID (ground truth)",
        examples=["29-B1 234.56"],
    )
    bien_so_camera: str = Field(
        ...,
        description="Biển số xe từ camera OCR nhận diện",
        examples=["29-81 234.56"],
    )


class ThaoTacChiTiet(BaseModel):
    """Chi tiết 1 thao tác lỗi."""

    loai: str = Field(
        description="Loại thao tác lỗi: THAY_THẾ | XÓA | CHÈN"
    )
    vi_tri_rfid: int = Field(
        description="Vị trí trên chuỗi RFID (bắt đầu từ 1, -1 nếu là CHÈN)"
    )
    vi_tri_camera: int = Field(
        description="Vị trí trên chuỗi Camera (bắt đầu từ 1, -1 nếu là XÓA)"
    )
    ky_tu_rfid: str = Field(
        description='Ký tự RFID ("" nếu là CHÈN)'
    )
    ky_tu_camera: str = Field(
        description='Ký tự Camera ("" nếu là XÓA)'
    )
    chi_phi: float = Field(
        description="Chi phí phạt của thao tác này"
    )


class KetQuaResponse(BaseModel):
    """Đầu ra: Kết quả đối chiếu."""

    bien_so_rfid: str = Field(description="Biển số RFID gốc")
    bien_so_camera: str = Field(description="Biển số Camera gốc")
    rfid_chuan_hoa: str = Field(description="Biển số RFID sau chuẩn hóa")
    camera_chuan_hoa: str = Field(description="Biển số Camera sau chuẩn hóa")
    chi_phi_phat: float = Field(description="Tổng chi phí phạt (Weighted Levenshtein Distance)")
    do_chinh_xac: float = Field(description="Độ chính xác / Điểm tương đồng (0.0 ~ 1.0)")
    so_loi: int = Field(description="Số lỗi phát hiện được")
    chi_tiet_loi: List[ThaoTacChiTiet] = Field(
        description="Chỉ các thao tác sai (không bao gồm KHỚP)"
    )


# ──────────────────────────────────────────────
# Endpoint chính
# ──────────────────────────────────────────────

@app.post(
    "/so-sanh",
    response_model=KetQuaResponse,
    summary="So sánh biển số RFID vs Camera",
    description=(
        "Nhận vào biển số từ thẻ RFID và biển số từ camera OCR, "
        "trả về độ chính xác, chi phí phạt, số lỗi và chi tiết các lỗi."
    ),
)
def so_sanh(yeu_cau: YeuCauSoSanh) -> KetQuaResponse:
    """Endpoint chính: so sánh 2 biển số xe."""

    # Gọi module so sánh
    kq = so_sanh_bien_so(yeu_cau.bien_so_rfid, yeu_cau.bien_so_camera)

    # Chuyển đổi danh sách lỗi ThaoTac → ThaoTacChiTiet (vị trí đếm từ 1)
    def chuyen_thao_tac(t) -> ThaoTacChiTiet:
        return ThaoTacChiTiet(
            loai=t.loai.value,
            # Nếu vị trí != -1 (có ký tự) thì cộng thêm 1 để tính từ vị trí thứ 1
            vi_tri_rfid=t.vi_tri_rfid + 1 if t.vi_tri_rfid != -1 else -1,
            vi_tri_camera=t.vi_tri_camera + 1 if t.vi_tri_camera != -1 else -1,
            ky_tu_rfid=t.ky_tu_rfid,
            ky_tu_camera=t.ky_tu_camera,
            chi_phi=t.chi_phi,
        )

    return KetQuaResponse(
        bien_so_rfid=yeu_cau.bien_so_rfid,
        bien_so_camera=yeu_cau.bien_so_camera,
        rfid_chuan_hoa=kq.rfid_chuan_hoa,
        camera_chuan_hoa=kq.camera_chuan_hoa,
        chi_phi_phat=kq.khoang_cach,
        do_chinh_xac=kq.diem_tuong_dong,
        so_loi=len(kq.cac_loi),
        chi_tiet_loi=[chuyen_thao_tac(t) for t in kq.cac_loi],
    )


@app.get(
    "/health",
    summary="Kiểm tra trạng thái API",
)
def health_check():
    """Endpoint kiểm tra API còn sống không."""
    return {"status": "ok", "module": "doi-chieu-bien-so-xe", "version": "1.0.0"}