"""
Script benchmark: Tạo 100 cặp biển số (RFID vs Camera) với các trường hợp
nhầm lẫn khác nhau, chạy qua module so sánh và xuất kết quả ra file .xlsx.

Cách chạy:
    cd "D:\Project\thực tập epass_viettel\đối chiếu biển số xe"
    pip install openpyxl
    python benchmark.py

Kết quả: File benchmark_ket_qua.xlsx sẽ được tạo trong cùng thư mục.
"""

import random
import sys
import os

# Thêm thư mục cha vào sys.path để import được package
thu_muc_cha = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if thu_muc_cha not in sys.path:
    sys.path.insert(0, thu_muc_cha)

# Lấy tên thư mục chứa code để import như package
ten_package = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Import từ package (dùng importlib để xử lý tên thư mục có dấu tiếng Việt)
import importlib
_pkg = importlib.import_module(ten_package)
_matcher = importlib.import_module(f"{ten_package}.matcher")
_distance = importlib.import_module(f"{ten_package}.distance")
_models = importlib.import_module(f"{ten_package}.models")

so_sanh_bien_so = _matcher.so_sanh_bien_so
lay_chi_phi_thay_the = _distance.lay_chi_phi_thay_the
LoaiThaoTac = _models.LoaiThaoTac


# ──────────────────────────────────────────────
# Phần 1: Sinh biển số xe ngẫu nhiên theo format Việt Nam
# ──────────────────────────────────────────────

# Danh sách mã tỉnh phổ biến
MA_TINH = [
    "11", "12", "14", "15", "17", "18", "19", "20",
    "21", "22", "24", "25", "26", "27", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38",
    "43", "47", "48", "49", "50", "51", "52", "54",
    "56", "58", "60", "61", "62", "63", "64", "65",
    "66", "67", "68", "69", "70", "71", "72", "73",
    "74", "75", "76", "77", "79", "81", "82", "83",
    "84", "85", "86", "88", "89", "90", "92", "93",
    "95", "97", "98", "99",
]

# Seri chữ cái phổ biến trên biển số xe máy
SERI_CHU = ["A", "B", "C", "D", "E", "F", "G", "H", "K", "L", "M", "N", "P", "R", "S", "T", "U", "V", "X", "Y", "Z"]


def sinh_bien_so_xe_may() -> str:
    """Sinh biển số xe máy ngẫu nhiên theo format: XXYZ NNNNN
    Ví dụ: 29B1 23456
    """
    ma_tinh = random.choice(MA_TINH)
    seri = random.choice(SERI_CHU) + str(random.randint(1, 9))
    so_cuoi = f"{random.randint(0, 99999):05d}"
    return f"{ma_tinh}{seri}{so_cuoi}"


# ──────────────────────────────────────────────
# Phần 2: Các hàm tạo lỗi giả lập camera OCR
# ──────────────────────────────────────────────

# Bảng các cặp ký tự dễ nhầm (dùng cho lỗi hình dạng giống)
NHAM_HINH_DANG_GIONG = {
    '0': 'O', 'O': '0',
    '1': 'I', 'I': '1',
    '2': 'Z', 'Z': '2',
    '5': 'S', 'S': '5',
    '6': 'G', 'G': '6',
    '8': 'B', 'B': '8',
    '9': 'P', 'P': '9',
    '4': 'A', 'A': '4',
    'D': 'O', 'Q': '0',
    'E': 'F', 'F': 'E',
    'M': 'N', 'N': 'M',
    'V': 'U', 'U': 'V',
    'K': 'X', 'X': 'K',
    'P': 'R', 'R': 'P',
}

# Tập ký tự cho lỗi ngẫu nhiên (hình dạng khác hẳn)
TAT_CA_KY_TU = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def tao_loi_khop_hoan_toan(bien_so: str) -> tuple[str, str]:
    """Trường hợp 1: Camera đọc đúng 100%."""
    return bien_so, "Khớp hoàn toàn"


def tao_loi_nham_1_ky_tu_giong(bien_so: str) -> tuple[str, str]:
    """Trường hợp 2: Camera nhầm 1 ký tự có hình dạng giống."""
    ds = list(bien_so)
    # Tìm vị trí có thể nhầm
    vi_tri_co_the = [i for i, ch in enumerate(ds) if ch in NHAM_HINH_DANG_GIONG]
    if not vi_tri_co_the:
        return bien_so, "Khớp hoàn toàn (không có ký tự dễ nhầm)"
    vi_tri = random.choice(vi_tri_co_the)
    ky_tu_goc = ds[vi_tri]
    ds[vi_tri] = NHAM_HINH_DANG_GIONG[ky_tu_goc]
    mo_ta = f"Nhầm hình dạng giống: {ky_tu_goc}→{ds[vi_tri]} (vị trí {vi_tri})"
    return "".join(ds), mo_ta


def tao_loi_nham_2_ky_tu_giong(bien_so: str) -> tuple[str, str]:
    """Trường hợp 3: Camera nhầm 2 ký tự có hình dạng giống."""
    ds = list(bien_so)
    vi_tri_co_the = [i for i, ch in enumerate(ds) if ch in NHAM_HINH_DANG_GIONG]
    if len(vi_tri_co_the) < 2:
        return tao_loi_nham_1_ky_tu_giong(bien_so)
    cac_vi_tri = random.sample(vi_tri_co_the, 2)
    mo_ta_parts = []
    for vi_tri in cac_vi_tri:
        ky_tu_goc = ds[vi_tri]
        ds[vi_tri] = NHAM_HINH_DANG_GIONG[ky_tu_goc]
        mo_ta_parts.append(f"{ky_tu_goc}→{ds[vi_tri]}")
    mo_ta = f"Nhầm 2 ký tự giống: {', '.join(mo_ta_parts)}"
    return "".join(ds), mo_ta


def tao_loi_nham_1_ky_tu_khac(bien_so: str) -> tuple[str, str]:
    """Trường hợp 4: Camera nhầm 1 ký tự có hình dạng khác hẳn."""
    ds = list(bien_so)
    vi_tri = random.randint(0, len(ds) - 1)
    ky_tu_goc = ds[vi_tri]
    # Chọn ký tự thay thế khác hẳn (không nằm trong bảng nhầm lẫn)
    ky_tu_moi = ky_tu_goc
    while ky_tu_moi == ky_tu_goc or ky_tu_moi == NHAM_HINH_DANG_GIONG.get(ky_tu_goc):
        ky_tu_moi = random.choice(TAT_CA_KY_TU)
    ds[vi_tri] = ky_tu_moi
    mo_ta = f"Nhầm hình dạng khác: {ky_tu_goc}→{ky_tu_moi} (vị trí {vi_tri})"
    return "".join(ds), mo_ta


def tao_loi_thieu_1_ky_tu(bien_so: str) -> tuple[str, str]:
    """Trường hợp 5: Camera đọc thiếu 1 ký tự."""
    vi_tri = random.randint(0, len(bien_so) - 1)
    ky_tu_mat = bien_so[vi_tri]
    ket_qua = bien_so[:vi_tri] + bien_so[vi_tri + 1:]
    mo_ta = f"Thiếu ký tự: {ky_tu_mat} (vị trí {vi_tri})"
    return ket_qua, mo_ta


def tao_loi_thua_1_ky_tu(bien_so: str) -> tuple[str, str]:
    """Trường hợp 6: Camera đọc thừa 1 ký tự."""
    vi_tri = random.randint(0, len(bien_so))
    ky_tu_thua = random.choice(TAT_CA_KY_TU)
    ket_qua = bien_so[:vi_tri] + ky_tu_thua + bien_so[vi_tri:]
    mo_ta = f"Thừa ký tự: +{ky_tu_thua} (vị trí {vi_tri})"
    return ket_qua, mo_ta


def tao_loi_thieu_2_ky_tu(bien_so: str) -> tuple[str, str]:
    """Trường hợp 7: Camera đọc thiếu 2 ký tự."""
    ds = list(bien_so)
    if len(ds) < 3:
        return tao_loi_thieu_1_ky_tu(bien_so)
    cac_vi_tri = sorted(random.sample(range(len(ds)), 2), reverse=True)
    ky_tu_mat = []
    for vi_tri in cac_vi_tri:
        ky_tu_mat.append(f"{ds[vi_tri]}(vị trí {vi_tri})")
        ds.pop(vi_tri)
    mo_ta = f"Thiếu 2 ký tự: {', '.join(reversed(ky_tu_mat))}"
    return "".join(ds), mo_ta


def tao_loi_ket_hop_thieu_va_nham(bien_so: str) -> tuple[str, str]:
    """Trường hợp 8: Camera vừa thiếu 1 ký tự vừa nhầm 1 ký tự giống."""
    # Bước 1: Xóa 1 ký tự
    vi_tri_xoa = random.randint(0, len(bien_so) - 1)
    ky_tu_mat = bien_so[vi_tri_xoa]
    ds = list(bien_so[:vi_tri_xoa] + bien_so[vi_tri_xoa + 1:])

    # Bước 2: Nhầm 1 ký tự giống
    vi_tri_co_the = [i for i, ch in enumerate(ds) if ch in NHAM_HINH_DANG_GIONG]
    mo_ta_nham = ""
    if vi_tri_co_the:
        vi_tri_nham = random.choice(vi_tri_co_the)
        ky_tu_goc = ds[vi_tri_nham]
        ds[vi_tri_nham] = NHAM_HINH_DANG_GIONG[ky_tu_goc]
        mo_ta_nham = f" + nhầm {ky_tu_goc}→{ds[vi_tri_nham]}"

    mo_ta = f"Thiếu {ky_tu_mat}(vị trí {vi_tri_xoa}){mo_ta_nham}"
    return "".join(ds), mo_ta


def tao_loi_hoan_toan_khac(bien_so: str) -> tuple[str, str]:
    """Trường hợp 9: Camera đọc ra biển số hoàn toàn khác (xe khác)."""
    bien_so_khac = sinh_bien_so_xe_may()
    # Đảm bảo biển số khác thực sự khác
    while bien_so_khac == bien_so:
        bien_so_khac = sinh_bien_so_xe_may()
    return bien_so_khac, "Biển số hoàn toàn khác (nghi xe khác)"


def tao_loi_nham_nhieu_ky_tu_khac(bien_so: str) -> tuple[str, str]:
    """Trường hợp 10: Camera nhầm 3+ ký tự hình dạng khác."""
    ds = list(bien_so)
    so_loi = random.randint(3, min(4, len(ds)))
    cac_vi_tri = random.sample(range(len(ds)), so_loi)
    mo_ta_parts = []
    for vi_tri in cac_vi_tri:
        ky_tu_goc = ds[vi_tri]
        ky_tu_moi = ky_tu_goc
        while ky_tu_moi == ky_tu_goc:
            ky_tu_moi = random.choice(TAT_CA_KY_TU)
        ds[vi_tri] = ky_tu_moi
        mo_ta_parts.append(f"{ky_tu_goc}→{ky_tu_moi}")
    mo_ta = f"Nhầm {so_loi} ký tự khác: {', '.join(mo_ta_parts)}"
    return "".join(ds), mo_ta


# ──────────────────────────────────────────────
# Phần 3: Phân bổ 100 test case theo tỷ lệ
# ──────────────────────────────────────────────

# (hàm tạo lỗi, số lượng test case)
PHAN_BO_TRUONG_HOP = [
    (tao_loi_khop_hoan_toan,           15),  # 15% khớp hoàn toàn
    (tao_loi_nham_1_ky_tu_giong,       20),  # 20% nhầm 1 chữ giống
    (tao_loi_nham_2_ky_tu_giong,       10),  # 10% nhầm 2 chữ giống
    (tao_loi_nham_1_ky_tu_khac,        10),  # 10% nhầm 1 chữ khác hẳn
    (tao_loi_thieu_1_ky_tu,            15),  # 15% thiếu 1 ký tự
    (tao_loi_thua_1_ky_tu,              5),  #  5% thừa 1 ký tự
    (tao_loi_thieu_2_ky_tu,             5),  #  5% thiếu 2 ký tự
    (tao_loi_ket_hop_thieu_va_nham,    10),  # 10% kết hợp thiếu + nhầm
    (tao_loi_hoan_toan_khac,            5),  #  5% hoàn toàn khác
    (tao_loi_nham_nhieu_ky_tu_khac,     5),  #  5% nhầm 3+ ký tự khác
]


def tao_du_lieu_benchmark() -> list[dict]:
    """Tạo 100 cặp dữ liệu benchmark."""
    ket_qua = []
    stt = 1

    for ham_tao_loi, so_luong in PHAN_BO_TRUONG_HOP:
        for _ in range(so_luong):
            # Sinh biển số RFID gốc
            bien_so_rfid = sinh_bien_so_xe_may()

            # Tạo biển số camera (có lỗi)
            bien_so_camera, mo_ta_loi = ham_tao_loi(bien_so_rfid)

            # Chạy thuật toán so sánh
            kq = so_sanh_bien_so(bien_so_rfid, bien_so_camera)

            # Tạo chuỗi mô tả alignment chi tiết
            chi_tiet_parts = []
            for t in kq.cac_thao_tac:
                if t.loai == LoaiThaoTac.KHOP:
                    chi_tiet_parts.append(f"{t.ky_tu_rfid}={t.ky_tu_camera}")
                elif t.loai == LoaiThaoTac.THAY_THE:
                    chi_tiet_parts.append(f"{t.ky_tu_rfid}→{t.ky_tu_camera}({t.chi_phi})")
                elif t.loai == LoaiThaoTac.XOA:
                    chi_tiet_parts.append(f"{t.ky_tu_rfid}→∅(xóa)")
                elif t.loai == LoaiThaoTac.CHEN:
                    chi_tiet_parts.append(f"∅→{t.ky_tu_camera}(chèn)")

            ket_qua.append({
                "stt": stt,
                "bien_so_rfid": kq.rfid_chuan_hoa,
                "bien_so_camera": kq.camera_chuan_hoa,
                "loai_loi": mo_ta_loi,
                "khoang_cach": kq.khoang_cach,
                "diem_tuong_dong": kq.diem_tuong_dong,
                "so_loi": len(kq.cac_loi),
                "chi_tiet_alignment": " | ".join(chi_tiet_parts),
            })
            stt += 1

    # Xáo trộn thứ tự để không bị nhóm theo loại lỗi
    random.shuffle(ket_qua)
    # Đánh lại số thứ tự
    for i, item in enumerate(ket_qua):
        item["stt"] = i + 1

    return ket_qua


# ──────────────────────────────────────────────
# Phần 4: Xuất ra file Excel (.xlsx)
# ──────────────────────────────────────────────

# Cấu hình các cột trong file Excel
CAU_HINH_COT = [
    ("STT",                "stt",               8),
    ("Biển số RFID",       "bien_so_rfid",     18),
    ("Biển số Camera",     "bien_so_camera",   18),
    ("Loại lỗi",           "loai_loi",         45),
    ("Chi phí phạt",       "khoang_cach",      14),
    ("Độ chính xác",       "diem_tuong_dong",  14),
    ("Số lỗi",             "so_loi",           10),
    ("Chi tiết Alignment", "chi_tiet_alignment", 70),
]

# Màu sắc
MAU_HEADER = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
MAU_DONG_CHAN = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
MAU_DONG_LE = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
FONT_HEADER = Font(name="Arial", size=11, bold=True, color="FFFFFF")
FONT_NOI_DUNG = Font(name="Arial", size=10)
VIEN = Border(
    left=Side(style="thin", color="B4C6E7"),
    right=Side(style="thin", color="B4C6E7"),
    top=Side(style="thin", color="B4C6E7"),
    bottom=Side(style="thin", color="B4C6E7"),
)


def xuat_excel(du_lieu: list[dict], duong_dan: str):
    """Xuất dữ liệu benchmark ra file Excel có định dạng đẹp."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Benchmark Biển Số Xe"

    # Tiêu đề tổng
    ws.merge_cells("A1:H1")
    cell_tieu_de = ws["A1"]
    cell_tieu_de.value = "BENCHMARK SO SÁNH BIỂN SỐ XE — RFID vs Camera OCR"
    cell_tieu_de.font = Font(name="Arial", size=14, bold=True, color="2F5496")
    cell_tieu_de.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Dòng mô tả
    ws.merge_cells("A2:H2")
    cell_mo_ta = ws["A2"]
    cell_mo_ta.value = f"Tổng số test case: {len(du_lieu)} | Weighted Levenshtein Distance + Backtracking"
    cell_mo_ta.font = Font(name="Arial", size=10, italic=True, color="808080")
    cell_mo_ta.alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 20

    # Header
    dong_header = 4
    for col_idx, (ten_cot, _, do_rong) in enumerate(CAU_HINH_COT, start=1):
        cell = ws.cell(row=dong_header, column=col_idx, value=ten_cot)
        cell.font = FONT_HEADER
        cell.fill = MAU_HEADER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = VIEN
        # Đặt độ rộng cột
        ws.column_dimensions[chr(64 + col_idx)].width = do_rong

    ws.row_dimensions[dong_header].height = 25

    # Dữ liệu
    for row_idx, item in enumerate(du_lieu):
        dong = dong_header + 1 + row_idx
        mau_dong = MAU_DONG_CHAN if row_idx % 2 == 0 else MAU_DONG_LE

        for col_idx, (_, khoa, _) in enumerate(CAU_HINH_COT, start=1):
            gia_tri = item[khoa]

            # Định dạng giá trị đặc biệt
            if khoa == "diem_tuong_dong":
                cell = ws.cell(row=dong, column=col_idx, value=gia_tri)
                cell.number_format = '0.00%'
            elif khoa == "khoang_cach":
                cell = ws.cell(row=dong, column=col_idx, value=gia_tri)
                cell.number_format = '0.0000'
            else:
                cell = ws.cell(row=dong, column=col_idx, value=gia_tri)

            cell.font = FONT_NOI_DUNG
            cell.fill = mau_dong
            cell.border = VIEN

            # Căn giữa cho các cột số
            if khoa in ("stt", "khoang_cach", "diem_tuong_dong", "so_loi"):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(vertical="center", wrap_text=True)

    # Freeze pane
    ws.freeze_panes = f"A{dong_header + 1}"

    # AutoFilter
    ws.auto_filter.ref = f"A{dong_header}:H{dong_header + len(du_lieu)}"

    # Lưu file
    wb.save(duong_dan)
    print(f"✅ Đã xuất file: {duong_dan}")
    print(f"   Tổng: {len(du_lieu)} test case")


# ──────────────────────────────────────────────
# Phần 5: Chạy chính
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import io
    # Đảm bảo stdout hỗ trợ UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Seed cố định để tái tạo kết quả (bỏ dòng này nếu muốn ngẫu nhiên mỗi lần)
    random.seed(42)

    print("[1/3] Dang tao 100 test case benchmark...")
    du_lieu = tao_du_lieu_benchmark()

    # Đường dẫn xuất file
    thu_muc_hien_tai = os.path.dirname(os.path.abspath(__file__))
    duong_dan_xlsx = os.path.join(thu_muc_hien_tai, "benchmark_ket_qua.xlsx")

    print("[2/3] Dang xuat file Excel...")
    xuat_excel(du_lieu, duong_dan_xlsx)

    # In thống kê nhanh
    print("")
    print("[3/3] Thong ke nhanh:")
    diem_tb = sum(d['diem_tuong_dong'] for d in du_lieu) / len(du_lieu)
    cp_tb = sum(d['khoang_cach'] for d in du_lieu) / len(du_lieu)
    so_khop = sum(1 for d in du_lieu if d['khoang_cach'] == 0)
    so_loi = sum(1 for d in du_lieu if d['khoang_cach'] > 0)
    print(f"   Diem tuong dong trung binh: {diem_tb:.4f}")
    print(f"   Chi phi phat trung binh:    {cp_tb:.4f}")
    print(f"   So case khop hoan toan:     {so_khop}")
    print(f"   So case co loi:             {so_loi}")
