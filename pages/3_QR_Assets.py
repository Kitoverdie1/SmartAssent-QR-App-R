import streamlit as st
import pandas as pd
from pathlib import Path
from auth import require_login, logout_button

EXCEL_PATH = "Smart Asset Lab.xlsx"
QR_DIR = Path("qrcodes")
QR_PDF_PATH = Path("qr_labels_A4_pages.pdf")

@st.cache_data
def load_assets(path: str) -> pd.DataFrame:
    excel_file = Path(path)
    if not excel_file.exists():
        return pd.DataFrame()
    df = pd.read_excel(excel_file).dropna(how="all").reset_index(drop=True)
    return df

def list_qr_files():
    if not QR_DIR.exists():
        return []
    return sorted(QR_DIR.glob("*.png"))

# ------------------ Auth & Page config ------------------
st.set_page_config(page_title="QR Assets", page_icon="🔍", layout="wide")
require_login()
logout_button()

# ------------------ CSS ------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }
    .hero-box {
        background: linear-gradient(135deg, #0D47A1, #1976D2);
        padding: 18px 24px;
        border-radius: 18px;
        color: #E3F2FD;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.45);
        margin-bottom: 18px;
    }
    .hero-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .hero-sub {
        font-size: 14px;
        opacity: 0.90;
    }
    .qr-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 14px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
        margin-bottom: 10px;
    }
    .qr-filename {
        font-size: 13px;
        color: #374151;
        font-weight: 600;
    }
    .qr-sub {
        font-size: 12px;
        color: #6B7280;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ Load data ------------------
assets_df = load_assets(EXCEL_PATH)
qr_files = list_qr_files()

st.markdown(
    """
<div class="hero-box">
  <div class="hero-title">QR Assets</div>
  <div class="hero-sub">ตรวจสอบ & ดาวน์โหลด QR Code สำหรับติดครุภัณฑ์</div>
</div>
""",
    unsafe_allow_html=True,
)

# ปุ่มดาวน์โหลด PDF ฉลาก A4
col_pdf, _ = st.columns([1, 3])
with col_pdf:
    if QR_PDF_PATH.exists():
        with open(QR_PDF_PATH, "rb") as f:
            st.download_button(
                "📄 ดาวน์โหลดแผ่นฉลาก QR (A4 3×8)",
                data=f,
                file_name=QR_PDF_PATH.name,
                mime="application/pdf",
            )
    else:
        st.info("เมื่อสร้างไฟล์ฉลาก A4 แล้ว จะมีปุ่มให้ดาวน์โหลดที่นี่ (qr_labels_A4_pages.pdf)")

st.markdown("---")

# ------------------ Filters ------------------
left, right = st.columns([1, 2])

with left:
    search_text = st.text_input("ค้นหาครุภัณฑ์ / รหัส / AssetID", "")

    status_col = None
    for c in assets_df.columns:
        if "สถานะ" in str(c):
            status_col = c
            break

    if not assets_df.empty and status_col:
        status_filter = st.multiselect(
            "กรองตามสถานะ",
            options=sorted(assets_df[status_col].dropna().unique()),
            default=[],
        )
    else:
        status_filter = []

    dept_col = None
    for c in assets_df.columns:
        if "หน่วยงาน" in str(c) or "แผนก" in str(c):
            dept_col = c
            break

    if not assets_df.empty and dept_col:
        dept_filter = st.multiselect(
            "กรองตามหน่วยงาน",
            options=sorted(assets_df[dept_col].dropna().unique()),
            default=[],
        )
    else:
        dept_filter = []

with right:
    if assets_df.empty:
        st.warning("ไม่พบไฟล์ Smart Asset Lab.xlsx หรือข้อมูลว่าง")
    else:
        df_filtered = assets_df.copy()

        if search_text:
            s = search_text.lower()
            df_filtered = df_filtered[
                df_filtered.apply(lambda r: s in str(r).lower(), axis=1)
            ]

        if status_col and status_filter:
            df_filtered = df_filtered[df_filtered[status_col].isin(status_filter)]

        if dept_col and dept_filter:
            df_filtered = df_filtered[df_filtered[dept_col].isin(dept_filter)]

        st.subheader("ตารางข้อมูลครุภัณฑ์ (เชื่อมกับ QR)")
        st.dataframe(df_filtered, use_container_width=True)

st.markdown("---")

# ------------------ แสดงไฟล์ QR Code ------------------
st.subheader("รายการไฟล์ QR Code ในโฟลเดอร์ `qrcodes/`")

if not qr_files:
    st.info("ยังไม่พบไฟล์ .png ในโฟลเดอร์ `qrcodes/` กรุณาสร้าง QR ด้วยสคริปต์ `build_pages_and_qr.py` ก่อน")
else:
    cols = st.columns(4)
    for idx, qr_path in enumerate(qr_files):
        col = cols[idx % 4]
        with col:
            st.markdown('<div class="qr-card">', unsafe_allow_html=True)
            st.image(str(qr_path), use_container_width=True)
            filename = qr_path.name
            stem = qr_path.stem
            st.markdown(f'<div class="qr-filename">{stem}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="qr-sub">ไฟล์: {filename}</div>', unsafe_allow_html=True)

            with open(qr_path, "rb") as f:
                st.download_button(
                    "⬇️ ดาวน์โหลด",
                    data=f,
                    file_name=filename,
                    key=f"dl_{stem}",
                    use_container_width=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
