import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- CONFIG & OS STYLE ---
st.set_page_config(page_title="Quantum OS v19", layout="wide", page_icon="🖥️")

# CSS tạo giao diện Hệ điều hành có hình nền và giảm lóa
quantum_os_style = """
<style>
    /* Hình nền Desktop Quantum */
    .stApp {
        background: linear-gradient(rgba(10, 10, 20, 0.8), rgba(10, 10, 20, 0.8)), 
                    url("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        color: #cfd8dc;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }

    /* Tắt thành phần mặc định */
    header, footer {visibility: hidden;}

    /* Style cho các Icon trên màn hình chính */
    .os-icon {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border_radius: 15px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: 0.3s;
        cursor: pointer;
        color: white;
    }
    .os-icon:hover {
        background: rgba(0, 255, 255, 0.2);
        border: 1px solid #00ffff;
        transform: translateY(-5px);
    }

    /* Các cửa sổ ứng dụng khi mở */
    .stTable, .stDataFrame, [data-testid="stVerticalBlock"] > div {
        background: rgba(15, 23, 42, 0.9) !important;
        border-radius: 12px;
        border: 1px solid #1e293b;
    }
    
    /* Chỉnh nút bấm cho đỡ lóa */
    .stButton>button {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 8px;
        width: 100%;
    }
</style>
"""
st.markdown(quantum_os_style, unsafe_allow_html=True)

# --- KHỞI TẠO HỆ THỐNG ---
if 'current_app' not in st.session_state:
    st.session_state.current_app = "Desktop"

def open_app(app_name):
    st.session_state.current_app = app_name

# Kết nối Google Sheets (Vẫn dùng link cũ trong Secrets)
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4]).dropna(how='all')

# --- MÀN HÌNH CHÍNH (DESKTOP) ---
if st.session_state.current_app == "Desktop":
    st.title("⚡ QUANTUM OS")
    st.write(f"Hôm nay: {datetime.now().strftime('%A, %d/%m/%Y')}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 INPUT TERMINAL\n(Nhập liệu)"):
            open_app("Input")
            st.rerun()
            
    with col2:
        if st.button("📊 DATA NEXUS\n(Thống kê)"):
            open_app("Stats")
            st.rerun()
            
    with col3:
        if st.button("💾 RECOVERY PORTAL\n(QR Backup)"):
            open_app("QR")
            st.rerun()

# --- CÁC CỬA SỔ ỨNG DỤNG ---
if st.session_state.current_app != "Desktop":
    if st.button("⬅️ QUAY LẠI DESKTOP"):
        open_app("Desktop")
        st.rerun()
    st.markdown("---")

    if st.session_state.current_app == "Input":
        st.subheader("🖥️ Ứng dụng: NHẬP LIỆU")
        with st.form("input_form"):
            date = st.date_input("Thời gian", datetime.now())
            t_type = st.selectbox("Loại", ["Chi", "Thu"])
            amt = st.number_input("Số tiền", min_value=0)
            cat = st.selectbox("Danh mục", ["Ăn uống", "Di chuyển", "Lương", "Khác"])
            note = st.text_input("Ghi chú")
            if st.form_submit_button("LƯU VÀO HỆ THỐNG"):
                df = get_data()
                new_row = pd.DataFrame([{"date":str(date), "type":t_type, "category":cat, "amount":amt, "note":note}])
                conn.update(spreadsheet=url, data=pd.concat([df, new_row]))
                st.success("Đã đồng bộ vĩnh viễn!")

    elif st.session_state.current_app == "Stats":
        st.subheader("🖥️ Ứng dụng: THỐNG KÊ")
        df = get_data()
        if not df.empty:
            total_chi = pd.to_numeric(df[df['type']=='Chi']['amount']).sum()
            st.metric("TỔNG CHI TIÊU", f"{total_chi:,.0f} VNĐ")
            fig = px.pie(df[df['type']=='Chi'], values='amount', names='category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("Dữ liệu trống.")

    elif st.session_state.current_app == "QR":
        st.subheader("🖥️ Ứng dụng: SAO LƯU QR")
        st.info("Chức năng mã hóa dữ liệu thành ma trận QR để lưu trữ offline.")
        # Bạn có thể dán lại code QR ở V18 vào đây
