import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="Titanium Permanent", layout="wide")

# --- KẾT NỐI LÕI (VĨNH VIỄN) ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    # ttl=0 để lấy dữ liệu tươi nhất, không qua bộ nhớ đệm
    return conn.read(spreadsheet=url, ttl=0).dropna(how='all')

# --- GIAO DIỆN HIỆN ĐẠI ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .main-button { background: #238636 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
menu = st.sidebar.selectbox("HỆ THỐNG", ["📊 Dashboard", "➕ Giao dịch", "💾 Data Vault"])

if menu == "📊 Dashboard":
    st.title("💎 Titanium Dashboard")
    df = fetch_data()
    
    if not df.empty:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        thu = df[df['type'] == 'Thu']['amount'].sum()
        chi = df[df['type'] == 'Chi']['amount'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("SỐ DƯ HIỆN TẠI", f"{(thu - chi):,.0f} đ")
        c2.metric("TỔNG CHI TIÊU", f"{chi:,.0f} đ", delta=f"-{chi:,.0f}", delta_color="inverse")
        
        st.subheader("Lịch sử giao dịch")
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.warning("Hệ thống trống. Vui lòng nhập dữ liệu.")

elif menu == "➕ Giao dịch":
    st.title("💸 Nhập giao dịch")
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        date = col1.date_input("Ngày", datetime.now())
        t_type = col1.selectbox("Loại", ["Thu", "Chi"])
        amount = col2.number_input("Số tiền", min_value=0, step=1000)
        cat = col2.selectbox("Hạng mục", ["Ăn uống", "Lương", "Tiền nhà", "Giải trí", "Khác"])
        note = st.text_input("Ghi chú")
        
        if st.form_submit_button("LƯU VÀO ĐÁM MÂY", use_container_width=True):
            if amount > 0:
                # FIX LỖI: Lấy dữ liệu -> Nối dòng -> Dùng update thay vì create
                df_old = fetch_data()
                new_row = pd.DataFrame([{"date": str(date), "type": t_type, "category": cat, "amount": amount, "note": note}])
                updated_df = pd.concat([df_old, new_row], ignore_index=True)
                
                # SỬ DỤNG UPDATE ĐỂ GHI ĐÈ LÊN FILE CŨ
                conn.update(spreadsheet=url, data=updated_df)
                
                st.success("Dữ liệu đã được khóa vĩnh viễn!")
                time.sleep(1)
                st.rerun()

elif menu == "💾 Data Vault":
    st.title("🔐 Kho dữ liệu bảo mật")
    df = fetch_data()
    
    st.write("Xuất dữ liệu dự phòng ra file Excel/CSV để lưu trữ trên máy tính.")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 TẢI XUỐNG DỮ LIỆU DỰ PHÒNG", data=csv, file_name="backup.csv", mime='text/csv')
    
    st.markdown("---")
    if st.checkbox("Kích hoạt chế độ Reset hệ thống"):
        if st.button("🗑️ XÓA VĨNH VIỄN TOÀN BỘ DỮ LIỆU"):
            empty_df = pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])
            conn.update(spreadsheet=url, data=empty_df)
            st.rerun()
