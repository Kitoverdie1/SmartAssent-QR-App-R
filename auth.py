import streamlit as st

# -----------------------------
# 🔐 รายชื่อผู้ใช้ (แก้ได้ตามจริง)
# -----------------------------
USERS = {
    "ton": {
        "password": "1234",
        "fullname": "คุณต้น",
        "role": "admin",
    },
    "demo": {
        "password": "demo1234",
        "fullname": "Demo User",
        "role": "user",
    },
}


def _init_session_state():
    """เตรียมค่าเริ่มต้นให้ session_state"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def login(username: str, password: str) -> bool:
    """
    เช็ค username / password
    ถ้าถูก: set session_state แล้วคืนค่า True
    """
    _init_session_state()

    user = USERS.get(username)
    if user and password == user["password"]:
        st.session_state.logged_in = True
        st.session_state.current_user = {
            "username": username,
            "fullname": user["fullname"],
            "role": user["role"],
        }
        return True
    return False


def is_logged_in() -> bool:
    """เช็คว่าล็อกอินอยู่ไหม"""
    _init_session_state()
    return bool(st.session_state.logged_in)


def is_authed() -> bool:
    """alias เผื่อโค้ดเก่าเรียกชื่อ is_authed()"""
    return is_logged_in()


def require_login():
    """
    ใช้บนหน้า Dashboard / QR
    - ถ้ายังไม่ล็อกอิน: redirect กลับหน้า Login (app.py)
    """
    _init_session_state()
    if not st.session_state.logged_in:
        # พยายามสลับหน้าไป app.py (หน้า Login)
        try:
            st.switch_page("app.py")
        except Exception:
            # ถ้าสลับหน้าไม่ได้ ให้เตือนและหยุดไว้เฉย ๆ
            st.warning("กรุณาเข้าสู่ระบบก่อนใช้งานระบบ")
            st.stop()


def logout_button():
    """
    ปุ่มออกจากระบบ (เอาไปวางบนหน้า Dashboard / QR)
    - กดแล้วเคลียร์ session แล้ว rerun
    - เมื่อ rerun require_login() บนหน้า Dashboard จะพาไปหน้า Login ให้อัตโนมัติ
    """
    _init_session_state()
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("ออกจากระบบ", use_container_width=True):
            # ล้างสถานะล็อกอิน
            st.session_state.logged_in = False
            st.session_state.current_user = None

            # Streamlit รุ่นใหม่ใช้ st.rerun()
            try:
                st.rerun()
            except Exception:
                # ถ้าเป็นเวอร์ชันเก่าที่มี experimental_rerun อยู่
                st.experimental_rerun()

