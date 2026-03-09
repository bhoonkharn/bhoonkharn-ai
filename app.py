import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. Page Config & CSS (เน้นคลีน สบายตา)
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")
st.markdown("""
    <style>
    .disclaimer { color: #8B0000; font-size: 0.8rem; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px; }
    .owner-box { padding: 5px 0 5px 20px; border-left: 4px solid #1E3A8A; margin-bottom: 20px; color: #31333F; line-height: 1.7; }
    div.stButton > button { font-size: 0.7rem !important; height: 26px !important; color: #666 !important; border-radius: 4px !important; }
    .q-label { font-size: 0.7rem; color: #999; margin-top: 15px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)
st.divider()

# 2. Robust Engine (ระบบเช็ก API Key แบบละเอียด)
def get_keys():
    k_list = []
    # 1. เช็ก Key หลัก
    if "GOOGLE_API_KEY" in st.secrets: k_list.append(st.secrets["GOOGLE_API_KEY"])
    # 2. เช็ก Key สำรองอื่นๆ (ถ้ามี)
    for key in st.secrets.keys():
        if "API_KEY" in key.upper() and st.secrets[key] not in k_list:
            k_list.append(st.secrets[key])
    return k_list

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "❌ ไม่พบ API Key ใน Secrets"
    random.shuffle(keys)
    for pk in keys:
        try:
            genai.configure(api_key=pk)
            model = genai.GenerativeModel("gemini-1.5-flash")
            # ทดสอบการเชื่อมต่อ
            model.generate_content("ping")
            return model, "Ready"
        except Exception as e:
            err_msg = str(e)
            continue
    return None, f"❌ เชื่อมต่อล้มเหลว: {err_msg[:50]}"

# ตรวจสอบสถานะและตั้งค่า Session
if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_engine(get_keys())

if "chat" not in st.session_state: st.session_state.chat = []
if "report" not in st.session_state: st.session_state.report = ""
if "qs" not in st.session_state: st.session_state.qs = []

# 3. Sidebar (เมนูตั้งค่า)
with st.sidebar:
    st.header("⚙️ ระบบ BHOON KHARN")
    if st.session_state.engine: st.success("🟢 AI พร้อมใช้งาน")
    else: st.error(st.session_state.status)
    
    if st.button("🔄 ลองเชื่อมต่อใหม่"): 
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat, st.session_state.report, st.session_state.qs = [], "", []
        st.rerun()

# 4. ส่วนอัปโหลดรูป (ประจำตำแหน่งเดิม)
c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แบบแปลน / สเปก", type=['jpg', 'png', 'jpeg'])
    if bp: st.image(bp, caption="Ref", use_container_width=True)
with c2:
    site = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site: st.image(site, caption="Site", use_container_width=True)

# ฟังก์ชันแชทต่อ
def run_q(q_text):
    if not st.session_state.engine: return
    st.session_state.chat.append({"role": "user", "content": q_text})
    resp = st.session_state.engine.generate_content("Analyze as BHOON KHARN AI: " + q_text)
    st.session_state.chat.append({"role": "assistant", "content": resp.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine: st.error("AI ไม่พร้อมใช้งาน")
    elif site or bp:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                p = "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพนี้เริ่มทันที:\n"
                p += "🔍 วิเคราะห์หน้างาน: (สถานะ)\n⏱️ จุดตายวิกฤต: (ความเสี่ยง)\n"
                p += "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect)\n🏗️ มาตรฐานเทคนิค: (วสท.)\n"
                p += "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (เป็นข้อๆ * นำหน้า ห้ามใช้ HTML)\n"
                p += "ท้ายรายงานแนะนำ 3 คำถามสั้นๆ ขึ้นต้นด้วย 'ถามช่าง:' โหมด: " + mode
                
                inputs = [p]
                if bp: inputs.append(Image.open(bp))
                if site: inputs.append(Image.open(site))
                
                response = st.session_state.engine.generate_content(inputs)
                txt_out = response.text
                
                # แยกคำถามและรายงาน
                st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง: (.+)", txt_out)[:3]]
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", txt_out, flags=re.DOTALL).strip()
                st.session_state.chat = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e: st.error(f"เกิดข้อผิดพลาด: {str(e)}")
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. ส่วนการแสดงผล (ป้องกันหน้าจอเด้ง) ---
report_container = st.container()
if st.session_state.report:
    with report_container:
        st.divider()
        st.subheader("📋 ผลการตรวจสอบ")
        r_txt = st.session_state.report
        # หัวข้อสำหรับการแยกส่วน
        h_map = [("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"), 
                 ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
                 ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
                 ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
                 ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")]
        
        pos = sorted([(re.search(pat, r_txt).start(), tit, re.search(pat, r_txt).end()) 
                      for tit, pat in h_map if re.search(pat, r_txt)])
        
        if not pos: st.markdown(r_txt)
        else:
            for i in range(len(pos)):
                start_c = pos[i][2]
                end_c = pos[i+1][0] if i+1 < len(pos) else len(r_txt)
                title_c = pos[i][1]
                content_c = r_txt[start_c:end_c].strip().strip(':').strip()
                
                if "🏠" in title_c:
                    st.markdown(f"#### {title_c}")
                    st.markdown(f"<div class='owner-box'>{content_c}</div>", unsafe_allow_html=True)
                elif "🔍" in title_c: st.info(content_c)
                else:
                    with st.expander(f"**{title_c}**"): st.markdown(content_c)

        st.download_button("📥 บันทึกรายงาน", st.session_state.report, "BK_Report.txt")

        # ส่วนถามต่อ (Small UI)
        if st.session_state.qs:
            st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.qs))
            for idx, q_val in enumerate(st.session_state.qs):
                if cols[idx].button("🔎 " + q_val, key=f"btn_{idx}", use_container_width=True): run_q(q_val)

    if len(st.session_state.chat) > 1:
        st.divider()
        for msg in st.session_state.chat[1:]:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if u_msg := st.chat_input("สอบถามเพิ่มเติม..."): run_q(u_msg)

    st.markdown("""<div class="disclaimer"><strong>ข้อกำหนดการใช้งาน:</strong><br>
    • ประเมินเบื้องต้นจากรูปถ่ายเท่านั้น ข้อมูลอาจไม่ครบถ้วนและไม่สามารถใช้แทนการตรวจสอบโดยวิศวกรวิชาชีพได้<br>
    • ความแม่นยำขึ้นอยู่กับความคมชัดของภาพ โปรดปรึกษาวิศวกรควบคุมงานของท่านก่อนดำเนินการใดๆ</div>""", unsafe_allow_html=True)
