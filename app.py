import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- 1. CẤU HÌNH GIAO DIỆN HIỆN ĐẠI ---
st.set_page_config(page_title="Titanium Simple", layout="wide", page_icon="📑")

st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #ffffff; }
    /* Card hiển thị số dư */
    .balance-box {
        background: #1c2128;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #30363d;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Nút bấm lớn dễ chạm */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        height: 3em;
        background-color: #238636 !important;
        border: none !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. KẾT NỐI SHEET TRỰC TIẾP ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Đọc trực tiếp, bỏ qua cache để dữ liệu luôn mới
    df = conn.read(spreadsheet=url, ttl=0)
    return df.dropna(how='all')

# --- 3. GIAO DIỆN ĐIỀU HƯỚNG ---
# Dùng thanh chọn đơn giản, không lỗi chuyển mục
menu = st.radio("CHỌN CHỨC NĂNG:", ["🏠 TỔNG QUAN", "➕ NHẬP CHI TIÊU", "💰 NHẬP THU NHẬP", "📂 QUẢN LÝ"], horizontal=True)

df = get_data()

# Ép kiểu số để tính toán (Tránh lỗi cộng trừ)
if not df.empty:
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

# --- 4. XỬ LÝ CÁC MỤC ---

if menu == "🏠 TỔNG QUAN":
    st.markdown("<br>", unsafe_allow_html=True)
    thu = df[df['type'] == 'Thu']['amount'].sum()
    chi = df[df['type'] == 'Chi']['amount'].sum()
    balance = thu - chi
    
    st.markdown(f"""
    <div class="balance-box">
        <p style="color: #8b949e; margin: 0;">SỐ DƯ HIỆN TẠI</p>
        <h1 style="color: #58a6ff; font-size: 3rem; margin: 10px 0;">{balance:,.0f} đ</h1>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("Tổng Thu (+)", f"{thu:,.0f} đ")
    c2.metric("Tổng Chi (-)", f"{chi:,.0f} đ", delta_color="inverse")
    
    st.write("### 🕒 Giao dịch gần nhất")
    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

elif menu == "➕ NHẬP CHI TIÊU" or menu == "💰 NHẬP THU NHẬP":
    is_chi = "Chi" if "CHI" in menu else "Thu"
    st.subheader(f"Ghi nhận khoản {is_chi}")
    
    with st.form("quick_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        amt = col1.number_input("Số tiền (đ)", min_value=0, step=1000)
        cat = col2.selectbox("Hạng mục", ["Ăn uống", "Lương", "Mua sắm", "Di chuyển", "Giải trí", "Khác"])
        note = st.text_input("Ghi chú/Nội dung")
        
        if st.form_submit_button(f"XÁC NHẬN {is_chi.upper()}"):
            if amt > 0:
                with st.spinner("Đang ghi vào Sheet..."):
                    # Tạo dòng mới
                    new_row = pd.DataFrame([{
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "type": is_chi,
                        "category": cat,
                        "amount": float(amt),
                        "note": note
                    }])
                    # Nối vào dữ liệu cũ
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    # Ghi đè lại Sheet (Dùng update cho file đã có sẵn)
                    conn.update(spreadsheet=url, data=updated_df)
                    st.success(f"Đã lưu khoản {is_chi} thành công!")
                    time.sleep(1)
                    st.rerun()

elif menu == "📂 QUẢN LÝ":
    st.subheader("Dữ liệu thô từ Sheet")
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ XÓA DÒNG CUỐI CÙNG"):
        if not df.empty:
            updated_df = df.iloc[:-1]
            conn.update(spreadsheet=url, data=updated_df)
            st.warning("Đã xóa giao dịch gần nhất!")
            st.rerun()
