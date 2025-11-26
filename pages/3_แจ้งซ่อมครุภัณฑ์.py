import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

from auth import is_authed, logout_button

EXCEL_PATH = "Smart Asset Lab.xlsx"


def get_asset_sheet_name() -> str:
    xls = pd.ExcelFile(EXCEL_PATH)
    return xls.sheet_names[0]


def load_assets() -> pd.DataFrame:
    if not Path(EXCEL_PATH).exists():
        return pd.DataFrame()
    asset_sheet = get_asset_sheet_name()
    df = pd.read_excel(EXCEL_PATH, sheet_name=asset_sheet).dropna(how="all")
    if "รหัสเครื่องมือห้องปฏิบัติการ" not in df.columns:
        df["รหัสเครื่องมือห้องปฏิบัติการ"] = ""
    if "ชื่อ" not in df.columns:
        df["ชื่อ"] = ""
    if "AssetID" not in df.columns:
        df["AssetID"] = ""
    return df[["รหัสเครื่องมือห้องปฏิบัติการ", "AssetID", "ชื่อ"]]


def load_maintenance() -> pd.DataFrame:
    if not Path(EXCEL_PATH).exists():
        return pd.DataFrame()
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="Maintenance")
    except ValueError:
        cols = [
            "วันที่",
            "รหัสเครื่องมือห้องปฏิบัติการ",
            "AssetID",
            "ชื่อ",
            "ประเภทงาน (PM/CM)",
            "อาการ/ปัญหา",
            "การแก้ไข",
            "ระดับความเสี่ยง",
            "มาตรการควบคุมอันตราย",
            "ผู้แจ้ง",
            "ผู้ดำเนินการ",
            "สถานะงาน",
        ]
        return pd.DataFrame(columns=cols)
    return df


def save_maintenance(df: pd.DataFrame):
    if Path(EXCEL_PATH).exists():
        writer = pd.ExcelWriter(
            EXCEL_PATH, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
    else:
        writer = pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode="w")

    df.to_excel(writer, sheet_name="Maintenance", index=False)
    writer.close()


def main():
    st.set_page_config(page_title="แจ้งซ่อม / PM", page_icon="🛠", layout="wide")

    if not is_authed():
        st.error("กรุณาเข้าสู่ระบบจากหน้า Home ก่อนใช้งาน")
        st.stop()

    st.title("🛠 ระบบบำรุงรักษา (PM/CM Maintenance)")
    logout_button()

    assets = load_assets()
    maint_df = load_maintenance()

    st.markdown("## แบบฟอร์มแจ้งซ่อม / ขอทำ PM")

    with st.form("maint_form"):
        c1, c2 = st.columns(2)
        work_type = c1.selectbox("ประเภทงาน", ["PM (Preventive Maintenance)", "CM (Corrective Maintenance)"])
        work_date = c2.date_input("วันที่แจ้ง/ดำเนินการ", datetime.today())

        # เลือกเครื่องมือ
        tool_code = st.selectbox(
            "เลือกเครื่องมือ", assets["รหัสเครื่องมือห้องปฏิบัติการ"].astype(str).tolist()
        )
        tool_row = assets[assets["รหัสเครื่องมือห้องปฏิบัติการ"].astype(str) == str(tool_code)].iloc[0]
        st.text_input("AssetID", value=str(tool_row["AssetID"]), disabled=True)
        st.text_input("ชื่อเครื่องมือ", value=str(tool_row["ชื่อ"]), disabled=True)

        st.text_area("อาการ/ปัญหา หรือขอบเขตงาน PM", key="issue")

        c3, c4 = st.columns(2)
        risk_level = c3.selectbox("ระดับความเสี่ยงของงานซ่อม", ["ต่ำ", "ปานกลาง", "สูง", "วิกฤติ"])
        control = c4.text_input("มาตรการควบคุมอันตราย (เช่น Lockout/Tagout, PPE ฯลฯ)")

        reporter = st.text_input("ผู้แจ้ง / ผู้ขอทำ PM")
        status = st.selectbox("สถานะงาน", ["รอดำเนินการ", "กำลังดำเนินการ", "เสร็จสิ้น"])

        submitted = st.form_submit_button("บันทึกใบงาน")

    if submitted:
        if not st.session_state.get("issue"):
            st.error("กรุณาระบุอาการ/ปัญหา หรือขอบเขตงาน PM")
        else:
            new_row = {
                "วันที่": work_date,
                "รหัสเครื่องมือห้องปฏิบัติการ": tool_code,
                "AssetID": tool_row["AssetID"],
                "ชื่อ": tool_row["ชื่อ"],
                "ประเภทงาน (PM/CM)": "PM" if work_type.startswith("PM") else "CM",
                "อาการ/ปัญหา": st.session_state["issue"],
                "การแก้ไข": "",
                "ระดับความเสี่ยง": risk_level,
                "มาตรการควบคุมอันตราย": control,
                "ผู้แจ้ง": reporter,
                "ผู้ดำเนินการ": "",
                "สถานะงาน": status,
            }
            maint_df = pd.concat([maint_df, pd.DataFrame([new_row])], ignore_index=True)
            save_maintenance(maint_df)
            st.success("บันทึกใบงานเรียบร้อยแล้ว")
            st.cache_data.clear()

    st.markdown("## ประวัติงานซ่อม/บำรุงรักษาย้อนหลัง")
    if maint_df.empty:
        st.info("ยังไม่มีข้อมูลงานซ่อม/บำรุงรักษา")
    else:
        maint_df["วันที่"] = pd.to_datetime(maint_df["วันที่"], errors="coerce")
        st.dataframe(
            maint_df.sort_values("วันที่", ascending=False),
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
