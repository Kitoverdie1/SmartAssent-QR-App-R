import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from auth import require_login, logout_button

EXCEL_PATH = "Smart Asset Lab.xlsx"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    excel_file = Path(path)
    if not excel_file.exists():
        return pd.DataFrame()
    df = pd.read_excel(excel_file).dropna(how="all").reset_index(drop=True)
    return df

def save_data(df: pd.DataFrame, path: str) -> None:
    df.to_excel(path, index=False)

def find_status_column(columns) -> str | None:
    for col in columns:
        if "สถานะ" in str(col):
            return col
    return None

# ------------------ Auth & Page config ------------------
st.set_page_config(page_title="Smart Asset Dashboard", page_icon="📊", layout="wide")
require_login()
logout_button()

# ------------------ CSS ------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }
    .hero-box {
        background: linear-gradient(135deg, #1565C0, #0D47A1);
        padding: 18px 24px;
        border-radius: 18px;
        color: #E3F2FD;
        box-shadow: 0 12px 30px rgba(13, 71, 161, 0.45);
        margin-bottom: 18px;
    }
    .hero-title {
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .hero-sub {
        font-size: 14px;
        opacity: 0.90;
    }
    .metric-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 16px 18px;
        border: 1px solid #E3F2FD;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
    }
    .metric-label {
        font-size: 13px;
        color: #6B7280;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
    }
    .metric-badge {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 999px;
        display: inline-block;
        margin-top: 4px;
    }
    .metric-badge.green {
        background: #DCFCE7;
        color: #166534;
    }
    .metric-badge.amber {
        background: #FEF3C7;
        color: #92400E;
    }
    .metric-badge.red {
        background: #FEE2E2;
        color: #991B1B;
    }
    .metric-badge.gray {
        background: #E5E7EB;
        color: #374151;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ Load data ------------------
df = load_data(EXCEL_PATH)

st.markdown(
    """
<div class="hero-box">
  <div class="hero-title">Smart Asset Dashboard</div>
  <div class="hero-sub">ภาพรวมการจัดการครุภัณฑ์ & เครื่องมือห้องปฏิบัติการ</div>
</div>
""",
    unsafe_allow_html=True,
)

if df.empty:
    st.error("ไม่พบไฟล์ข้อมูลหรือข้อมูลว่าง: Smart Asset Lab.xlsx")
    st.info("ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์เดียวกับโปรเจกต์ และมีข้อมูลอย่างน้อย 1 แถว")
    st.stop()

status_col = find_status_column(df.columns)

# ------------------ Metrics ------------------
col_all, col_ok, col_repairable, col_broken, col_missing = st.columns(5)
total_assets = len(df)

def count_status(keywords):
    if not status_col:
        return 0
    pattern = "|".join(keywords)
    return df[status_col].astype(str).str.contains(pattern, case=False, na=False).sum()

with col_all:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">รวมครุภัณฑ์ทั้งหมด</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{total_assets:,}</div>', unsafe_allow_html=True)
    st.markdown('<span class="metric-badge gray">ทั้งหมด</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_ok:
    ready_count = count_status(["พร้อมใช้", "พร้อมใช้งาน"])
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">พร้อมใช้งาน</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{ready_count:,}</div>', unsafe_allow_html=True)
    st.markdown('<span class="metric-badge green">สถานะดี</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_repairable:
    repairable_count = count_status(["ชำรุดซ่อมแซมได้", "ซ่อมได้"])
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">ชำรุดซ่อมแซมได้</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{repairable_count:,}</div>', unsafe_allow_html=True)
    st.markdown('<span class="metric-badge amber">ต้องซ่อมแซม</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_broken:
    broken_count = count_status(["ชำรุดซ่อมแซมไม่ได้", "ซ่อมไม่ได้"])
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">ชำรุดซ่อมไม่ได้</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{broken_count:,}</div>', unsafe_allow_html=True)
    st.markdown('<span class="metric-badge red">พิจารณาทดแทน</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_missing:
    missing_count = count_status(["ตรวจไม่พบ", "สูญหาย"])
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-label">ตรวจไม่พบ / สูญหาย</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{missing_count:,}</div>', unsafe_allow_html=True)
    st.markdown('<span class="metric-badge gray">ต้องติดตาม</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ Tabs ------------------
tab_overview, tab_table, tab_edit = st.tabs(["📊 ภาพรวม", "📋 ตารางข้อมูล", "✏️ แก้ไข & บันทึก"])

# Tab 1: Overview
with tab_overview:
    col_chart, col_side = st.columns([2, 1])

    if status_col:
        status_counts = df[status_col].value_counts().reset_index()
        status_counts.columns = ["สถานะ", "จำนวน"]

        with col_chart:
            st.subheader("สัดส่วนตามสถานะครุภัณฑ์")
            base = alt.Chart(status_counts).encode(
                theta=alt.Theta(field="จำนวน", type="quantitative"),
                color=alt.Color(field="สถานะ", type="nominal"),
            )
            pie = base.mark_arc(innerRadius=60)
            text = base.mark_text(radius=80, size=14).encode(text="จำนวน:Q")
            st.altair_chart(pie + text, use_container_width=True)

        with col_side:
            st.subheader("รายละเอียดสถานะ")
            st.dataframe(status_counts, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่พบคอลัมน์ 'สถานะ' ในไฟล์ Excel จึงไม่สามารถสร้างแผนภูมิสถานะได้")

    st.markdown("---")

    dept_col = None
    for c in df.columns:
        if "หน่วยงาน" in str(c) or "แผนก" in str(c):
            dept_col = c
            break

    if dept_col and status_col:
        st.subheader(f"จำนวนครุภัณฑ์ตามหน่วยงาน ({dept_col})")
        dept_counts = (
            df.groupby([dept_col, status_col])
            .size()
            .reset_index(name="จำนวน")
        )

        chart = (
            alt.Chart(dept_counts)
            .mark_bar()
            .encode(
                x=alt.X(f"{dept_col}:N", sort="-y", title="หน่วยงาน"),
                y=alt.Y("จำนวน:Q"),
                color=alt.Color(f"{status_col}:N", title="สถานะ"),
                tooltip=[dept_col, status_col, "จำนวน"],
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("หากต้องการกราฟตามหน่วยงาน กรุณามีคอลัมน์ 'หน่วยงาน' หรือ 'แผนก' ในไฟล์ Excel")

# Tab 2: Table view
with tab_table:
    st.subheader("ตารางข้อมูลครุภัณฑ์ทั้งหมด")

    col_filters = st.columns(3)
    with col_filters[0]:
        search_text = st.text_input("🔍 ค้นหาจากชื่อ / รหัส / AssetID", "")
    with col_filters[1]:
        if status_col:
            status_filter = st.multiselect(
                "กรองตามสถานะ",
                options=sorted(df[status_col].dropna().unique()),
                default=[],
            )
        else:
            status_filter = []
    with col_filters[2]:
        dept_col = None
        for c in df.columns:
            if "หน่วยงาน" in str(c) or "แผนก" in str(c):
                dept_col = c
                break
        if dept_col:
            dept_filter = st.multiselect(
                "กรองตามหน่วยงาน",
                options=sorted(df[dept_col].dropna().unique()),
                default=[],
            )
        else:
            dept_filter = []

    filtered_df = df.copy()
    if search_text:
        s = search_text.lower()
        filtered_df = filtered_df[filtered_df.apply(lambda r: s in str(r).lower(), axis=1)]
    if status_col and status_filter:
        filtered_df = filtered_df[filtered_df[status_col].isin(status_filter)]
    if dept_col and dept_filter:
        filtered_df = filtered_df[filtered_df[dept_col].isin(dept_filter)]

    st.dataframe(filtered_df, use_container_width=True)

# Tab 3: Edit & Save
with tab_edit:
    st.subheader("แก้ไขข้อมูลและบันทึกกลับไปยัง Excel")
    st.info("แก้ไขข้อมูลในตารางด้านล่างได้โดยตรง แล้วกดปุ่มบันทึกเพื่อเขียนกลับไปยังไฟล์ Excel")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="asset_editor",
    )

    if st.button("💾 บันทึกการเปลี่ยนแปลงไปยัง Excel", type="primary"):
        save_data(edited_df, EXCEL_PATH)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว ✅")
        st.cache_data.clear()
        st.experimental_rerun()
