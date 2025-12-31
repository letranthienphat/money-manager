import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. HỆ THỐNG ĐIỀU KHIỂN ---
st.set_page_config(page_title="Quantum OS V22.1", layout="wide", page_icon="💎")

# Khởi tạo trạng thái hệ thống nếu chưa có
if 'app_state' not in st.session_state: 
    st.session_state.app_state = "Dashboard"

# --- 2. GIAO DIỆN HIỆN ĐẠI (Sửa lỗi hiển thị) ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .stApp { background: #0f172a; color: #f1f5f9; }
    .balance-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BỘ MÁY XỬ LÝ DỮ LIỆU ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def sync_data():
    try:
        # ttl=0 để luôn lấy dữ liệu mới nhất từ Google Sheets
        df = conn.read(spreadsheet=url, ttl=0)
        df = df.dropna(how='all')
        if not df.empty:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])

# --- 4. THANH ĐIỀU HƯỚNG (SIDEBAR) ---
with st.sidebar:
    st.title("💠 QUANTUM V22.1")
    # Sử dụng button để chuyển trạng thái app
    if st.button("🏠 DASHBOARD", use_container_width=True): 
        st.session_state.app_state = "Dashboard"
        st.rerun()
    if st.button("➕ THÊM/TRỪ TIỀN", use_container_width=True): 
        st.session_state.app_state = "Terminal"
        st.rerun()
    if st.button("📜 LỊCH SỬ", use_container_width=True): 
        st.session_state.app_state = "Ledger"
        st.rerun()
    st.markdown("---")
    st.caption("Status: Online | Python 3.13")

# --- 5. CỬA SỔ ỨNG DỤNG ---

# --- MODULE: MÀN HÌNH CHÍNH ---
if st.session_state.app_state == "Dashboard":
    st.title("🌌 Quantum Dashboard")
    df = sync_data()
    
    total_thu = df[df['type'] == 'Thu']['amount'].sum()
    total_chi = df[df['type'] == 'Chi']['amount'].sum()
    balance = total_thu - total_chi
    
    st.markdown(f"""
    <div class="balance-card">
        <p style="color: #94a3b8; margin:0;">SỐ DƯ HIỆN TẠI</p>
        <h1 style="color: #38bdf8; font-size: 3rem; margin:0;">{balance:,.0f} <span style="font-size: 1.2rem;">VNĐ</span></h1>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("TỔNG THU (+)", f"{total_thu:,.0f} VNĐ")
    c2.metric("TỔNG CHI (-)", f"{total_chi:,.0f} VNĐ", delta_color="inverse")

# --- MODULE: THÊM/TRỪ TIỀN (SỬA LỖI FORM) ---
elif st.session_state.app_state == "Terminal":
    st.header("📲 Giao dịch Lượng tử")
    
    # Tạo container chứa form để đảm bảo tính bao đóng
    with st.container():
        with st.form("quantum_terminal_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            
            with col_a:
                d = st.date_input("Ngày thực thi", datetime.now())
                t = st.selectbox("Phân loại", ["Chi", "Thu"])
                
            with col_b:
                amt = st.number_input("Giá trị năng lượng (VNĐ)", min_value=0, step=1000)
                cat = st.selectbox("Danh mục", ["Ăn uống", "Lương", "Mua sắm", "Di chuyển", "Khác"])
            
            note = st.text_input("Ghi chú mã hóa")
            
            # Nút submit PHẢI nằm trong 'with st.form'
            submitted = st.form_submit_button("🚀 XÁC NHẬN GỬI")
            
            if submitted:
                if amt > 0:
                    with st.spinner("Đang kết nối Lõi dữ liệu..."):
                        df_current = sync_data()
                        new_data = pd.DataFrame([{
                            "date": d.strftime('%Y-%m-%d'),
                            "type": t,
                            "category": cat,
                            "amount": float(amt),
                            "note": note
                        }])
                        updated_df = pd.concat([df_current, new_data], ignore_index=True)
                        conn.create(spreadsheet=url, data=updated_df)
                        
                        st.toast("Dữ liệu đã được nạp thành công!", icon="✅")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("⚠️ Số tiền phải lớn hơn 0.")

# --- MODULE: LỊCH SỬ ---
elif st.session_state.app_state == "Ledger":
    st.header("📜 Nhật ký Hệ thống")
    df = sync_data()
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Nhật ký hiện tại đang trống.")
