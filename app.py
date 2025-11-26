import streamlit as st
from auth import is_authed  # ฟังก์ชันเช็คล็อกอินจาก auth.py

st.set_page_config(
    page_title="MedEquip Pro Lab – Medical Equipment Management",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# 🔁 ตรวจสถานะ / query ให้เด้งไปหน้า login
# -----------------------------
# ถ้าล็อกอินแล้ว → เข้า Dashboard หลักเลย
if is_authed():
    st.switch_page("pages/1_หน้าหลัก.py")

# อ่าน query parameter (รองรับทั้ง streamlit ใหม่/เก่า)
try:
    query_params = st.query_params
except Exception:
    query_params = st.experimental_get_query_params()

# ถ้ากดลิงก์ที่มี ?goto_login=1 → เด้งไปหน้าเข้าสู่ระบบ
if "goto_login" in query_params:
    st.switch_page("pages/0_เข้าสู่ระบบ.py")

# -----------------------------
# 🎨 CSS หน้า Landing (ซ่อน sidebar)
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    .stApp {
        background: linear-gradient(to bottom, #F0F9FF 0%, #E0F9FF 30%, #EDF2FF 100%);
    }

    /* ซ่อน sidebar ในหน้า Landing */
    [data-testid="stSidebar"] {
        display: none;
    }
    .main .block-container {
        padding-left: 0;
        padding-right: 0;
    }

    /* แถบหัวเว็บ */
    .me-header-bar {
        background-color: #FFFFFF;
        border-bottom: 1px solid #E5E7EB;
        padding: 10px 32px;
        display: flex;
        align-items: center;
        justify-content: space-between; /* ดันปุ่มไปชิดขวา */
        box-shadow: 0 2px 6px rgba(15,23,42,0.04);
        margin-bottom: 12px;
    }
    .me-header-left {
        display:flex;
        align-items:center;
        gap:10px;
    }
    .me-logo {
        width:36px;
        height:36px;
        border-radius:12px;
        background: #2563EB;
        display:flex;
        align-items:center;
        justify-content:center;
        color:#fff;
        font-size:20px;
    }
    .me-title-main {
        font-size:16px;
        font-weight:700;
        color:#111827;
        line-height:1.2;
    }
    .me-title-sub {
        font-size:12px;
        color:#6B7280;
    }

    /* ปุ่มเข้าสู่ระบบชิดขวา */
    .me-login-link {
        display:inline-flex;
        align-items:center;
        justify-content:center;
        padding:6px 18px;
        border-radius:999px;
        background:#2563EB;
        color:#FFFFFF;
        font-size:13px;
        font-weight:600;
        text-decoration:none;
        box-shadow:0 8px 20px rgba(37,99,235,0.45);
    }
    .me-login-link:hover {
        background:#1D4ED8;
        color:#FFFFFF;
    }

    /* Hero */
    .hero {
        padding: 36px 8% 24px 8%;
        text-align:center;
    }
    .hero h1 {
        font-size: 40px;
        font-weight: 800;
        color:#111827;
        margin-bottom: 6px;
    }
    .hero p {
        font-size: 15px;
        color:#4B5563;
        margin-top: 4px;
    }

    /* ส่วนการ์ดคุณสมบัติ */
    .feature-section {
        padding: 16px 8% 32px 8%;
    }
    .feature-title {
        text-align:center;
        font-size:22px;
        font-weight:700;
        margin-bottom: 18px;
        color:#111827;
    }
    .feature-grid {
        display:flex;
        flex-wrap:wrap;
        gap:18px;
        justify-content:center;
    }
    .feature-card {
        background:#FFFFFF;
        border-radius:18px;
        padding:18px 18px 16px 18px;
        width:260px;
        box-shadow:0 14px 35px rgba(15,23,42,0.12);
        border:1px solid #E5E7EB;
        text-align:center;
    }
    .feature-icon {
        width:42px;
        height:42px;
        border-radius:999px;
        background:#EFF6FF;
        color:#2563EB;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:22px;
        margin:0 auto 8px auto;
    }
    .feature-head {
        font-size:16px;
        font-weight:700;
        margin-bottom:4px;
        color:#111827;
    }
    .feature-desc {
        font-size:13px;
        color:#4B5563;
    }

    /* ปุ่ม “เริ่มใช้งานระบบ” */
    button[kind="primary"] {
        background: #16A34A !important;
        border-radius: 999px !important;
        border: none !important;
        padding: 6px 22px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        color:#FFFFFF !important;
        box-shadow: 0 12px 30px rgba(22,163,74,0.45) !important;
    }
    button[kind="primary"]:hover {
        background:#22C55E !important;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 🔵 Header (โลโก้ + ปุ่มเข้าสู่ระบบขวาสุด)
# -----------------------------
st.markdown(
    """
    <div class="me-header-bar">
      <div class="me-header-left">
        <div class="me-logo">⚙️</div>
        <div>
          <div class="me-title-main">MedEquip Pro Lab</div>
          <div class="me-title-sub">ระบบบริหารจัดการเครื่องมือแพทย์แบบครบวงจร</div>
        </div>
      </div>
      <a href="?goto_login=1" class="me-login-link">เข้าสู่ระบบ</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 🌟 Hero + ปุ่ม “เริ่มใช้งานระบบ”
# -----------------------------
st.markdown(
    """
    <div class="hero">
      <h1>บริหารเครื่องมือแพทย์อย่างมืออาชีพ เพื่อผลการตรวจที่แม่นยำและปลอดภัย</h1>
      <p>
        จัดการครอบคลุม ตั้งแต่ทะเบียน ประวัติการบำรุงรักษา แผนสอบเทียบ ไปจนถึงการแจ้งซ่อมแบบเรียลไทม์
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("เริ่มใช้งานระบบ  ➜", type="primary", key="hero_login"):
        st.switch_page("pages/0_เข้าสู่ระบบ.py")

# -----------------------------
# 💡 การ์ดคุณสมบัติ 3 ใบ
# -----------------------------
st.markdown(
    """
    <div class="feature-section">
      <div class="feature-title">คุณสมบัติหลักของ MedEquip Pro Lab</div>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">📋</div>
          <div class="feature-head">ทะเบียนครบถ้วน</div>
          <div class="feature-desc">
            จัดเก็บข้อมูลเครื่องมือแพทย์ทุกชนิดอย่างเป็นระบบ
            รองรับ Serial Number, QR Code, สถานะ และผู้รับผิดชอบ
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📆</div>
          <div class="feature-head">แผน PM & Calibration อัตโนมัติ</div>
          <div class="feature-desc">
            วางแผนบำรุงรักษาและสอบเทียบล่วงหน้า
            พร้อมสรุปสถานะครบตามมาตรฐาน ISO 15189 / 17025
          </div>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🛠</div>
          <div class="feature-head">ติดตามการซ่อมแบบเรียลไทม์</div>
          <div class="feature-desc">
            บันทึกใบงาน แจ้งซ่อมผ่านเว็บ แจ้งเตือนสถานะงานซ่อม
            และเก็บประวัติย้อนหลังเพื่อวิเคราะห์แนวโน้ม
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
