import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime   # ✅ ใช้สร้างเลขที่แจ้งซ่อม / วันที่

EXCEL_PATH = "Smart Asset Lab.xlsx"
REPAIR_SHEET_NAME = "Repairs"   # ✅ ชีตเก็บข้อมูลแจ้งซ่อม

st.set_page_config(page_title="Asset Detail", page_icon="🔧", layout="wide")
st.title("🔧 รายละเอียดครุภัณฑ์ (จาก QR Code)")

# ================================
# 1) รับค่า code จาก URL
# ================================
try:
    # streamlit รุ่นใหม่
    query_params = st.query_params
except Exception:
    # streamlit รุ่นเก่า
    query_params = st.experimental_get_query_params()

if isinstance(query_params, dict):
    asset_code = query_params.get("code", [""])[0].strip()
else:
    asset_code = ""

if not asset_code:
    st.error("ไม่พบรหัสทรัพย์สิน (code=...) ใน URL")
    st.info("ตัวอย่างลิงก์ที่ถูกต้อง:  \n`...?code=LAB-AS-001`")
    st.stop()

st.caption(f"รหัสจาก URL: **{asset_code}**")

# ================================
# 2) โหลด Excel
# ================================
if not Path(EXCEL_PATH).exists():
    st.error(f"ไม่พบไฟล์ Excel: {EXCEL_PATH}")
    st.stop()

# ใช้ชีตแรกเป็นชีตหลักของครุภัณฑ์
xl = pd.ExcelFile(EXCEL_PATH)
MAIN_SHEET_NAME = xl.sheet_names[0]
df = xl.parse(MAIN_SHEET_NAME)

# ================================
# 3) หาเรคอร์ดที่ตรงกับ code
# ================================
id_cols = ["รหัสเครื่องมือห้องปฏิบัติการ", "AssetID", "รหัส", "รหัสครุภัณฑ์"]

def find_id_column(df):
    for col in id_cols:
        if col in df.columns:
            return col
    return None

IDCOL = find_id_column(df)

if IDCOL is None:
    st.error("ไม่พบคอลัมน์รหัสทรัพย์สินใน Excel")
    st.write("รองรับชื่อคอลัมน์:", id_cols)
    st.stop()

df[IDCOL] = df[IDCOL].astype(str).str.strip()
row = df[df[IDCOL] == asset_code]

if row.empty:
    st.error(f"ไม่พบทรัพย์สินรหัส `{asset_code}` ใน Excel")
    st.stop()

row_index = row.index[0]
row_data = row.iloc[0].to_dict()

# ชื่อครุภัณฑ์เอาไว้ใช้ในฟอร์มแจ้งซ่อม
asset_name = str(row_data.get("ชื่อ", ""))

st.success(f"พบข้อมูลของทรัพย์สิน: `{asset_code}`")

# ================================
# 4) Form แก้ไขข้อมูลครุภัณฑ์
# ================================
st.subheader("แก้ไขข้อมูลครุภัณฑ์")

with st.form("edit_form"):
    new_values = {}
    for col in df.columns:
        val = row_data.get(col, "")
        if pd.isna(val):
            val = ""
        new_values[col] = st.text_input(col, str(val))
    saved_asset = st.form_submit_button("💾 บันทึกข้อมูลครุภัณฑ์")

# ================================
# 5) บันทึกข้อมูลครุภัณฑ์กลับ Excel (เฉพาะชีตหลัก)
# ================================
if saved_asset:
    for col in df.columns:
        df.at[row_index, col] = new_values[col]

    # เขียนทับเฉพาะชีตหลัก โดยไม่ลบชีต Repairs
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl",
                        mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=MAIN_SHEET_NAME, index=False)

    st.success("บันทึกข้อมูลครุภัณฑ์สำเร็จ ✔")

st.markdown("---")

# ================================
# 6) ฟอร์มแจ้งซ่อมครุภัณฑ์นี้
# ================================
st.subheader("🛠️ แจ้งซ่อมครุภัณฑ์นี้")

st.info(
    "หากครุภัณฑ์รายการนี้มีปัญหา กรุณากรอกรายละเอียดด้านล่าง "
    "ระบบจะบันทึกข้อมูลไปที่ชีต **Repairs** ในไฟล์ Excel เดียวกัน\n"
    "และสามารถดู/จัดการได้จากหน้าเมนู **แจ้งซ่อมครุภัณฑ์** ใน Sidebar ของแอปหลักทันที"
)

# โหลดข้อมูลแจ้งซ่อมเดิม (ถ้ายังไม่มีชีต Repairs จะสร้าง DataFrame เปล่าให้)
try:
    repairs_df = pd.read_excel(EXCEL_PATH, sheet_name=REPAIR_SHEET_NAME).dropna(how="all")
except ValueError:
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

problem_detail = st.text_area("อาการ / รายละเอียดปัญหา", height=120)
reporter_name = st.text_input("ชื่อผู้แจ้งซ่อม")
reporter_phone = st.text_input("เบอร์โทรติดต่อ")
report_date = st.date_input("วันที่แจ้งซ่อม", value=datetime.today())

saved_repair = st.button("📨 บันทึกคำขอแจ้งซ่อมสำหรับครุภัณฑ์นี้")

if saved_repair:
    if not problem_detail.strip():
        st.warning("กรุณากรอกรายละเอียดปัญหาอย่างน้อย 1 บรรทัด")
    else:
        new_repair = {
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

        repairs_df = pd.concat(
            [repairs_df, pd.DataFrame([new_repair])],
            ignore_index=True
        )

        # เขียนทับเฉพาะชีต Repairs โดยไม่ลบชีตอื่น
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl",
                            mode="a", if_sheet_exists="replace") as writer:
            repairs_df.to_excel(writer, sheet_name=REPAIR_SHEET_NAME, index=False)

        st.success(
            "✅ บันทึกคำขอแจ้งซ่อมเรียบร้อยแล้ว!\n"
            "สามารถเปิดหน้า **แจ้งซ่อมครุภัณฑ์** ใน Sidebar ของแอปหลักเพื่อดูรายการนี้ได้ทันที"
        )
