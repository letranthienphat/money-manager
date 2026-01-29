import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import plotly.express as px
import time

# --- 1. CẤU HÌNH APP CHUẨN FINTECH ---
st.set_page_config(page_title="Titanium Finance", layout="wide", page_icon="💳")

# CSS tối ưu cho Mobile (Không che nút bấm)
st.markdown("""
<style>
    /* Chỉnh font chữ đẹp hơn */
    .stApp {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Card số dư nổi bật */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Ẩn menu mặc định góc phải cho gọn */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. KẾT NỐI DỮ LIỆU (AUTO-REPAIR) ---
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    """Tải dữ liệu và tự động sửa lỗi nếu file trống"""
    try:
        # ttl=1: Cache 1 giây để luôn mới
        df = conn.read(spreadsheet=url, ttl=1)
        df = df.dropna(how='all')
        
        # Ép kiểu dữ liệu (Quan trọng để không bị lỗi cộng trừ)
        if not df.empty:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
        return df
    except Exception:
        # Trả về bảng rỗng chuẩn nếu lỗi
        return pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note'])

# --- 3. THANH ĐIỀU HƯỚNG HIỆN ĐẠI (SIDEBAR) ---
with st.sidebar:
    selected = option_menu(
        "Titanium App",
        ["Tổng quan", "Nhập giao dịch", "Báo cáo", "Cài đặt"],
        icons=['house', 'plus-circle', 'bar-chart', 'gear'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0f172a"},
            "icon": {"color": "#38bdf8", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#1e293b"},
            "nav-link-selected": {"background-color": "#0284c7"},
        }
    )

# --- 4. CÁC MÀN HÌNH CHỨC NĂNG ---

# === MÀN HÌNH 1: TỔNG QUAN ===
if selected == "Tổng quan":
    st.title("💳 Ví của tôi")
    
    df = get_data()
    
    # Tính toán
    if not df.empty:
        thu = df[df['type'] == 'Thu']['amount'].sum()
        chi = df[df['type'] == 'Chi']['amount'].sum()
        du = thu - chi
    else:
        thu, chi, du = 0, 0, 0

    # Hiển thị thẻ Số dư (Dùng Container chuẩn của Streamlit)
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Số dư khả dụng", f"{du:,.0f} đ", delta="Tiền mặt")
        col2.metric("Tổng Thu", f"{thu:,.0f} đ", delta="Tích lũy", delta_color="normal")
        col3.metric("Tổng Chi", f"{chi:,.0f} đ", delta="-Chi tiêu", delta_color="inverse")

    st.markdown("### 🕒 Giao dịch gần nhất")
    if not df.empty:
        # Hiển thị bảng rút gọn, đẹp mắt
        view_df = df[['date', 'type', 'category', 'amount', 'note']].sort_values('date', ascending=False).head(5)
        st.dataframe(
            view_df, 
            use_container_width=True,
            column_config={
                "date": "Ngày",
                "type": "Loại",
                "category": "Mục",
                "amount": st.column_config.NumberColumn("Số tiền", format="%d đ"),
                "note": "Ghi chú"
            },
            hide_index=True
        )
    else:
        st.info("Chưa có giao dịch nào.")

# === MÀN HÌNH 2: NHẬP GIAO DỊCH (Quan trọng nhất) ===
elif selected == "Nhập giao dịch":
    st.header("📝 Thêm giao dịch mới")
    
    # Dùng st.container để đóng khung form, tránh vỡ layout
    with st.container(border=True):
        # Chọn Thu hay Chi bằng Tabs cho dễ bấm trên điện thoại
        tab_chi, tab_thu = st.tabs(["💸 KHOẢN CHI (Tiêu tiền)", "💰 KHOẢN THU (Nhận tiền)"])
        
        # --- FORM CHI TIỀN ---
        with tab_chi:
            with st.form("form_chi", clear_on_submit=True):
                c1, c2 = st.columns(2)
                amount = c1.number_input("Số tiền chi", min_value=0, step=1000, key="chi_amt")
                cat = c2.selectbox("Danh mục", ["Ăn uống", "Di chuyển", "Mua sắm", "Cafe", "Tiền nhà", "Khác"], key="chi_cat")
                note = st.text_input("Ghi chú", placeholder="Ví dụ: Ăn phở", key="chi_note")
                date = st.date_input("Ngày", datetime.now(), key="chi_date")
                
                if st.form_submit_button("XÁC NHẬN CHI ➖", use_container_width=True, type="primary"):
                    if amount > 0:
                        with st.spinner("Đang lưu..."):
                            df_old = get_data()
                            new_row = pd.DataFrame([{"date": str(date), "type": "Chi", "category": cat, "amount": float(amount), "note": note}])
                            updated_df = pd.concat([df_old, new_row], ignore_index=True)
                            conn.create(spreadsheet=url, data=updated_df)
                            st.toast(f"Đã trừ {amount:,.0f} đ", icon="✅")
                            time.sleep(1) # Đợi 1s để data kịp lên server
                            st.rerun()
                    else:
                        st.warning("Nhập số tiền lớn hơn 0")

        # --- FORM THU TIỀN ---
        with tab_thu:
            with st.form("form_thu", clear_on_submit=True):
                c1, c2 = st.columns(2)
                amount = c1.number_input("Số tiền thu", min_value=0, step=1000, key="thu_amt")
                cat = c2.selectbox("Nguồn thu", ["Lương", "Thưởng", "Đòi nợ", "Đầu tư", "Khác"], key="thu_cat")
                note = st.text_input("Ghi chú", key="thu_note")
                date = st.date_input("Ngày", datetime.now(), key="thu_date")
                
                if st.form_submit_button("XÁC NHẬN THU ➕", use_container_width=True, type="primary"):
                    if amount > 0:
                        with st.spinner("Đang lưu..."):
                            df_old = get_data()
                            new_row = pd.DataFrame([{"date": str(date), "type": "Thu", "category": cat, "amount": float(amount), "note": note}])
                            updated_df = pd.concat([df_old, new_row], ignore_index=True)
                            conn.create(spreadsheet=url, data=updated_df)
                            st.toast(f"Đã cộng {amount:,.0f} đ", icon="✅")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("Nhập số tiền lớn hơn 0")

# === MÀN HÌNH 3: BÁO CÁO ===
elif selected == "Báo cáo":
    st.header("📊 Phân tích tài chính")
    df = get_data()
    
    if not df.empty:
        df_chi = df[df['type'] == 'Chi']
        if not df_chi.empty:
            # Biểu đồ tròn
            fig = px.pie(df_chi, values='amount', names='category', title='Cơ cấu chi tiêu', hole=0.5)
            st.plotly_chart(fig, use_container_width=True)
            
            # Biểu đồ cột theo ngày
            st.subheader("Chi tiêu theo ngày")
            daily = df_chi.groupby('date')['amount'].sum().reset_index()
            fig2 = px.bar(daily, x='date', y='amount', color_discrete_sequence=['#ff4b4b'])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu chi tiêu để phân tích.")
    else:
        st.write("Chưa có dữ liệu.")

# === MÀN HÌNH 4: CÀI ĐẶT ===
elif selected == "Cài đặt":
    st.header("⚙️ Quản lý dữ liệu")
    with st.container(border=True):
        st.warning("Vùng nguy hiểm")
        if st.button("🗑️ XÓA SẠCH DỮ LIỆU VÀ LÀM LẠI", type="primary"):
            conn.create(spreadsheet=url, data=pd.DataFrame(columns=['date', 'type', 'category', 'amount', 'note']))
            st.success("Đã reset hệ thống!")
            time.sleep(1)
            st.rerun()
