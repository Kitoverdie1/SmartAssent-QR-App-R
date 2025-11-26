import pandas as pd
from pathlib import Path

# -------------------------
# ชื่อไฟล์ (ถ้าคุณเปลี่ยนชื่อให้แก้ตรงนี้)
# -------------------------
PLAN_PATH = "แผนสอบเทียบและบำรุงรักษาเครื่องมือ.xlsx"
SMART_ASSET_PATH = "Smart Asset Lab.xlsx"


def build_calibration_from_plan(plan_path: str) -> pd.DataFrame:
    """
    อ่านไฟล์แผนสอบเทียบและบำรุงรักษา (แผ่นห้องปฏิบัติการ + ธนาคารเลือด)
    แล้วแปลงให้อยู่ในรูปแบบมาตรฐานของชีต 'Calibration'
    """
    xls = pd.ExcelFile(plan_path)
    frames = []

    for sheet in xls.sheet_names:
        # อ่านด้วย header แถวที่ 3 (index=2)
        raw = pd.read_excel(plan_path, sheet_name=sheet, header=2)

        # แถวแรกของ raw คือหัวตารางจริง (No., ID Code, Equipment, ...)
        headers = raw.iloc[0].tolist()

        # ข้าม 2 แถวแรก (แถว 0 = header, แถว 1 = ชื่อกลุ่มเช่น "เครื่องมือตรวจวิเคราะห์")
        df = raw.iloc[2:].copy()
        df.columns = headers

        # เก็บเฉพาะแถวที่มี ID Code (ตัดแถวหัวข้อเช่น "กล้องจุลทรรศน์" ออก)
        if "ID Code" not in df.columns:
            continue

        df = df[df["ID Code"].notna()].copy()

        # แปลง Due M/D/Y เป็น datetime
        if "Due M/D/Y" in df.columns:
            df["Due M/D/Y"] = pd.to_datetime(df["Due M/D/Y"], errors="coerce")
        else:
            df["Due M/D/Y"] = pd.NaT

        # สร้าง DataFrame มาตรฐานสำหรับชีต Calibration
        calib = pd.DataFrame({
            "วันที่สอบเทียบ": pd.NaT,
            "รหัสเครื่องมือห้องปฏิบัติการ": df["ID Code"].astype(str),
            "AssetID": df.get("Asset ID", pd.Series([""] * len(df))).astype(str),
            "ชื่อ": df["Equipment"].astype(str),
            "ผู้ให้บริการสอบเทียบ": "",
            "ผลการสอบเทียบ": "",
            "ใบรายงาน (ไฟล์/เลขที่)": "",
            "Calibration Due Date ถัดไป": df["Due M/D/Y"],
        })

        frames.append(calib)

    if not frames:
        raise RuntimeError("ไม่พบข้อมูล ID Code ในไฟล์แผน")

    cal = pd.concat(frames, ignore_index=True)

    # คำนวณสถานะจาก Due Date
    today = pd.Timestamp("today").normalize()

    def status(row):
        d = row["Calibration Due Date ถัดไป"]
        if pd.isna(d):
            return "ไม่ระบุ"
        if d < today:
            return "เกินกำหนด"
        if d <= today + pd.Timedelta(days=30):
            return "ใกล้กำหนด"
        return "ปกติ"

    cal["สถานะ"] = cal.apply(status, axis=1)
    return cal


def write_calibration_to_smart_asset(cal_df: pd.DataFrame, smart_path: str):
    """
    เขียน DataFrame ลงชีต 'Calibration' ใน Smart Asset Lab.xlsx
    ถ้ามีชีตเดิมอยู่แล้วจะถูกแทนที่ (replace)
    """
    smart_file = Path(smart_path)

    if smart_file.exists():
        writer = pd.ExcelWriter(
            smart_file, engine="openpyxl", mode="a", if_sheet_exists="replace"
        )
    else:
        writer = pd.ExcelWriter(smart_file, engine="openpyxl", mode="w")

    cal_df.to_excel(writer, sheet_name="Calibration", index=False)
    writer.close()


def main():
    plan_file = Path(PLAN_PATH)
    if not plan_file.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์แผน: {plan_file}")

    cal_df = build_calibration_from_plan(str(plan_file))
    write_calibration_to_smart_asset(cal_df, SMART_ASSET_PATH)

    print(f"✅ สร้าง/อัปเดตชีต 'Calibration' ในไฟล์ {SMART_ASSET_PATH} เรียบร้อยแล้ว")
    print(f"จำนวนเครื่องมือในแผนสอบเทียบทั้งหมด: {len(cal_df)} รายการ")


if __name__ == "__main__":
    main()
