import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. HỆ THỐNG ĐIỀU KHIỂN ---
st.set_page_config(page_title="Quantum OS V22", layout="wide", page_icon="💎")

# Khởi tạo trạng thái hệ thống
if 'app_state' not in st.session_state: st.session_state.app_state = "Dashboard"

# --- 2. GIAO DIỆN MODERN OS (ĐÃ FIX LÓA) ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .stApp {
        background: #0f172a;
        background-image: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f1f5f9;
    }
    /* Thẻ hiển thị số dư */
    .balance-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    /* Nút bấm điều hướng */
    .nav-button {
        background: #1e293b !important;
        border: 1px solid #38bdf8 !important;
        color: #38bdf8 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BỘ MÁY XỬ LÝ DỮ LIỆU (CORE ENGINE) ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def sync_data():
    """Tải dữ liệu và đảm bảo đúng định dạng số"""
    try:
        df = conn.read(spreadsheet=url, ttl=0)
        df = df.dropna(how='all')
        if not df.empty:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])

# --- 4. GIAO DIỆN CHÍNH (CONTROL CENTER) ---

# Thanh SideBar thu gọn
with st.sidebar:
    st.title("💠 QUANTUM V22")
    if st.button("🏠 MÀN HÌNH CHÍNH"): st.session_state.app_state = "Dashboard"; st.rerun()
    if st.button("➕ THÊM/TRỪ TIỀN"): st.session_state.app_state = "Terminal"; st.rerun()
    if st.button("📜 LỊCH SỬ CHI TIẾT"): st.session_state.app_state = "Ledger"; st.rerun()
    st.markdown("---")
    st.caption("Version: 22.0.1 Stable")

# --- MODULE: MÀN HÌNH CHÍNH ---
if st.session_state.app_state == "Dashboard":
    st.subheader("Hệ thống Tài chính Lượng tử")
    df = sync_data()
    
    # Tính toán số dư
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
    c2.metric("TỔNG CHI (-)", f"{total_chi:,.0f} VNĐ", delta=f"-{total_chi:,.0f}", delta_color="inverse")

# --- MODULE: THÊM/TRỪ TIỀN (FIXED) ---
elif st.session_state.app_state == "Terminal":
    st.header("📲 Giao dịch mới")
    
    with st.container(border=True):
        with st.form("quantum_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            d = col_a.date_input("Ngày", datetime.now())
            t = col_a.selectbox("Loại giao dịch", ["Chi", "Thu"], help="Chọn Thu để cộng tiền, Chi để trừ tiền")
            
            amt = col_b.number_input("Số tiền (VNĐ)", min_value=0, step=1000, format="%d")
            cat = col_b.selectbox("Danh mục", ["Ăn uống", "Lương", "Mua sắm", "Di chuyển", "Khác"])
            
            note = st.text_input("Ghi chú nội dung")
            
            submit = st.form_submit_button("🚀 XÁC NHẬN GỬI DỮ LIỆU")
            
            if submit:
                if amt > 0:
                    with st.spinner("Đang kết nối Lõi dữ liệu..."):
                        # Bước 1: Lấy dữ liệu mới nhất
                        df_current = sync_data()
                        
                        # Bước 2: Tạo dòng mới (Đảm bảo amount là float)
                        new_data = pd.DataFrame([{
                            "date": d.strftime('%Y-%m-%d'),
                            "type": str(t),
                            "category": str(cat),
                            "amount": float(amt),
                            "note": str(note)
                        }])
                        
                        # Bước 3: Gộp và Cập nhật
                        updated_df = pd.concat([df_current, new_data], ignore_index=True)
                        
                        # Sử dụng create để ghi đè an toàn
                        conn.create(spreadsheet=url, data=updated_df)
                        
                        st.success(f"Đã thực hiện thành công giao dịch {t}!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Vui lòng nhập số tiền hợp lệ!")

# --- MODULE: LỊCH SỬ ---
elif st.session_state.app_state == "Ledger":
    st.header("📜 Nhật ký hệ thống")
    df = sync_data()
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        
        # Nút xóa dữ liệu (Backup trước khi dùng)
        if st.checkbox("Mở khóa quyền Xóa"):
            if st.button("🗑️ XÓA TOÀN BỘ DỮ LIỆU"):
                conn.create(spreadsheet=url, data=pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note']))
                st.rerun()
