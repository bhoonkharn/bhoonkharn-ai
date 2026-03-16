cat << 'EOF' > test_ui.py
import streamlit as st

# --- 1. CONFIG ---
st.set_page_config(
    page_title="BHOON KHARN AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS FOR MINIMALIST UI ---
st.markdown("""
<style>
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu, footer, header { visibility: hidden; }
    html, body, [class*="st-app"] { background-color: #FFFFFF; color: #1A1A1A; font-family: 'Helvetica Neue', Arial, sans-serif; }
    .status-bar { position: fixed; top: 20px; right: 30px; display: flex; align-items: center; gap: 15px; z-index: 1000; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background-color: #28a745; box-shadow: 0 0 5px #28a745; }
    .status-text { font-size: 0.75rem; font-weight: 700; color: #666; letter-spacing: 1px; }
    .bk-title { font-size: 3rem; font-weight: 700; text-align: center; letter-spacing: -2px; margin-top: 80px; color: #1A1A1A; }
    .bk-subtitle { font-size: 0.85rem; color: #999; text-align: center; margin-bottom: 60px; text-transform: uppercase; letter-spacing: 4px; }
    .stButton>button { border-radius: 4px; border: 1px solid #EEE; background: white; color: #1A1A1A; }
</style>
<div class="status-bar"><div style="display: flex; align-items: center; gap: 5px;"><div class="dot"></div><span class="status-text">ONLINE</span></div></div>
""", unsafe_allow_html=True)

# --- 3. UI LAYOUT ---
h_col1, h_col2, h_col3 = st.columns([8, 0.8, 1.2])
with h_col2: st.button("🌐 TH")
with h_col3: st.button("SIGN IN")

st.markdown("<div class='bk-title'>BHOON KHARN</div>", unsafe_allow_html=True)
st.markdown("<div class='bk-subtitle'>Advanced Construction Intelligence</div>", unsafe_allow_html=True)
st.markdown("---")

up_cols = st.columns(2)
with up_cols[0]:
    st.markdown("<p style='font-size:0.9rem; font-weight:bold;'>BLUEPRINT / PLAN</p>", unsafe_allow_html=True)
    st.file_uploader("a", label_visibility="collapsed")
with up_cols[1]:
    st.markdown("<p style='font-size:0.9rem; font-weight:bold;'>SITE PHOTO</p>", unsafe_allow_html=True)
    st.file_uploader("b", label_visibility="collapsed")

st.markdown("<br><br>", unsafe_allow_html=True)
_, btn_space, _ = st.columns([1, 2, 1])
with btn_space:
    if st.button("RUN ANALYSIS", type="primary", use_container_width=True):
        st.write("Analysing...")

st.markdown(f"<div style='text-align:center; margin-top:150px; color:#DDD; font-size:0.7rem;'>© 2026 BHOON KHARN | INTERNATIONAL STANDARD</div>", unsafe_allow_html=True)
EOF
