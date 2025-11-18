import pandas as pd
import qrcode
import os

# -----------------------------
# 1. ตั้งค่าไฟล์และโฟลเดอร์
# -----------------------------
EXCEL_PATH = "Smart Asset Lab.xlsx"
OUTPUT_QR = "qrcodes"

STREAMLIT_URL = "https://gpqgy3cvkjoblhckidqhaf.streamlit.app/qr_detail?code="

os.makedirs(OUTPUT_QR, exist_ok=True)

# -----------------------------
# 2. โหลดข้อมูล
# -----------------------------
df = pd.read_excel(EXCEL_PATH).fillna("")

if "รหัสเครื่องมือห้องปฏิบัติการ" not in df.columns:
    raise Exception("❌ ERROR: ไม่พบคอลัมน์ 'รหัสเครื่องมือห้องปฏิบัติการ' ใน Excel")

# -----------------------------
# 3. วนสร้าง QR Code
# -----------------------------
for i, row in df.iterrows():
    tool_code = str(row["รหัสเครื่องมือห้องปฏิบัติการ"]).strip()

    # สร้าง URL สำหรับ Streamlit Cloud
    qr_url = STREAMLIT_URL + tool_code

    # สร้าง QR
    img = qrcode.make(qr_url)

    file_name = f"{tool_code}.png"
    save_path = os.path.join(OUTPUT_QR, file_name)
    img.save(save_path)

    print(f"✔ QR สร้างแล้ว: {save_path}")

print("\n🎉 สร้าง QR Codes เสร็จสมบูรณ์แล้ว!")
print("📌 ไปที่โฟลเดอร์ qrcodes เพื่อดูไฟล์ทั้งหมด")
