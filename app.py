import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import requests

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Quantum Mobile V14", layout="wide", page_icon="💰")

# --- KẾT NỐI DATABASE ---
# Database sẽ được lưu ngay trên thư mục chạy của Streamlit
conn = sqlite3.connect('quantum_data.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS finance 
                 (date TEXT, type TEXT, category TEXT, amount REAL, note TEXT)''')
    conn.commit()

init_db()

# --- GIAO DIỆN ỨNG DỤNG ---
st.title("🌌 QUANTUM FINANCE V14.0")
st.markdown("---")

# Tab chức năng tối ưu cho Mobile
tab1, tab2, tab3 = st.tabs(["📲 NHẬP LIỆU", "📊 THỐNG KÊ", "📋 LỊCH SỬ"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        st.subheader("Thêm Giao Dịch")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Ngày", datetime.now())
            t_type = st.selectbox("Loại", ["Chi", "Thu"])
        with col2:
            amount = st.number_input("Số tiền (VNĐ)", min_value=0, step=10000)
            category = st.selectbox("Danh mục", ["Ăn uống", "Di chuyển", "Lương", "Mua sắm", "Tiền điện/nước", "Khác"])
        
        note = st.text_input("Ghi chú chi tiết")
        
        submit = st.form_submit_button("LƯU VÀO HỆ THỐNG")
        
        if submit:
            if amount > 0:
                c.execute('INSERT INTO finance VALUES (?,?,?,?,?)', 
                          (date.strftime('%Y-%m-%d'), t_type, category, amount, note))
                conn.commit()
                st.success(f"✅ Đã ghi nhận: -{amount:,.0f} VNĐ" if t_type == "Chi" else f"✅ Đã thêm: +{amount:,.0f} VNĐ")
            else:
                st.error("❌ Vui lòng nhập số tiền lớn hơn 0")

with tab2:
    st.subheader("Phân Tích Chi Tiêu")
    df = pd.read_sql_query("SELECT * FROM finance", conn)
    
    if not df.empty:
        # Tính toán tổng
        total_thu = df[df['type'] == 'Thu']['amount'].sum()
        total_chi = df[df['type'] == 'Chi']['amount'].sum()
        balance = total_thu - total_chi
        
        # Hiển thị số dư
        col_a, col_b = st.columns(2)
        col_a.metric("TỔNG THU", f"{total_thu:,.0f} VNĐ")
        col_b.metric("TỔNG CHI", f"{total_chi:,.0f} VNĐ", delta=f"-{total_chi:,.0f}", delta_color="inverse")
        st.metric("SỐ DƯ HIỆN TẠI", f"{balance:,.0f} VNĐ")

        # Biểu đồ tròn
        df_chi = df[df['type'] == 'Chi']
        if not df_chi.empty:
            fig = px.pie(df_chi, values='amount', names='category', 
                         title="Cơ Cấu Các Khoản Chi", hole=0.4,
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu. Hãy nhập giao dịch đầu tiên!")

with tab3:
    st.subheader("Danh Sách Giao Dịch")
    df_history = pd.read_sql_query("SELECT * FROM finance ORDER BY date DESC", conn)
    if not df_history.empty:
        st.dataframe(df_history, use_container_width=True)
        
        # Nút xóa dữ liệu (Cẩn thận!)
        if st.button("Xóa toàn bộ lịch sử"):
            c.execute("DELETE FROM finance")
            conn.commit()
            st.rerun()
    else:
        st.write("Lịch sử trống.")
