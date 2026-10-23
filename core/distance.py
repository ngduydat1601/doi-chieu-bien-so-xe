"""
Thuật toán Weighted Levenshtein Distance + Backtracking.

Gồm 2 bước:
  1. Tính ma trận DP (quy hoạch động)
  2. Truy vết ngược để tìm alignment tối ưu (dùng math.isclose để an toàn)
"""

import math
from typing import List

from .config import BANG_TRA_CHI_PHI, CHI_PHI_CHEN, CHI_PHI_MAC_DINH, CHI_PHI_XOA
from .models import LoaiThaoTac, ThaoTac


def lay_chi_phi_thay_the(ky_tu_1: str, ky_tu_2: str) -> float:
    """Tra cứu chi phí thay thế giữa 2 ký tự."""
    if ky_tu_1 == ky_tu_2:
        return 0.0
    return BANG_TRA_CHI_PHI.get((ky_tu_1, ky_tu_2), CHI_PHI_MAC_DINH)


def tinh_ma_tran_dp(chuoi_1: str, chuoi_2: str) -> List[List[float]]:
    """Tính ma trận DP cho Weighted Levenshtein.

    Args:
        chuoi_1: Chuỗi nguồn (RFID).
        chuoi_2: Chuỗi đích (camera).

    Returns:
        Ma trận dp kích thước (len(chuoi_1)+1) x (len(chuoi_2)+1).
        Giá trị dp[m][n] chính là khoảng cách weighted Levenshtein.
    """
    do_dai_1 = len(chuoi_1)
    do_dai_2 = len(chuoi_2)

    dp = [[0.0] * (do_dai_2 + 1) for _ in range(do_dai_1 + 1)]

    for j in range(1, do_dai_2 + 1):
        dp[0][j] = dp[0][j - 1] + CHI_PHI_CHEN
    for i in range(1, do_dai_1 + 1):
        dp[i][0] = dp[i - 1][0] + CHI_PHI_XOA

    for i in range(1, do_dai_1 + 1):
        for j in range(1, do_dai_2 + 1):
            dp[i][j] = min(
                dp[i-1][j-1] + lay_chi_phi_thay_the(chuoi_1[i-1], chuoi_2[j-1]),
                dp[i-1][j] + CHI_PHI_XOA,
                dp[i][j-1] + CHI_PHI_CHEN,
            )

    return dp


def truy_vet(
    chuoi_rfid: str,
    chuoi_camera: str,
    dp: List[List[float]],
) -> List[ThaoTac]:
    """Truy vết ngược từ ma trận DP để tìm chuỗi thao tác tối ưu.

    Đi từ dp[m][n] ngược về dp[0][0], tại mỗi bước xác định
    thao tác nào đã được chọn bằng so sánh float an toàn.

    Returns:
        Danh sách ThaoTac theo thứ tự từ trái sang phải.
    """
    cac_thao_tac = []
    i = len(chuoi_rfid)
    j = len(chuoi_camera)

    while i > 0 or j > 0:
        if i > 0 and j > 0:
            gia_tri = dp[i][j]
            chi_phi_thay = lay_chi_phi_thay_the(chuoi_rfid[i-1], chuoi_camera[j-1])
            
            tu_cheo = dp[i-1][j-1] + chi_phi_thay
            tu_tren = dp[i-1][j] + CHI_PHI_XOA
            tu_trai = dp[i][j-1] + CHI_PHI_CHEN

            # Ưu tiên: chéo (khớp/thay thế) > trên (xóa) > trái (chèn)
            if math.isclose(gia_tri, tu_cheo, abs_tol=1e-9):
                if chuoi_rfid[i-1] == chuoi_camera[j-1]:
                    loai = LoaiThaoTac.KHOP
                    cp = 0.0
                else:
                    loai = LoaiThaoTac.THAY_THE
                    cp = chi_phi_thay

                cac_thao_tac.append(ThaoTac(
                    loai=loai,
                    vi_tri_rfid=i - 1,
                    vi_tri_camera=j - 1,
                    ky_tu_rfid=chuoi_rfid[i-1],
                    ky_tu_camera=chuoi_camera[j-1],
                    chi_phi=cp,
                ))
                i -= 1
                j -= 1

            elif math.isclose(gia_tri, tu_tren, abs_tol=1e-9):
                cac_thao_tac.append(ThaoTac(
                    loai=LoaiThaoTac.XOA,
                    vi_tri_rfid=i - 1,
                    vi_tri_camera=-1,
                    ky_tu_rfid=chuoi_rfid[i-1],
                    ky_tu_camera="",
                    chi_phi=CHI_PHI_XOA,
                ))
                i -= 1

            elif math.isclose(gia_tri, tu_trai, abs_tol=1e-9):
                cac_thao_tac.append(ThaoTac(
                    loai=LoaiThaoTac.CHEN,
                    vi_tri_rfid=-1,
                    vi_tri_camera=j - 1,
                    ky_tu_rfid="",
                    ky_tu_camera=chuoi_camera[j-1],
                    chi_phi=CHI_PHI_CHEN,
                ))
                j -= 1
            else:
                raise ValueError("Bị gãy logic truy vết DP! Kiểm tra lại cấu hình trọng số phạt.")

        elif i > 0:
            cac_thao_tac.append(ThaoTac(
                loai=LoaiThaoTac.XOA,
                vi_tri_rfid=i - 1,
                vi_tri_camera=-1,
                ky_tu_rfid=chuoi_rfid[i-1],
                ky_tu_camera="",
                chi_phi=CHI_PHI_XOA,
            ))
            i -= 1

        else:
            cac_thao_tac.append(ThaoTac(
                loai=LoaiThaoTac.CHEN,
                vi_tri_rfid=-1,
                vi_tri_camera=j - 1,
                ky_tu_rfid="",
                ky_tu_camera=chuoi_camera[j-1],
                chi_phi=CHI_PHI_CHEN,
            ))
            j -= 1

    cac_thao_tac.reverse()
    return cac_thao_tac