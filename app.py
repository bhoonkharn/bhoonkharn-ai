import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: เน้นความคลีน สัดส่วนปุ่มจิ๋ว และสีแดงเลือดหมูสำหรับหมายเหตุ
st.markdown("""
    <style>
    /* ข้อกำหนดการใช้งาน: สีแดงเลือดหมู */
    .disclaimer-text {
        color: #8B0000 !important;
        font-size: 0.8rem;
        line-height: 1.4;
        margin-top: 35px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    /* จุดสังเกตเจ้าของบ้าน: เส้นน้ำเงินด้านซ้าย คลีนๆ */
    .homeowner-box {
        padding: 5px 0 5px 20px;
        border-left: 4px solid #1E3A8A;
        margin-bottom: 25px;
        color: #31333F;
        line-height: 1.8;
    }
    /* ปุ่มถามต่อ: ปรับให้เล็กจิ๋วและสะอาดตาที่สุด */
    div.stButton > button {
        font-size: 0.7rem !important;
        height: 24px !important;
        padding: 0px 8px !important;
        color: #666 !important;
        border-radius: 4px !important;
        border: 1px solid #eee !important;
    }
    /* หัวข้อถามต่อ: เล็กและเทาจาง */
    .q-label {
        font-size: 0.7rem;
        color: #999;
        margin-bottom: 5px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key (Robust Logic)
def load_keys():
    k = []
    if "GOOGLE_API_KEY" in st.secrets:
        k.append(st.secrets["GOOGLE_API_KEY"])
    for key in st.secrets.keys():
        if "API_KEY" in key.upper() and st.secrets[key] not in k:
            k.append(st.secrets[key])
    return k

@st.cache_resource
def start_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    pool = keys.copy()
    random.shuffle(pool)
    for p_key in pool:
        try:
            genai.configure(api_key=p_key)
            m = genai.GenerativeModel("gemini-1.5-flash")
            m.generate_content("ping")
            return m, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = start_engine(load_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# Session ข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar เมนูด้านซ้าย (วาดก่อนเพื่อความเสถียร)
with st.sidebar:
    st.header("⚙️ ระบบ BHOON KHARN")
    if st.session_state.engine: st.success("🟢 พร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status')}")
    
    if st.button("🔄 ลองเชื่อมต่อใหม่"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ
col_left, col_right = st.columns(2)
with col_left:
    blue_print = st.file_uploader("📋 แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
    if blue_print: st.image(blue_print, caption="แบบอ้างอิง", use_container_width=True)
with col_right:
    site_img = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_img: st.image(site_img, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันคุยต่อ
def ask_ai(q_text):
    if not st.session_state.engine: return
    st.session_state.chat_history.append({"role": "user", "content": q_text})
    resp = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN AI: " + q_text)
    st.session_state.chat_history.append({"role": "assistant", "content": resp.text})
    st.rerun()

# 5. ปุ่มเริ่มวิเคราะห์ (อยู่นอกเงื่อนไขเพื่อให้โชว์ตลอด)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน")
    elif site_img or blue_print:
        with st.spinner('BHOON KHARN AI กำลังวิเคราะห์...'):
            try:
                # สร้าง Prompt แบบปลอดภัย (ไม่ใช้ f-string ยาวๆ)
                p = "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพนี้โดยเริ่มทันที:\n"
                p += "🔍 วิเคราะห์หน้างาน: (ระบุงานและสถานะ)\n"
                p += "⏱️ จุดตายวิกฤต: (ระบุความเสี่ยงที่ต้องระวัง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect และงบซ่อม)\n"
                p += "🏗️ มาตรฐานเทคนิค: (วสท./มยผ./สากล)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (เป็นข้อๆ ใช้เครื่องหมาย * นำหน้า ห้ามใช้ HTML)\n"
                p += "ท้ายรายงานให้แนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:'\n"
                p += "โหมดการรายงาน: " + mode
                
                content_list = [p]
                if blue_print: content_list.append(Image.open(blue_print))
                if site_img: content_list.append(Image.open(site_img))
                
                response = st.session_state.engine.generate_content(content_list)
                raw_text = response.text
                
                # แยกคำถามด่วน
                qs = re.findall(r"ถามช่าง: (.+)", raw_text)
                st.session_state.quick_qs = [q.strip() for q in qs[:3]]
                
                # ตัดส่วนคำถามออกเพื่อทำรายงานสะอาดๆ
                report_text = re.sub(r"ถามช่าง: .*", "", raw_text, flags=re.DOTALL).strip()
                st.session_state.final_report = report_text
                st.session_state.chat_history = [{"role": "assistant", "content": report_text}]
                st.rerun()
            except Exception as e:
                st.error("เกิดข้อผิดพลาด: " + str(e))
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. ส่วนการแสดงผล (ล็อก Container ไว้ด้านบนกันหน้าจอเด้ง) ---
report_box = st.container()

if st.session_state.final_report:
    with report_box:
        st.divider()
        st.subheader("📋 รายงานวิเคราะห์โดย BHOON KHARN AI")
        
        full_report = st.session_state.final_report
        patterns = [
            ("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"),
            ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
            ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
            ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
            ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")
        ]
        
        # ค้นหาตำแหน่งเพื่อแยกส่วน
        found_pos = []
        for title, pat in patterns:
            m = re.search(pat, full_report)
            if m: found_pos.append((m.start(), title, m.end()))
        found_pos.sort()
        
        if not found_pos:
            st.markdown(full_report)
        else:
            for i in range(len(found_pos)):
                s = found_pos[i][2]
                e = found_pos[i+1][0] if i+1 < len(found_pos) else len(full_report)
                title = found_pos[i][1]
                content = full_report[s:e].strip().strip(':').strip()
                
                if "🔍" in title:
                    st.info(content)
                elif "🏠" in title:
                    st.markdown("#### " + title)
                    st.markdown("<div class='homeowner-box'>", unsafe_allow_html=True)
                    st.markdown(content)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    with st.expander("**" + title + "**"):
                        st.markdown(content)

        st.download_button("📥 บันทึกรายงาน", st.session_state.final_report, "BK_Report.txt")

        # ส่วนถามต่อ (Small UI)
        if st.session_state.quick_qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            q_cols = st.columns(len(st.session_state.quick_qs))
            for idx, q_val in enumerate(st.session_state.quick_qs):
                if q_cols[idx].button("🔎 " + q
