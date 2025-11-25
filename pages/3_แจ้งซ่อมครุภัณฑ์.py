# pages/3_แจ้งซ่อมครุภัณฑ์.py
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from auth import is_authed, logout_button

EXCEL_PATH = "Smart Asset Lab.xlsx"
REPAIR_SHEET_NAME = "Repairs"   # ชื่อชีตเก็บรายการแจ้งซ่อม

# -----------------------------
# ตั้งค่าหน้า
# -----------------------------
st.set_page_config(page_title="แจ้งซ่อมครุภัณฑ์", page_icon="🛠️", layout="wide")

if not is_authed():
    st.stop()

# แถบด้านบนขวา: ปุ่มออกจากระบบ
logout_button()

st.markdown("""
<style>
.page-title{
    font-size:32px;
    font-weight:700;
    margin-bottom:0;
}
.page-subtitle{
    color:#6b7280;
    margin-bottom:18px;
}
.card{
    background:#ffffff;
    border-radius:18px;
    padding:20px 24px;
    box-shadow:0 10px 25px rgba(15,23,42,0.06);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">แจ้งซ่อมครุภัณฑ์</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">บันทึกคำขอซ่อมครุภัณฑ์และติดตามสถานะได้จากระบบ</div>', unsafe_allow_html=True)

# -----------------------------
# 1) โหลดข้อมูลครุภัณฑ์จาก Excel
# -----------------------------
excel_file = Path(EXCEL_PATH)
if not excel_file.exists():
    st.error(f"ไม่พบไฟล์ Excel: {EXCEL_PATH}")
    st.stop()

# ชีตหลักสมมติเป็นชีตแรก (เหมือนที่คุณใช้หน้าอื่น)
assets_df = pd.read_excel(EXCEL_PATH, sheet_name=0).dropna(how="all").reset_index(drop=True)

# หา column รหัส + ชื่อ ให้ยืดหยุ่นกับหลายแบบชื่อคอลัมน์
code_col = None
for c in ["รหัสเครื่องมือห้องปฏิบัติการ", "AssetID", "รหัสครุภัณฑ์"]:
    if c in assets_df.columns:
        code_col = c
        break

name_col = None
for c in ["ชื่อ", "ชื่อครุภัณฑ์", "รายการครุภัณฑ์"]:
    if c in assets_df.columns:
        name_col = c
        break

if code_col is None:
    st.error("ไม่พบคอลัมน์รหัสครุภัณฑ์ (เช่น 'รหัสเครื่องมือห้องปฏิบัติการ' หรือ 'AssetID')")
    st.stop()

if name_col is None:
    # ถ้าไม่มีชื่อ ให้สร้างคอลัมน์ว่าง ๆ ไว้
    assets_df["ชื่อครุภัณฑ์_ชั่วคราว"] = ""
    name_col = "ชื่อครุภัณฑ์_ชั่วคราว"

# -----------------------------
# 2) โหลดข้อมูลแจ้งซ่อมเดิม (ถ้ามี)
# -----------------------------
try:
    repairs_df = pd.read_excel(EXCEL_PATH, sheet_name=REPAIR_SHEET_NAME).dropna(how="all")
except ValueError:
    # ยังไม่มีชีต Repairs
    repairs_df = pd.DataFrame(columns=[
        "repair_id",
        "asset_code",
        "asset_name",
        "problem_detail",
        "reporter_name",
        "reporter_phone",
        "report_date",
        "created_at",
        "status"
    ])

# -----------------------------
# 3) UI หลัก: ฟอร์มแจ้งซ่อม + ตารางประวัติ
# -----------------------------
col_form, col_history = st.columns([1.2, 1.8])

with col_form:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ฟอร์มแจ้งซ่อม")

    # เตรียม options สำหรับ selectbox
    display_options = [
        f"{row[code_col]} - {row[name_col]}"
        for _, row in assets_df.iterrows()
    ]
    selected_display = st.selectbox(
        "เลือกครุภัณฑ์ที่ต้องการแจ้งซ่อม",
        options=display_options,
        index=0 if display_options else None
    )

    report_date = st.date_input("วันที่แจ้งซ่อม", value=datetime.today())
    problem_detail = st.text_area("อาการ / รายละเอียดปัญหา", height=120)

    reporter_name = st.text_input("ชื่อผู้แจ้ง")
    reporter_phone = st.text_input("เบอร์โทรติดต่อ")

    submit = st.button("บันทึกคำขอแจ้งซ่อม", type="primary")

    if submit:
        if not selected_display or not problem_detail.strip():
            st.warning("กรุณาเลือกครุภัณฑ์และกรอกรายละเอียดปัญหาให้ครบถ้วน")
        else:
            asset_code = selected_display.split(" - ")[0].strip()
            # หา asset name จาก df
            asset_row = assets_df.loc[assets_df[code_col] == asset_code].iloc[0]
            asset_name = str(asset_row[name_col])

            new_row = {
                "repair_id": f"R{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "asset_code": asset_code,
                "asset_name": asset_name,
                "problem_detail": problem_detail.strip(),
                "reporter_name": reporter_name.strip(),
                "reporter_phone": reporter_phone.strip(),
                "report_date": report_date.strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "รอรับเรื่อง"
            }

            # ต่อท้ายเข้า DataFrame
            repairs_df = pd.concat([repairs_df, pd.DataFrame([new_row])],
                                   ignore_index=True)

            # เขียนกลับเข้า Excel แค่ชีต Repairs (ชีตอื่นยังอยู่)
            with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl",
                                mode="a", if_sheet_exists="replace") as writer:
                repairs_df.to_excel(writer, sheet_name=REPAIR_SHEET_NAME, index=False)

            st.success("✅ บันทึกคำขอแจ้งซ่อมเรียบร้อยแล้ว")

    st.markdown('</div>', unsafe_allow_html=True)

with col_history:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ประวัติการแจ้งซ่อมล่าสุด")

    if repairs_df.empty:
        st.info("ยังไม่มีรายการแจ้งซ่อม")
    else:
        show_cols = ["repair_id", "asset_code", "asset_name",
                     "problem_detail", "report_date", "status"]
        show_cols = [c for c in show_cols if c in repairs_df.columns]

        st.dataframe(
            repairs_df.sort_values("created_at", ascending=False)[show_cols].head(50),
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
