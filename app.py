import streamlit as st
from auth import login, is_logged_in   # ใช้ auth.py เดิมของคุณ

# -----------------------------
# ⚙️ ตั้งค่าหน้า
# -----------------------------
st.set_page_config(
    page_title="MEM System - Login",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ถ้าเคยล็อกอินอยู่แล้ว → ไปหน้า Dashboard เลย
if is_logged_in():
    st.switch_page("pages/1_หน้าหลัก.py")

if "login_error" not in st.session_state:
    st.session_state["login_error"] = ""

# -----------------------------
# 🎨 CSS: การ์ด login กลางจอพอดี
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    /* พื้นหลังโทนม่วง-ฟ้า */
    .stApp {
        background: radial-gradient(circle at top,
                                    #C7D2FE 0%,
                                    #6366F1 35%,
                                    #4C1D95 80%);
    }

    /* ซ่อน header / toolbar / sidebar ของ Streamlit */
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none;}

    /* ให้ block-container กลายเป็น flex แล้วจัดของไว้กลางจอ */
    .main .block-container {
        max-width: 100%;
        height: 100vh;
        padding-top: 0;
        padding-bottom: 0;
        margin: 0;
        display: flex;
        justify-content: center;   /* กลางแนวนอน */
        align-items: center;       /* กลางแนวตั้ง */
    }

    /* ใช้ตัว form ของ Streamlit เป็นการ์ด login */
    [data-testid="stForm"] {
        background: #F9FAFB;
        border-radius: 28px;
        padding: 26px 32px 22px 32px;
        box-shadow: 0 28px 60px rgba(15, 23, 42, 0.75);
        border: 1px solid #E5E7EB;
        width: 430px;              /* ความกว้างการ์ด */
    }

    /* ให้เนื้อหาข้างใน form กว้างเต็มการ์ด */
    [data-testid="stForm"] > div {
        width: 100%;
    }

    /* หัวข้อด้านบนการ์ด */
    .login-title-main {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
        text-align: center;
        margin-bottom: 2px;
    }
    .login-title-sub {
        font-size: 13px;
        color: #4B5563;
        text-align: center;
    }
    .login-title-org {
        font-size: 12px;
        color: #6B21A8;
        text-align: center;
        margin-bottom: 14px;
    }

    /* label + input */
    [data-testid="stTextInput"] {
        width: 100%;
    }

    [data-testid="stTextInput"] > label {
        color: #111827 !important;
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 2px;
    }

    [data-testid="stTextInput"] input {
        background-color: #F9FAFB !important;
        border-radius: 999px !important;
        border: 1px solid #D1D5DB !important;
        color: #111827 !important;
        padding-left: 16px !important;
        font-size: 14px !important;
    }

    [data-testid="stTextInput"] input::placeholder {
        color: #9CA3AF !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 1px #6366F1 !important;
    }

    /* ปุ่มเข้าสู่ระบบ ให้กว้างเท่าการ์ด และเป็น pill */
    [data-testid="stForm"] button[kind="primary"] {
        width: 100%;
        background: linear-gradient(135deg, #6366F1, #4C1D95);
        color: #FFFFFF !important;
        border-radius: 999px;
        border: none;
        font-weight: 700;
        font-size: 15px;
        padding-top: 6px;
        padding-bottom: 6px;
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.55);
    }

    [data-testid="stForm"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #A5B4FC, #7C3AED);
        transform: translateY(-1px);
    }

    /* กล่อง error */
    .login-error-box {
        margin-top: 8px;
        margin-bottom: 4px;
        padding: 8px 12px;
        border-radius: 10px;
        background: #FEE2E2;
        border: 1px solid #F87171;
        font-size: 12px;
        color: #B91C1C;
    }

    /* ข้อความท้ายการ์ด */
    .login-footer-text {
        margin-top: 10px;
        font-size: 11px;
        color: #6B7280;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 🧩 ฟอร์ม Login อยู่ใน card เดียว
# -----------------------------
login_error = st.session_state["login_error"]

with st.form("login_form"):
    st.markdown(
        """
        <div class="login-title-main">MEM System</div>
        <div class="login-title-sub">Medical Equipment Management System</div>
        <div class="login-title-org">โรงพยาบาลมหาวิทยาลัยพะเยา</div>
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input("ชื่อผู้ใช้", placeholder="เช่น ton")
    password = st.text_input("รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน")

    if login_error:
        st.markdown(
            f'<div class="login-error-box">{login_error}</div>',
            unsafe_allow_html=True,
        )

    submitted = st.form_submit_button("เข้าสู่ระบบ")

    st.markdown(
        '<div class="login-footer-text">สำหรับเจ้าหน้าที่ภายในเท่านั้น</div>',
        unsafe_allow_html=True,
    )

# -----------------------------
# 🔐 ตรวจผลการล็อกอิน
# -----------------------------
if submitted:
    if login(username.strip(), password):
        st.session_state["login_error"] = ""
        st.rerun()  # รอบถัดไป is_logged_in() จะเด้งไปหน้า Dashboard
    else:
        st.session_state["login_error"] = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
        st.rerun()
