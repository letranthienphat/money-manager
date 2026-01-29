import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
import time

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Titanium Hardcore", layout="wide")

# --- 2. KẾT NỐI TRỰC TIẾP (FIX LỖI GHI) ---
# Lấy URL từ Secrets
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

def get_sheet():
    # Kết nối bằng cách giả lập quyền (Yêu cầu Sheet phải ở chế độ 'Anyone with link can Edit')
    gc = gspread.public(SHEET_URL) # Thử kết nối công khai
    # Nếu sheet của bạn cần quyền cao hơn, chúng ta sẽ xử lý sau. 
    # Nhưng cách tốt nhất là dùng thư viện gspread chuẩn:
    try:
        # Cách này dùng link sheet trực tiếp và ghi vào dòng cuối
        return gspread.open_by_url(SHEET_URL).get_worksheet(0)
    except Exception as e:
        st.error("Lỗi quyền truy cập! Hãy đảm bảo Sheet đã chọn 'Anyone with link can EDIT'")
        return None

# --- 3. GIAO DIỆN ---
st.title("💳 Titanium Hardcore Edition")
st.info("Bản này sử dụng kết nối trực tiếp, không qua Server trung gian.")

tab1, tab2 = st.tabs(["📊 Tổng quan", "➕ Nhập liệu"])

sheet = get_sheet()

if sheet:
    # Đọc dữ liệu
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    with tab1:
        if not df.empty:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            thu = df[df['type'] == 'Thu']['amount'].sum()
            chi = df[df['type'] == 'Chi']['amount'].sum()
            st.metric("SỐ DƯ THỰC TẾ", f"{thu - chi:,.0f} đ")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.write("Chưa có dữ liệu.")

    with tab2:
        with st.form("hardcore_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            amt = col1.number_input("Số tiền", min_value=0, step=1000)
            t_type = col1.selectbox("Loại", ["Thu", "Chi"])
            cat = col2.selectbox("Mục", ["Ăn uống", "Lương", "Mua sắm", "Khác"])
            note = col2.text_input("Ghi chú")
            
            if st.form_submit_button("LƯU NGAY (KHÔNG LỖI)"):
                if amt > 0:
                    # GHI TRỰC TIẾP VÀO DÒNG CUỐI (APPEND)
                    new_row = [datetime.now().strftime("%d/%m/%Y"), t_type, cat, amt, note]
                    sheet.append_row(new_row)
                    st.success("Đã ghi thành công!")
                    time.sleep(1)
                    st.rerun()
