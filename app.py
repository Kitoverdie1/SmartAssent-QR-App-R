import streamlit as st
from auth import login, is_logged_in

# -----------------------------
# ⚙️ ตั้งค่าหน้า
# -----------------------------
st.set_page_config(
    page_title="MEM System - Login",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ถ้าล็อกอินอยู่แล้ว ให้เด้งไปหน้า Dashboard ทันที
if is_logged_in():
    st.switch_page("pages/2_Smart_Asset_Dashboard.py")

# -----------------------------
# 🎨 CSS: พื้นหลังม่วงสบายตา + ฟอร์มกลางจอ
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top,
                                    #D1C4E9 0%,
                                    #9575CD 35%,
                                    #673AB7 70%,
                                    #4527A0 100%);
    }

    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}

    /* ให้เนื้อหาหน้า Login อยู่กลางจอ */
    .main .block-container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 0;
        padding-bottom: 0;
    }

    /* ซ่อน sidebar ในหน้า Login */
    [data-testid="stSidebar"] { display: none; }

    /* การ์ดฟอร์มหลัก */
    [data-testid="stForm"] {
        width: 460px;
        max-width: 95vw;
        background: rgba(12, 10, 35, 0.96);
        border-radius: 24px;
        padding: 22px 26px 18px 26px;
        box-shadow: 0 26px 60px rgba(0, 0, 0, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #F5F3FF;
    }

    .login-header-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 16px;
    }

    .login-logo {
        width: 56px;
        height: 56px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        background: linear-gradient(135deg, #EDE7F6, #9575CD);
        box-shadow: 0 10px 24px rgba(46, 16, 101, 0.7);
        color: #4A148C;
    }

    .login-title-main {
        font-size: 22px;
        font-weight: 700;
        color: #EDE7F6;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
    }

    .login-title-sub {
        font-size: 13px;
        color: #C5CAE9;
    }

    .login-org {
        font-size: 12px;
        color: #B39DDB;
        margin-top: 3px;
    }

    [data-testid="stForm"] label {
        color: #EDE7F6 !important;
        font-weight: 500;
        font-size: 13px;
    }

    [data-testid="stForm"] input {
        background-color: #F5F3FF !important;
        border-radius: 999px !important;
        border: 1px solid #CE93D8 !important;
        color: #111827 !important;
        padding-left: 18px !important;
        font-size: 14px !important;
    }

    [data-testid="stForm"] input::placeholder {
        color: #9CA3AF !important;
    }

    [data-testid="stForm"] input:focus {
        border-color: #FFB300 !important;
        box-shadow: 0 0 0 1px #FFB300 !important;
    }

    [data-testid="stForm"] button[kind="primary"] {
        background: linear-gradient(135deg, #7E57C2, #5E35B1);
        color: #FFFFFF;
        border-radius: 999px;
        border: none;
        font-weight: 700;
        font-size: 15px;
        padding-top: 7px;
        padding-bottom: 7px;
        box-shadow: 0 12px 26px rgba(46, 16, 101, 0.75);
    }

    [data-testid="stForm"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #B39DDB, #673AB7);
        transform: translateY(-1px);
    }

    .login-footer-text {
        margin-top: 10px;
        font-size: 12px;
        color: #ECEFF4;
        text-align: center;
        opacity: 0.9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 🧩 ฟอร์มเข้าสู่ระบบ (อยู่กลางจอ)
# -----------------------------
with st.form("login_form"):
    st.markdown(
        """
        <div class="login-header-row">
            <div class="login-logo">🩺</div>
            <div>
                <div class="login-title-main">MEM System</div>
                <div class="login-title-sub">Medical Equipment Management System</div>
                <div class="login-org">โรงพยาบาลมหาวิทยาลัยพะเยา</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input("ชื่อผู้ใช้", placeholder="เช่น ton")
    password = st.text_input("รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน")

    submitted = st.form_submit_button("เข้าสู่ระบบ")

if submitted:
    if login(username.strip(), password):
        # ล็อกอินสำเร็จ → ไปหน้า Dashboard ทันที
        st.switch_page("pages/2_Smart_Asset_Dashboard.py")
    else:
        st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

st.markdown(
    '<div class="login-footer-text">สำหรับเจ้าหน้าที่ภายในเท่านั้น</div>',
    unsafe_allow_html=True,
)
