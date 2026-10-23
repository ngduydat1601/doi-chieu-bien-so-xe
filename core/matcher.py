"""
Hàm chính: so sánh biển số xe RFID vs Camera OCR.

File này mỏng — chỉ điều phối luồng:
chuẩn hóa → tính DP → truy vết → đánh giá → trả kết quả.
"""

from .distance import tinh_ma_tran_dp, truy_vet
from .models import KetQuaSoSanh, LoaiThaoTac


def chuan_hoa_bien_so(bien_so: str) -> str:
    """Chuẩn hóa chuỗi biển số: bỏ ký tự đặc biệt, viết hoa."""
    return "".join(ch.upper() for ch in bien_so if ch.isalnum())


def so_sanh_bien_so(bien_so_rfid: str, bien_so_camera: str) -> KetQuaSoSanh:
    """So sánh và đánh giá 2 biển số xe.

    Args:
        bien_so_rfid: Biển số từ thẻ RFID (ground truth).
        bien_so_camera: Biển số từ camera nhận diện.

    Returns:
        KetQuaSoSanh chứa kết quả đánh giá và alignment chi tiết.
    """
    # Chuẩn hóa
    rfid_chuan = chuan_hoa_bien_so(bien_so_rfid)
    camera_chuan = chuan_hoa_bien_so(bien_so_camera)

    # Tính ma trận DP + truy vết
    dp = tinh_ma_tran_dp(rfid_chuan, camera_chuan)
    khoang_cach = dp[len(rfid_chuan)][len(camera_chuan)]
    cac_thao_tac = truy_vet(rfid_chuan, camera_chuan, dp)

    # Tính điểm tương đồng
    do_dai_max = max(len(rfid_chuan), len(camera_chuan))
    if do_dai_max == 0:
        diem = 1.0
    else:
        diem = max(0.0, min(1.0, 1.0 - khoang_cach / do_dai_max))

    # Lọc lỗi
    cac_loi = [t for t in cac_thao_tac if t.loai != LoaiThaoTac.KHOP]

    return KetQuaSoSanh(
        bien_so_rfid=bien_so_rfid,
        bien_so_camera=bien_so_camera,
        rfid_chuan_hoa=rfid_chuan,
        camera_chuan_hoa=camera_chuan,
        khoang_cach=round(khoang_cach, 4),
        diem_tuong_dong=round(diem, 4),
        cac_thao_tac=cac_thao_tac,
        cac_loi=cac_loi,
    )