import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 1. CONFIG & CÀI ĐẶT HỆ THỐNG ---
st.set_page_config(page_title="Quantum OS v20", layout="wide", page_icon="⚛️")

# Khởi tạo các biến hệ thống trong Session State
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#38bdf8"
if 'bg_url' not in st.session_state: st.session_state.bg_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
if 'current_app' not in st.session_state: st.session_state.current_app = "Desktop"

# --- 2. MODERN GLASSMORPHISM CSS ---
modern_css = f"""
<style>
    header, footer {{visibility: hidden;}}
    
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("{st.session_state.bg_url}");
        background-size: cover;
        background-position: center;
        color: white;
    }}

    /* Thẻ Card hiện đại */
    .app-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
        transition: 0.3s;
    }}

    /* Nút bấm kiểu OS */
    .stButton>button {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: 0.3s !important;
    }}
    .stButton>button:hover {{
        background: {st.session_state.theme_color}44 !important;
        border: 1px solid {st.session_state.theme_color} !important;
        transform: translateY(-2px);
    }}

    /* Thanh Dock phía dưới */
    .dock-bar {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.5);
        padding: 10px 20px;
        border-radius: 20px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        gap: 15px;
        z-index: 1000;
    }}
</style>
"""
st.markdown(modern_css, unsafe_allow_html=True)

# --- 3. LOGIC KẾT NỐI ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4]).dropna(how='all')

# --- 4. GIAO DIỆN DESKTOP ---
if st.session_state.current_app == "Desktop":
    st.title("🌌 Quantum Workspace")
    st.write(f"Hệ thống ổn định • {datetime.now().strftime('%H:%M')}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Grid ứng dụng chính
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="app-card"><h3>📝</h3><p>Terminal</p></div>', unsafe_allow_html=True)
        if st.button("Mở Nhập liệu"): st.session_state.current_app = "Input"; st.rerun()
    with col2:
        st.markdown('<div class="app-card"><h3>📊</h3><p>Analytics</p></div>', unsafe_allow_html=True)
        if st.button("Mở Thống kê"): st.session_state.current_app = "Stats"; st.rerun()
    with col3:
        st.markdown('<div class="app-card"><h3>⚙️</h3><p>Settings</p></div>', unsafe_allow_html=True)
        if st.button("Cài đặt Hệ thống"): st.session_state.current_app = "Settings"; st.rerun()

# --- 5. CỬA SỔ ỨNG DỤNG ---
elif st.session_state.current_app == "Input":
    st.subheader("📝 NHẬP LIỆU HỆ THỐNG")
    with st.container(border=True):
        with st.form("input_form"):
            col_a, col_b = st.columns(2)
            d = col_a.date_input("Ngày", datetime.now())
            t = col_a.selectbox("Loại", ["Chi", "Thu"])
            amt = col_b.number_input("Số tiền", min_value=0)
            cat = col_b.selectbox("Danh mục", ["Ăn uống", "Lương", "Giải trí", "Khác"])
            note = st.text_input("Ghi chú")
            if st.form_submit_button("XÁC NHẬN GIAO DỊCH"):
                df = get_data()
                new_row = pd.DataFrame([{"date":str(d), "type":t, "category":cat, "amount":amt, "note":note}])
                conn.update(spreadsheet=url, data=pd.concat([df, new_row]))
                st.success("Dữ liệu đã được nạp!")

elif st.session_state.current_app == "Settings":
    st.subheader("⚙️ CÀI ĐẶT HỆ THỐNG")
    with st.container(border=True):
        st.write("Tùy chỉnh giao diện")
        new_bg = st.text_input("Link hình nền (URL)", st.session_state.bg_url)
        new_color = st.color_picker("Màu chủ đạo (Accent Color)", st.session_state.theme_color)
        
        if st.button("ÁP DỤNG THAY ĐỔI"):
            st.session_state.bg_url = new_bg
            st.session_state.theme_color = new_color
            st.rerun()
        
        st.markdown("---")
        st.write("Thông tin phiên bản: Quantum OS v20.0 (Stable)")

# --- 6. THANH DOCK ĐIỀU HƯỚNG ---
if st.session_state.current_app != "Desktop":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🏠 VỀ MÀN HÌNH CHÍNH"):
        st.session_state.current_app = "Desktop"
        st.rerun()
