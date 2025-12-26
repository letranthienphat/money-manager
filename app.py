import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time

# --- 1. CORE SYSTEM CONFIG ---
st.set_page_config(page_title="Quantum OS v21", layout="wide", page_icon="🌐")

if 'hide_balance' not in st.session_state: st.session_state.hide_balance = False
if 'current_app' not in st.session_state: st.session_state.current_app = "Dashboard"

# --- 2. ADVANCED NEBULA CSS ---
st.markdown(f"""
<style>
    header, footer {{visibility: hidden;}}
    .stApp {{
        background: #05050a;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.15) 0, transparent 50%);
        color: #e2e8f0;
    }}
    
    /* Hiệu ứng Glassmorphism cho Card */
    .quantum-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 15px;
    }}

    /* Sidebar Custom */
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 10, 20, 0.95) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.3);
    }}

    /* Animation cho nút bấm */
    .stButton>button {{
        width: 100%;
        border-radius: 10px !important;
        background: rgba(56, 189, 248, 0.1) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .stButton>button:hover {{
        background: rgba(56, 189, 248, 0.3) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    df = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4])
    df = df.dropna(how='all')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

# --- 4. SIDEBAR NAVIGATION (SYSTEM TRAY) ---
with st.sidebar:
    st.markdown("### 💠 QUANTUM CORE")
    st.session_state.current_app = st.radio("ỨNG DỤNG", 
        ["Dashboard", "Terminal (Nhập)", "Nexus (Thống kê)", "Ledger (Lịch sử)", "Settings"],
        label_visibility="collapsed")
    
    st.markdown("---")
    st.session_state.hide_balance = st.checkbox("Ẩn số dư (Privacy)")
    if st.button("🚀 Khởi động lại"): st.rerun()

# --- 5. APP MODULES ---

# --- MODULE: DASHBOARD ---
if st.session_state.current_app == "Dashboard":
    st.title("🌌 Welcome, User")
    st.write(f"Trạng thái hệ thống: **Mượt mà** | {datetime.now().strftime('%d/%m/%Y')}")
    
    df = load_data()
    total_chi = df[df['type']=='Chi']['amount'].sum()
    total_thu = df[df['type']=='Thu']['amount'].sum()
    balance = total_thu - total_chi
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
        val = "****" if st.session_state.hide_balance else f"{balance:,.0f} VNĐ"
        st.metric("SỐ DƯ KHẢ DỤNG", val)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
        val_chi = "****" if st.session_state.hide_balance else f"{total_chi:,.0f}"
        st.metric("TỔNG CHI THÁNG", val_chi, delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="quantum-card">', unsafe_allow_html=True)
        st.metric("UPTIME HỆ THỐNG", "99.9%")
        st.markdown('</div>', unsafe_allow_html=True)

    # Biểu đồ nhanh trên Desktop
    st.subheader("📈 Xu hướng tài chính")
    fig_line = px.line(df.sort_values('date'), x='date', y='amount', color='type', 
                       markers=True, template="plotly_dark",
                       color_discrete_map={'Thu':'#4ade80', 'Chi':'#f87171'})
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

# --- MODULE: TERMINAL ---
elif st.session_state.current_app == "Terminal (Nhập)":
    st.header("⌨️ INPUT TERMINAL")
    with st.container():
        with st.form("input_v21"):
            c1, c2 = st.columns(2)
            d = c1.date_input("Ngày giao dịch", datetime.now())
            t = c1.selectbox("Loại", ["Chi", "Thu"])
            amt = c2.number_input("Giá trị (VNĐ)", min_value=0)
            cat = c2.selectbox("Danh mục", ["Ăn uống", "Lương", "Di chuyển", "Mua sắm", "Đầu tư", "Khác"])
            note = st.text_input("Nội dung chi tiết")
            
            if st.form_submit_button("THỰC THI LỆNH"):
                with st.status("Đang mã hóa dữ liệu..."):
                    df_old = load_data()
                    new_r = pd.DataFrame([{"date":str(d), "type":t, "category":cat, "amount":amt, "note":note}])
                    conn.update(spreadsheet=url, data=pd.concat([df_old, new_r]))
                    st.success("✅ Giao dịch đã được đồng bộ vào Chuỗi Lượng Tử!")

# --- MODULE: NEXUS (STATS) ---
elif st.session_state.current_app == "Nexus (Thống kê)":
    st.header("📊 DATA NEXUS")
    df = load_data()
    
    # Biểu đồ Sunburst (Đa tầng) hoặc Pie 3D
    df_chi = df[df['type']=='Chi']
    if not df_chi.empty:
        fig_3d = px.pie(df_chi, values='amount', names='category', hole=0.5,
                        color_discrete_sequence=px.colors.sequential.Agsunset)
        st.plotly_chart(fig_3d, use_container_width=True)
        
        # Thống kê danh mục cao nhất
        top_cat = df_chi.groupby('category')['amount'].sum().idxmax()
        st.warning(f"Cảnh báo: Bạn đang chi nhiều nhất vào mục **{top_cat}**")

# --- MODULE: SETTINGS ---
elif st.session_state.current_app == "Settings":
    st.header("⚙️ SYSTEM SETTINGS")
    st.write("Cấu hình hệ điều hành")
    st.color_picker("Thay đổi màu Neon chủ đạo", "#38bdf8")
    st.button("Dọn dẹp bộ nhớ đệm (Cache)")
    st.button("Xuất file Backup (Excel)")
