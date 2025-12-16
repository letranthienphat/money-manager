# --- BƯỚC 1: CÀI ĐẶT ---
!pip install streamlit pyngrok -q
import os

# --- BƯỚC 2: TẠO FILE APP ---
with open('app.py', 'w', encoding='utf-8') as f:
    f.write("""
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Quantum Mobile V13", layout="wide")

# Lấy IP để người dùng copy trực tiếp trên App
import requests
endpoint_ip = requests.get('https://ipv4.icanhazip.com').text.strip()

conn = sqlite3.connect('quantum_v13.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS finance (date TEXT, type TEXT, cat TEXT, amount REAL, note TEXT)')
conn.commit()

st.title("🌌 QUANTUM MOBILE V13")
st.info(f"🔑 Mật khẩu truy cập (nếu web hỏi): {endpoint_ip}")

tabs = st.tabs(["📲 Nhập liệu", "📊 Thống kê", "📋 Lịch sử"])

with tabs[0]:
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        d = col1.date_input("Ngày", datetime.now())
        t = col2.selectbox("Loại", ["Chi", "Thu"])
        cat = st.selectbox("Danh mục", ["Ăn uống", "Di chuyển", "Lương", "Mua sắm", "Khác"])
        amt = st.number_input("Số tiền (VNĐ)", min_value=0, step=1000)
        note = st.text_input("Ghi chú")
        if st.form_submit_button("LƯU GIAO DỊCH"):
            c.execute('INSERT INTO finance VALUES (?,?,?,?,?)', (d.strftime('%Y-%m-%d'), t, cat, amt, note))
            conn.commit()
            st.success("✅ Đã lưu!")

with tabs[1]:
    df = pd.read_sql_query("SELECT * FROM finance", conn)
    if not df.empty:
        thu = df[df['type']=='Thu']['amount'].sum()
        chi = df[df['type']=='Chi']['amount'].sum()
        st.metric("SỐ DƯ HIỆN TẠI", f"{thu - chi:,.0f} VNĐ", f"Thu: {thu:,.0f} | Chi: {chi:,.0f}")
        
        fig = px.pie(df[df['type']=='Chi'], values='amount', names='cat', title="Cơ cấu chi tiêu")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Chưa có dữ liệu.")

with tabs[2]:
    df_history = pd.read_sql_query("SELECT * FROM finance ORDER BY date DESC", conn)
    st.dataframe(df_history, use_container_width=True)
    """)

# --- BƯỚC 3: CHẠY VÀ HIỆN LINK ---
print("Đang khởi tạo đường truyền...")
get_ipython().system_raw('streamlit run app.py &')
!npx localtunnel --port 8501
