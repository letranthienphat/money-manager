import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time

# --- 1. CẤU HÌNH HỆ THỐNG SIÊU CẤP ---
st.set_page_config(page_title="Titanium Ultimate", layout="wide", page_icon="⚡")

# --- 2. GIAO DIỆN LUXURY DARK (Tối ưu cảm ứng) ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Thiết kế thẻ Card bóng bẩy */
    .element-container img { border-radius: 20px; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #111, #222);
        border: 1px solid #333;
        padding: 20px !important;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Nút bấm lớn cho điện thoại */
    .stButton>button {
        height: 3.5rem;
        border-radius: 15px !important;
        background: #222 !important;
        color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        font-size: 18px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÕI KẾT NỐI (VĨNH CỬU) ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(spreadsheet=url, ttl="0s")
        df = df.dropna(how='all')
        if not df.empty:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])

# --- 4. THANH ĐIỀU HƯỚNG DOCK (Nâng cấp VIP) ---
# Đưa menu ra giữa màn hình hoặc Sidebar tùy chỉnh để không bị "liệt"
with st.sidebar:
    selected = option_menu(
        menu_title="QUANTUM CORE",
        options=["TRANG CHỦ", "THU/CHI", "NHẬT KÝ", "HỆ THỐNG"],
        icons=["house-fill", "plus-circle-fill", "journal-text", "cpu-fill"],
        menu_icon="shimmer",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#000"},
            "icon": {"color": "#00d4ff", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "color": "#fff"},
            "nav-link-selected": {"background-color": "#00d4ff", "color": "#000"},
        }
    )

# --- 5. ĐIỀU PHỐI TÁC VỤ ---

df = get_db()

if selected == "TRANG CHỦ":
    st.title("⚡ Dashboard")
    
    thu = df[df['type'] == 'Thu']['amount'].sum()
    chi = df[df['type'] == 'Chi']['amount'].sum()
    balance = thu - chi
    
    col1, col2 = st.columns(2)
    col1.metric("SỐ DƯ TỔNG", f"{balance:,.0f} đ")
    col2.metric("CHI TRONG THÁNG", f"{chi:,.0f} đ", delta_color="inverse")
    
    st.markdown("### Giao dịch mới nhất")
    st.dataframe(df.tail(10).sort_index(ascending=False), use_container_width=True)

elif selected == "THU/CHI":
    st.title("💸 Nhập dữ liệu")
    
    # Sử dụng Tabs hiện đại để chuyển đổi Thu/Chi cực nhanh
    tab1, tab2 = st.tabs(["➖ KHOẢN CHI", "➕ KHOẢN THU"])
    
    with tab1:
        with st.form("form_expense"):
            amt = st.number_input("Số tiền", min_value=0, step=1000, key="e_amt")
            cat = st.selectbox("Hạng mục", ["Ăn uống", "Đi lại", "Mua sắm", "Nhà cửa", "Khác"])
            note = st.text_input("Ghi chú", key="e_note")
            if st.form_submit_button("XÁC NHẬN CHI ➖", use_container_width=True):
                if amt > 0:
                    new_data = pd.DataFrame([{"date": str(datetime.now().date()), "type": "Chi", "category": cat, "amount": float(amt), "note": note}])
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                    st.toast("Đã ghi nhận khoản chi!", icon="🔥")
                    time.sleep(1)
                    st.rerun()

    with tab2:
        with st.form("form_income"):
            amt = st.number_input("Số tiền", min_value=0, step=1000, key="i_amt")
            cat = st.selectbox("Nguồn tiền", ["Lương", "Thưởng", "Kinh doanh", "Khác"])
            note = st.text_input("Ghi chú", key="i_note")
            if st.form_submit_button("XÁC NHẬN THU ➕", use_container_width=True):
                if amt > 0:
                    new_data = pd.DataFrame([{"date": str(datetime.now().date()), "type": "Thu", "category": cat, "amount": float(amt), "note": note}])
                    updated_df = pd.concat([df, new_data], ignore_index=True)
                    conn.update(spreadsheet=url, data=updated_df)
                    st.toast("Đã cộng tiền vào tài khoản!", icon="💰")
                    time.sleep(1)
                    st.rerun()

elif selected == "NHẬT KÝ":
    st.title("📜 Lịch sử")
    st.data_editor(df, use_container_width=True, num_rows="dynamic")
    st.caption("Mẹo: Bạn có thể sửa trực tiếp vào bảng trên và nhấn Save (nếu cấu hình quyền cao hơn).")

elif selected == "HỆ THỐNG":
    st.title("⚙️ Cấu hình")
    st.info(f"Đang kết nối tới: {url}")
    if st.button("🗑️ RESET TOÀN BỘ DỮ LIỆU"):
        empty_df = pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])
        conn.update(spreadsheet=url, data=empty_df)
        st.success("Hệ thống đã sạch bóng!")
        st.rerun()
