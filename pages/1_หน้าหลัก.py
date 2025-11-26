import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

from auth import is_authed, logout_button

EXCEL_PATH = "Smart Asset Lab.xlsx"


def get_asset_sheet_name() -> str:
    xls = pd.ExcelFile(EXCEL_PATH)
    return xls.sheet_names[0]


@st.cache_data
def load_assets() -> pd.DataFrame:
    if not Path(EXCEL_PATH).exists():
        return pd.DataFrame()

    try:
        asset_sheet = get_asset_sheet_name()
        df = pd.read_excel(EXCEL_PATH, sheet_name=asset_sheet).dropna(how="all")
    except Exception:
        df = pd.read_excel(EXCEL_PATH, sheet_name=0).dropna(how="all")

    base_cols = [
        "รหัสเครื่องมือห้องปฏิบัติการ",
        "AssetID",
        "ชื่อ",
        "หมวดหมู่",
        "สถานะ",
        "ความเสี่ยง (Risk Level)",
        "ผู้รับผิดชอบ (ปัจจุบัน)",
        "สถานที่ใช้งาน (ปัจจุบัน)",
        "ผู้ผลิต",
        "ผู้ให้บริการซ่อม",
        "อายุการใช้งาน (ปี)",
        "วันที่เริ่มใช้งาน",
        "วันที่คาดว่าสิ้นสุดอายุ",
        "Calibration Due Date",
        "Calibration Status",
        "PM Due Date",
        "PM Status",
    ]
    for c in base_cols:
        if c not in df.columns:
            df[c] = None

    return df


@st.cache_data
def load_sheet(sheet_name: str, columns: list) -> pd.DataFrame:
    if not Path(EXCEL_PATH).exists():
        return pd.DataFrame(columns=columns)

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
        for c in columns:
            if c not in df.columns:
                df[c] = None
        return df[columns]
    except ValueError:
        return pd.DataFrame(columns=columns)


def main():
    st.set_page_config(page_title="Dashboard หลัก", page_icon="📊", layout="wide")

    if not is_authed():
        st.error("กรุณาเข้าสู่ระบบจากหน้า Home ก่อนใช้งาน")
        st.stop()

    st.title("📊 Dashboard หลัก – Integrated Smart Asset & MEQ Platform")
    logout_button()

    assets = load_assets()
    maintenance = load_sheet(
        "Maintenance",
        [
            "วันที่",
            "รหัสเครื่องมือห้องปฏิบัติการ",
            "AssetID",
            "ชื่อ",
            "ประเภทงาน (PM/CM)",
            "อาการ/ปัญหา",
            "การแก้ไข",
            "ระดับความเสี่ยง",
            "ผู้ดำเนินการ",
            "สถานะงาน",
        ],
    )
    calibration = load_sheet(
        "Calibration",
        [
            "วันที่สอบเทียบ",
            "รหัสเครื่องมือห้องปฏิบัติการ",
            "AssetID",
            "ชื่อ",
            "ผู้ให้บริการสอบเทียบ",
            "ผลการสอบเทียบ",
            "ใบรายงาน (ไฟล์/เลขที่)",
            "Calibration Due Date ถัดไป",
            "สถานะ",
        ],
    )
    risk_events = load_sheet(
        "RiskEvents",
        [
            "วันที่เกิดเหตุ",
            "รหัสเครื่องมือห้องปฏิบัติการ",
            "เหตุการณ์",
            "ระดับความรุนแรง (Severity)",
            "ความถี่ (Occurrence)",
            "การตรวจพบ (Detection)",
            "ค่า RPN",
            "ผู้บันทึก",
            "สถานะเหตุการณ์",
        ],
    )

    today = date.today()
    today_ts = pd.Timestamp(today)

    total_assets = len(assets)
    active_assets = (assets["สถานะ"] == "พร้อมใช้งาน").sum() if "สถานะ" in assets.columns else 0
    high_risk_assets = (assets["ความเสี่ยง (Risk Level)"] == "สูง").sum()

    calib_overdue = 0
    if not calibration.empty:
        calib_dt = pd.to_datetime(calibration["Calibration Due Date ถัดไป"], errors="coerce")
        calib_overdue = ((calib_dt.notna()) & (calib_dt < today_ts)).sum()

    pm_overdue = 0
    if not assets.empty:
        pm_dt = pd.to_datetime(assets["PM Due Date"], errors="coerce")
        pm_overdue = ((pm_dt.notna()) & (pm_dt < today_ts)).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("จำนวนเครื่องมือทั้งหมด", f"{total_assets:,}")
    col2.metric("พร้อมใช้งาน", f"{active_assets:,}")
    col3.metric("High Risk", f"{high_risk_assets:,}")
    col4.metric("เกินกำหนดสอบเทียบ", f"{calib_overdue:,}")

    st.markdown("---")

    tabs = st.tabs(
        [
            "1) Asset Master Data",
            "2) Calibration Management",
            "3) PM/CM Maintenance",
            "4) Risk & Safety",
            "5) Quality Documents (ภาพรวม)",
            "6) Analytics Snapshot",
            "7) Smart Notification (ภาพรวม)",
        ]
    )

    # 1) Asset
    with tabs[0]:
        st.subheader("Asset Master Data – ทะเบียนครุภัณฑ์และเครื่องมือแพทย์")
        if assets.empty:
            st.info("ยังไม่มีข้อมูลครุภัณฑ์ในไฟล์ Excel")
        else:
            c1, c2, c3 = st.columns(3)
            status_filter = c1.multiselect("สถานะ", sorted(assets["สถานะ"].dropna().unique().tolist()))
            risk_filter = c2.multiselect("ระดับความเสี่ยง", sorted(assets["ความเสี่ยง (Risk Level)"].dropna().unique().tolist()))
            dept_filter = c3.multiselect(
                "สถานที่ใช้งาน (ปัจจุบัน)",
                sorted(assets["สถานที่ใช้งาน (ปัจจุบัน)"].dropna().unique().tolist()),
            )

            df_view = assets.copy()
            if status_filter:
                df_view = df_view[df_view["สถานะ"].isin(status_filter)]
            if risk_filter:
                df_view = df_view[df_view["ความเสี่ยง (Risk Level)"].isin(risk_filter)]
            if dept_filter:
                df_view = df_view[df_view["สถานที่ใช้งาน (ปัจจุบัน)"].isin(dept_filter)]

            st.dataframe(
                df_view[
                    [
                        "รหัสเครื่องมือห้องปฏิบัติการ",
                        "ชื่อ",
                        "หมวดหมู่",
                        "สถานะ",
                        "ความเสี่ยง (Risk Level)",
                        "ผู้รับผิดชอบ (ปัจจุบัน)",
                        "สถานที่ใช้งาน (ปัจจุบัน)",
                        "Calibration Due Date",
                        "PM Due Date",
                    ]
                ].sort_values("รหัสเครื่องมือห้องปฏิบัติการ"),
                use_container_width=True,
            )

    # 2) Calibration
    with tabs[1]:
        st.subheader("ระบบสอบเทียบ (Calibration Management)")
        st.write("ใช้ข้อมูลจากชีต `Calibration` ในไฟล์ Smart Asset Lab.xlsx")

        if calibration.empty:
            st.info("ยังไม่มีข้อมูลชีต 'Calibration'")
        else:
            calib_df = calibration.copy()
            calib_df["Calibration Due Date ถัดไป"] = pd.to_datetime(
                calib_df["Calibration Due Date ถัดไป"], errors="coerce"
            )
            calib_df["สถานะ"] = calib_df["สถานะ"].fillna("ปกติ")

            c1, c2 = st.columns(2)
            status_filter = c1.multiselect("สถานะ", sorted(calib_df["สถานะ"].dropna().unique().tolist()))
            due_mode = c2.selectbox(
                "ตัวกรองกำหนดสอบเทียบ",
                ["ทั้งหมด", "ใกล้กำหนด (ภายใน 30 วัน)", "เกินกำหนดแล้ว"],
            )

            if status_filter:
                calib_df = calib_df[calib_df["สถานะ"].isin(status_filter)]

            if due_mode == "ใกล้กำหนด (ภายใน 30 วัน)":
                calib_df = calib_df[
                    (calib_df["Calibration Due Date ถัดไป"].notna())
                    & (calib_df["Calibration Due Date ถัดไป"] >= today_ts)
                    & (calib_df["Calibration Due Date ถัดไป"] <= today_ts + pd.Timedelta(days=30))
                ]
            elif due_mode == "เกินกำหนดแล้ว":
                calib_df = calib_df[
                    (calib_df["Calibration Due Date ถัดไป"].notna())
                    & (calib_df["Calibration Due Date ถัดไป"] < today_ts)
                ]

            st.dataframe(calib_df, use_container_width=True)

            if not calib_df.empty:
                st.markdown("#### สรุปจำนวนเครื่องมือแบ่งตามสถานะสอบเทียบ")
                st.bar_chart(
                    calib_df.groupby("สถานะ")["รหัสเครื่องมือห้องปฏิบัติการ"].count(),
                    use_container_width=True,
                )

    # 3) Maintenance
    with tabs[2]:
        st.subheader("ระบบบำรุงรักษา (PM/CM Maintenance)")
        if maintenance.empty:
            st.info("ยังไม่มีข้อมูลชีต 'Maintenance'")
        else:
            maint_df = maintenance.copy()
            maint_df["วันที่"] = pd.to_datetime(maint_df["วันที่"], errors="coerce")

            c1, c2 = st.columns(2)
            type_filter = c1.multiselect("ประเภทงาน", ["PM", "CM"], default=[])
            status_filter = c2.multiselect(
                "สถานะงาน",
                maint_df["สถานะงาน"].dropna().unique().tolist(),
            )

            if type_filter:
                maint_df = maint_df[maint_df["ประเภทงาน (PM/CM)"].isin(type_filter)]
            if status_filter:
                maint_df = maint_df[maint_df["สถานะงาน"].isin(status_filter)]

            st.dataframe(
                maint_df.sort_values("วันที่", ascending=False),
                use_container_width=True,
            )

            maint_df["เดือน"] = maint_df["วันที่"].dt.to_period("M").astype(str)
            st.markdown("#### งานซ่อม/PM แบ่งตามเดือน")
            st.bar_chart(
                maint_df.groupby(["เดือน", "ประเภทงาน (PM/CM)"])["รหัสเครื่องมือห้องปฏิบัติการ"]
                .count()
                .unstack(fill_value=0),
                use_container_width=True,
            )

    # 4) Risk
    with tabs[3]:
        st.subheader("ความเสี่ยงและความปลอดภัย (Risk & Safety)")
        if risk_events.empty:
            st.info("ยังไม่มีข้อมูลชีต 'RiskEvents'")
        else:
            risk_df = risk_events.copy()
            risk_df["วันที่เกิดเหตุ"] = pd.to_datetime(risk_df["วันที่เกิดเหตุ"], errors="coerce")
            st.dataframe(
                risk_df.sort_values("วันที่เกิดเหตุ", ascending=False),
                use_container_width=True,
            )

            st.markdown("#### เหตุการณ์แบ่งตามระดับความรุนแรง")
            st.bar_chart(
                risk_df.groupby("ระดับความรุนแรง (Severity)")["รหัสเครื่องมือห้องปฏิบัติการ"]
                .count()
                .sort_values(ascending=False),
                use_container_width=True,
            )

    # 5) Quality Docs overview
    with tabs[4]:
        st.subheader("Quality Documentation Hub – ภาพรวม")
        st.write(
            "รายละเอียดการเพิ่ม/แก้ไขเอกสารอยู่ที่หน้า `เอกสารคุณภาพ` ในเมนูด้านซ้าย (ไฟล์ 5_เอกสารคุณภาพ.py)"
        )

    # 6) Analytics snapshot
    with tabs[5]:
        st.subheader("Analytics Snapshot")
        if not assets.empty and "หมวดหมู่" in assets.columns:
            st.markdown("#### จำนวนเครื่องมือแบ่งตามหมวดหมู่")
            st.bar_chart(
                assets.groupby("หมวดหมู่")["รหัสเครื่องมือห้องปฏิบัติการ"].count().sort_values(ascending=False),
                use_container_width=True,
            )
        if not maintenance.empty:
            st.markdown("#### Top 10 เครื่องมือที่มีงานซ่อม/PM มากที่สุด")
            st.bar_chart(
                maintenance.groupby("รหัสเครื่องมือห้องปฏิบัติการ")["วันที่"]
                .count()
                .sort_values(ascending=False)
                .head(10),
                use_container_width=True,
            )

    # 7) Notification overview
    with tabs[6]:
        st.subheader("Smart Notification – ภาพรวม")
        st.write(
            """
            ระบบแจ้งเตือนจะอาศัย Due Date จาก Calibration / PM และอายุการใช้งาน
            ค่าตั้งต่าง ๆ สามารถกำหนดได้ที่หน้า `Smart_Notification` จากเมนูด้านซ้าย
            จากนั้นสามารถใช้ Google Apps Script หรือ Python ภายนอกดึงข้อมูลไปยิง LINE / Email ต่อได้
            """
        )


if __name__ == "__main__":
    main()
