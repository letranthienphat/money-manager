import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. THIẾT LẬP HỆ THỐNG ---
st.set_page_config(page_title="Titanium Infinity", layout="wide", page_icon="♾️")

# --- 2. GIAO DIỆN DARK-PREMIUM (Chống lóa & Hiện đại) ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .stApp { background-color: #050505; color: #e0e0e0; }
    .stMetric { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #d4af37;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d4af37, #b8860b) !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. KẾT NỐI LÕI (CORE ENGINE) ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def load_quantum_data():
    """Tải dữ liệu tươi nhất từ Cloud"""
    try:
        df = conn.read(spreadsheet=url, ttl="0s") # Ép buộc không dùng cache
        df = df.dropna(how='all')
        if not df.empty:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])

# --- 4. ĐIỀU HƯỚNG ---
menu = st.sidebar.radio("HỆ THỐNG", ["📊 DASHBOARD", "💸 GIAO DỊCH", "🔐 DATA VAULT"])

# --- MODULE 1: DASHBOARD ---
if menu == "📊 DASHBOARD":
    st.title("♾️ Titanium Overview")
    df = load_quantum_data()
    
    total_thu = df[df['type'] == 'Thu']['amount'].sum()
    total_chi = df[df['type'] == 'Chi']['amount'].sum()
    balance = total_thu - total_chi
    
    c1, c2, c3 = st.columns(3)
    c1.metric("TÀI SẢN RÒNG", f"{balance:,.0f} đ")
    c2.metric("TỔNG THU", f"{total_thu:,.0f} đ")
    c3.metric("TỔNG CHI", f"{total_chi:,.0f} đ", delta=f"-{total_chi:,.0f}", delta_color="inverse")
    
    st.markdown("---")
    st.subheader("Nhật ký 5 giao dịch cuối")
    st.table(df.tail(5))

# --- MODULE 2: GIAO DỊCH (SỬA LỖI VĨNH VIỄN) ---
elif menu == "💸 GIAO DỊCH":
    st.header("📲 Lệnh Tài Chính Mới")
    
    with st.form("infinity_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            d = st.date_input("Ngày thực hiện", datetime.now())
            t = st.selectbox("Loại lệnh", ["Chi", "Thu"])
        with col2:
            amt = st.number_input("Số tiền (đ)", min_value=0, step=1000)
            cat = st.selectbox("Danh mục", ["Ăn uống", "Lương", "Mua sắm", "Di chuyển", "Khác"])
        
        note = st.text_input("Ghi chú mã hóa")
        submit = st.form_submit_button("XÁC NHẬN ĐỒNG BỘ")
        
        if submit:
            if amt > 0:
                with st.spinner("Đang đẩy dữ liệu lên Cloud..."):
                    # 1. Đọc dữ liệu hiện tại
                    current_df = load_quantum_data()
                    
                    # 2. Tạo dòng mới
                    new_entry = pd.DataFrame([{
                        "date": str(d),
                        "type": t,
                        "category": cat,
                        "amount": float(amt),
                        "note": note
                    }])
                    
                    # 3. Kết hợp dữ liệu
                    final_df = pd.concat([current_df, new_entry], ignore_index=True)
                    
                    # 4. SỬ DỤNG .UPDATE THAY VÌ .CREATE ĐỂ FIX LỖI
                    conn.update(spreadsheet=url, data=final_df)
                    
                    st.success("✅ Đã khóa dữ liệu vĩnh viễn trên Cloud!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("⚠️ Vui lòng nhập số tiền!")

# --- MODULE 3: DATA VAULT (TÍNH NĂNG VIP) ---
elif menu == "🔐 DATA VAULT":
    st.header("🔐 Kho Lưu Trữ Titanium")
    df = load_quantum_data()
    
    st.info("Dữ liệu của bạn được lưu trữ đồng thời trên Google Sheets và có thể tải về máy.")
    
    # Tính năng Backup Excel
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 TẢI BACKUP (.CSV)", csv, "titanium_backup.csv", "text/csv")
    
    st.markdown("---")
    st.warning("⚠️ QUẢN TRỊ VIÊN: Xóa dữ liệu sẽ không thể khôi phục.")
    if st.checkbox("Xác nhận quyền xóa"):
        if st.button("🗑️ RESET TOÀN BỘ"):
            empty_df = pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])
            conn.update(spreadsheet=url, data=empty_df)
            st.rerun()
