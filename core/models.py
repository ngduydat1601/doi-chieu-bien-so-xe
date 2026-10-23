"""Các kiểu dữ liệu dùng chung trong module."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class LoaiThaoTac(Enum):
    """Loại thao tác trong alignment."""
    KHOP = "KHỚP"
    THAY_THE = "THAY_THẾ"
    XOA = "XÓA"
    CHEN = "CHÈN"


@dataclass
class ThaoTac:
    """Một thao tác trong chuỗi alignment."""
    loai: LoaiThaoTac
    vi_tri_rfid: int        # -1 nếu là CHÈN
    vi_tri_camera: int      # -1 nếu là XÓA
    ky_tu_rfid: str         # "" nếu là CHÈN
    ky_tu_camera: str       # "" nếu là XÓA
    chi_phi: float


@dataclass
class KetQuaSoSanh:
    """Kết quả so sánh giữa biển số RFID và biển số camera."""
    bien_so_rfid: str
    bien_so_camera: str
    rfid_chuan_hoa: str
    camera_chuan_hoa: str
    khoang_cach: float
    diem_tuong_dong: float
    cac_thao_tac: List[ThaoTac] # Alignment đầy đủ
    cac_loi: List[ThaoTac]      # Chỉ các bước sai (không KHỚP)