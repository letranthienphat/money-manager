import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.io as pio

# --- CẤU HÌNH QUANTUM OS ---
st.set_page_config(page_title="Quantum OS v16", layout="wide", page_icon="⚛️", initial_sidebar_state="expanded")

# --- ĐỊNH NGHĨA GIAO DIỆN QUANTUM (CSS HACK) ---
# Đây là phần biến giao diện web thành giao diện OS Neon
quantum_css = """
<style>
    /* Tắt hẳn header và footer mặc định của Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Nền tối Quantum */
    .stApp {
        background-color: #0a0a12;
        background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0a0a12 70%);
        color: #e0e0ff;
        font-family: 'Consolas', 'Courier New', monospace;
    }

    /* Thanh Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0e0e1a;
        border-right: 1px solid #00ffff40;
        box-shadow: 5px 0 15px -5px #00ffff20;
    }

    /* Các container (cửa sổ ứng dụng) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #12122480;
        border: 1px solid #00ffff60;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 20px #00ffff20, inset 0 0 10px #00ffff10;
        backdrop-filter: blur(5px);
        margin-bottom: 20px;
    }

    /* Tiêu đề Neon */
    h1, h2, h3 {
        color: #00ffff !important;
        text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff80;
        font-weight: 300 !important;
        letter-spacing: 2px;
    }

    /* Nút bấm Quantum */
    .stButton>button {
        background: transparent !important;
        border: 1px solid #00ffff !important;
        color: #00ffff !important;
        border-radius: 5px;
        text-shadow: 0 0 5px #00ffff;
        box-shadow: 0 0 10px #00ffff40, inset 0 0 5px #00ffff40;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #00ffff20 !important;
        box-shadow: 0 0 20px #00ffff, inset 0 0 10px #00ffff !important;
    }

    /* Input fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #0a0a12 !important;
        color: #00ffff !important;
        border: 1px solid #00ffff40 !important;
        border-radius: 4px;
    }

    /* Metrics (Số dư) */
    [data-testid="stMetricLabel"] { color: #00ffff80 !important; }
    [data-testid="stMetricValue"] {
        color: #fff !important;
        text-shadow: 0 0 10px #00ffff;
    }
</style>
"""
st.markdown(quantum_css, unsafe_allow_html=True)

# Cấu hình Plotly sang Dark theme
pio.templates.default = "plotly_dark"


# --- KẾT NỐI DỮ LIỆU (GIỮ NGUYÊN V15) ---
# URL này sẽ được lấy từ Secrets, không cần sửa ở đây
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Đọc dữ liệu, đảm bảo kiểu số cho cột amount
    df = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3, 4])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    return df

# --- GIAO DIỆN CHÍNH: QUANTUM OS ---

# Sidebar đóng vai trò là "System Menu"
with st.sidebar:
    st.title("⚛️ SYSTEM CORE")
    st.markdown("---")
    menu = st.radio(
        "NAVIGATION MODULE",
        ["🚀 NHẬP LIỆU (Input Terminal)", "📊 PHÂN TÍCH (Data Nexus)", "📋 SỔ CÁI (Ledger View)"],
        index=0
    )
    st.markdown("---")
    st.caption("Quantum OS v16.0 | Status: ONLINE")
    st.caption("Storage: Google Cloud Link")


# Nội dung chính (Main Panel)
st.title("🌌 QUANTUM FINANCE OS")

if menu == "🚀 NHẬP LIỆU (Input Terminal)":
    st.header(">> KHỞI TẠO GIAO DỊCH MỚI")
    st.markdown("Nhập thông tin vào các trường bên dưới để đồng bộ hóa với lõi dữ liệu.")
    
    # Dùng container để tạo hiệu ứng khung cửa sổ
    with st.container():
        with st.form("quantum_input", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("THỜI GIAN (Date Point)", datetime.now())
                t_type = st.selectbox("LOẠI GIAO DỊCH (Type)", ["Chi", "Thu"])
            with col2:
                amount = st.number_input("GIÁ TRỊ (Quantum Value - VNĐ)", min_value=0.0, step=10000.0, format="%.0f")
                category = st.selectbox("DANH MỤC (Category Node)", ["Ăn uống", "Di chuyển", "Lương", "Mua sắm", "Tiền điện/nước", "Khác"])
            
            note = st.text_input("GHI CHÚ DỮ LIỆU (Data Note)")
            
            st.markdown("<br>", unsafe_allow_html=True) # Khoảng cách
            submit = st.form_submit_button(">> ĐỒNG BỘ HÓA DỮ LIỆU <<")
            
            if submit:
                if amount > 0:
                    with st.spinner('Đang thiết lập liên kết lượng tử...'):
                        existing_data = get_data()
                        new_row = pd.DataFrame([{
                            "date": date.strftime('%Y-%m-%d'),
                            "type": t_type,
                            "category": category,
                            "amount": float(amount),
                            "note": note
                        }])
                        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                        conn.update(spreadsheet=url, data=updated_df)
                    st.success(f"✅ DỮ LIỆU ĐÃ ĐƯỢC GHI VÀO LÕI VĨNH CỬU!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ CẢNH BÁO: Giá trị năng lượng phải lớn hơn 0.")

elif menu == "📊 PHÂN TÍCH (Data Nexus)":
    st.header(">> TỔNG QUAN HỆ THỐNG TÀI CHÍNH")
    
    with st.spinner('Đang phân tích dữ liệu lõi...'):
        df = get_data()
        df = df[df['amount'] > 0] # Lọc các dòng rác

        if not df.empty:
            total_thu = df[df['type'] == 'Thu']['amount'].sum()
            total_chi = df[df['type'] == 'Chi']['amount'].sum()
            balance = total_thu - total_chi
            
            # Hiển thị Metrics theo phong cách Quantum
            with st.container():
                c1, c2, c3 = st.columns(3)
                c1.metric("TỔNG NĂNG LƯỢNG THU", f"{total_thu:,.0f} U")
                c2.metric("TỔNG NĂNG LƯỢNG CHI", f"{total_chi:,.0f} U", delta=f"-{total_chi:,.0f}")
                c3.metric("SỐ DƯ HỆ THỐNG", f"{balance:,.0f} U")

            st.markdown("---")
            
            # Biểu đồ
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("CƠ CẤU CHI TIÊU (Pie Scan)")
                df_chi = df[df['type'] == 'Chi']
                if not df_chi.empty:
                    fig_pie = px.pie(df_chi, values='amount', names='category', 
                                     hole=0.5, color_discrete_sequence=px.colors.sequential.Electric)
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00ffff")
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Chưa có dữ liệu chi.")

            with col_chart2:
                 st.subheader("XU HƯỚNG THEO NGÀY (Timeline Scan)")
                 if not df.empty:
                     df_daily = df.groupby(['date', 'type'])['amount'].sum().reset_index()
                     fig_bar = px.bar(df_daily, x='date', y='amount', color='type', barmode='group',
                                      color_discrete_map={'Thu': '#00ff00', 'Chi': '#ff00ff'})
                     fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00ffff",
                                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#00ffff20'))
                     st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("Hệ thống chưa phát hiện dữ liệu. Vui lòng khởi tạo giao dịch.")

elif menu == "📋 SỔ CÁI (Ledger View)":
    st.header(">> NHẬT KÝ GIAO DỊCH CHI TIẾT")
    
    with st.container():
        df_history = get_data()
        if not df_history.empty:
            # Format lại cột số tiền cho đẹp
            st.dataframe(
                df_history.sort_index(ascending=False),
                use_container_width=True,
                column_config={
                    "amount": st.column_config.NumberColumn(
                        "Số tiền (VNĐ)",
                        format="%d đ"
                    )
                }
            )
        else:
             st.info("Nhật ký trống.")
