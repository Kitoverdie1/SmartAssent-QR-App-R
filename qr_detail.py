import streamlit as st
import pandas as pd
from pathlib import Path

EXCEL_PATH = "Smart Asset Lab.xlsx"

st.set_page_config(page_title="Asset Detail", page_icon="🔧", layout="wide")
st.title("🔧 รายละเอียดครุภัณฑ์")

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

# ================================
# 2) โหลด Excel
# ================================
if not Path(EXCEL_PATH).exists():
    st.error(f"ไม่พบไฟล์ Excel: {EXCEL_PATH}")
    st.stop()

df = pd.read_excel(EXCEL_PATH)

# ================================
# 3) หาคอลัมน์รหัส
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

# ================================
# 4) หาเรคอร์ดที่ตรงกับ code
# ================================
df[IDCOL] = df[IDCOL].astype(str).str.strip()
row = df[df[IDCOL] == asset_code]

if row.empty:
    st.error(f"ไม่พบทรัพย์สินรหัส `{asset_code}` ใน Excel")
    st.stop()

row_index = row.index[0]
row_data = row.iloc[0].to_dict()

st.success(f"พบข้อมูลของทรัพย์สิน: `{asset_code}`")

# ================================
# 5) Form แก้ไขข้อมูล
# ================================
st.subheader("แก้ไขข้อมูล")

with st.form("edit_form"):
    new_values = {}
    for col in df.columns:
        val = row_data.get(col, "")
        if pd.isna(val):
            val = ""
        new_values[col] = st.text_input(col, str(val))
    saved = st.form_submit_button("💾 บันทึกข้อมูล")

# ================================
# 6) บันทึกกลับ Excel
# ================================
if saved:
    for col in df.columns:
        df.at[row_index, col] = new_values[col]

    df.to_excel(EXCEL_PATH, index=False)
    st.success("บันทึกข้อมูลสำเร็จ ✔")
