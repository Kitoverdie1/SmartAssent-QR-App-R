import streamlit as st
import pandas as pd
from pathlib import Path

from auth import is_authed, logout_button

EXCEL_PATH = "Smart Asset Lab.xlsx"


def load_config() -> pd.DataFrame:
    cols = [
        "ชื่อค่า",
        "ค่า",
        "รายละเอียด",
    ]
    if not Path(EXCEL_PATH).exists():
        return pd.DataFrame(columns=cols)

    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="NotificationConfig")
    except ValueError:
        return pd.DataFrame(columns=cols)

    for c in cols:
        if c not in df.columns:
            df[c] = None

    return df[cols]


def save_config(df: pd.DataFrame):
    if Path(EXCEL_PATH).exists():
        writer = pd.ExcelWriter(
            EXCEL_PATH, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
    else:
        writer = pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode="w")

    df.to_excel(writer, sheet_name="NotificationConfig", index=False)
    writer.close()


def upsert_setting(df: pd.DataFrame, name: str, value: str, desc: str) -> pd.DataFrame:
    if name in df["ชื่อค่า"].astype(str).tolist():
        df.loc[df["ชื่อค่า"] == name, ["ค่า", "รายละเอียด"]] = [value, desc]
    else:
        df = pd.concat(
            [df, pd.DataFrame([{"ชื่อค่า": name, "ค่า": value, "รายละเอียด": desc}])],
            ignore_index=True,
        )
    return df


def main():
    st.set_page_config(page_title="Smart Notification", page_icon="🔔", layout="wide")

    if not is_authed():
        st.error("กรุณาเข้าสู่ระบบจากหน้า Home ก่อนใช้งาน")
        st.stop()

    st.title("🔔 ระบบแจ้งเตือนอัจฉริยะ (Smart Notification)")
    logout_button()

    cfg = load_config()

    st.markdown(
        """
        ใช้หน้านี้กำหนดค่าพื้นฐานสำหรับการแจ้งเตือน เช่น กี่วันก่อนถึงกำหนดสอบเทียบ / PM
        และตั้งค่า Token ของ LINE หรือ Email (เก็บไว้ใน Excel เพื่อใช้ต่อกับ Script ภายนอก)
        """
    )

    # ---------- ค่ากำหนดด้านเวลา ----------
    st.subheader("ค่ากำหนดเวลาแจ้งเตือน")

    c1, c2, c3 = st.columns(3)
    days_calib = c1.number_input("แจ้งเตือนก่อนถึงกำหนดสอบเทียบ (วัน)", min_value=1, max_value=365, value=30)
    days_pm = c2.number_input("แจ้งเตือนก่อนถึงกำหนด PM (วัน)", min_value=1, max_value=365, value=14)
    days_life = c3.number_input("แจ้งเตือนก่อนหมดอายุการใช้งานเครื่องมือ (วัน)", min_value=1, max_value=365, value=90)

    # ---------- Token ต่าง ๆ ----------
    st.subheader("การเชื่อมต่อ LINE / Email (เก็บค่าไว้ใช้ภายนอก)")

    line_token = st.text_input("LINE Notify / LINE OA Access Token", type="password")
    email_sender = st.text_input("Email ผู้ส่งแจ้งเตือน (เช่น noreply@up.ac.th)")
    email_smtp = st.text_input("SMTP Server (ใช้ใน Script ภายนอก)", value="smtp.gmail.com")

    if st.button("💾 บันทึกค่าการแจ้งเตือน", type="primary"):
        cfg = upsert_setting(cfg, "days_before_calibration", str(days_calib), "แจ้งเตือนก่อนถึงกำหนดสอบเทียบ (วัน)")
        cfg = upsert_setting(cfg, "days_before_pm", str(days_pm), "แจ้งเตือนก่อนถึงกำหนด PM (วัน)")
        cfg = upsert_setting(cfg, "days_before_lifecycle", str(days_life), "แจ้งเตือนก่อนหมดอายุการใช้งาน (วัน)")
        cfg = upsert_setting(cfg, "line_token", line_token, "Access Token สำหรับส่งแจ้งเตือน LINE")
        cfg = upsert_setting(cfg, "email_sender", email_sender, "อีเมลผู้ส่งแจ้งเตือน")
        cfg = upsert_setting(cfg, "email_smtp", email_smtp, "SMTP Server สำหรับส่งอีเมล")

        save_config(cfg)
        st.success("บันทึกค่าการแจ้งเตือนเรียบร้อยแล้ว ✅")

    st.markdown("---")
    st.subheader("รายการค่าตั้งปัจจุบัน (จาก Excel)")

    cfg = load_config()
    if cfg.empty:
        st.info("ยังไม่มีการบันทึกค่าการแจ้งเตือนในชีต NotificationConfig")
    else:
        st.dataframe(cfg, use_container_width=True)


if __name__ == "__main__":
    main()
