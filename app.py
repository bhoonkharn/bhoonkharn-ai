import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: ปรับจูนให้สะอาดตาที่สุด ลดขนาดส่วนเสริม และใช้สีแดงเลือดหมูตามโจทย์
st.markdown("""
    <style>
    /* ข้อกำหนดการใช้งาน: สีแดงเลือดหมู */
    .disclaimer-text {
        color: #8B0000 !important;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    /* จุดสังเกตเจ้าของบ้าน: เส้นน้ำเงินด้านซ้าย ไม่มีพื้นหลังจ้า */
    .homeowner-box {
        padding: 10px 0 10px 20px;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 25px;
        color: #31333F;
        line-height: 1.8;
    }
    /* ปรับขนาดปุ่มถามต่อให้เล็กและสะอาดตา */
    div.stButton > button {
        font-size: 0.75rem !important;
        height: auto !important;
        padding: 4px 12px !important;
        color: #555 !important;
    }
    /* หัวข้อถามต่อ: สีเทา ตัวเล็ก ไม่แย่งซีน */
    .q-label {
        font-size: 0.75rem;
        color: #888;
        margin-bottom: 10px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key
def get_keys():
    k_list = []
    if "GOOGLE_API_KEY" in st.secrets:
        k_list.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in k_list:
            k_list.append(st.secrets[k])
    return k_list

@st.cache_resource
def init_ai(keys):
    if not keys: return None, "ไม่พบ API Key"
    random.shuffle(keys)
    for k in keys:
        try:
            genai.configure(api_key=k)
            model = genai.GenerativeModel("gemini-1.5-flash")
            model.generate_content("test")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = init_ai(get_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# Session State สำหรับเก็บข้อมูล
if "chat_log" not in st.session_state: st.session_state.chat_log = []
if "report" not in st.session_state: st.session_state.report = ""
if "btns" not in st.session_state: st.session_state.btns = []

# 3. Sidebar เมนูด้านซ้าย (มั่นใจว่าขึ้นแน่นอน)
with st.sidebar:
    st.header("⚙️ ตั้งค่าระบบ")
    if st.session_state.engine: st.success("🟢 AI พร้อมใช้งาน")
    else: st.error(f"🔴 {st.session_state.get('status')}")
    
    if st.button("🔄 รีเซ็ตการเชื่อมต่อ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด", use_container_width=True):
        st.session_state.chat_log = []
        st.session_state.report = ""
        st.session_state.btns = []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (ประจำที่แน่นอน)
col_a, col_b = st.columns(2)
with col_a:
    img_ref = st.file_uploader("📋 แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
    if img_ref: st.image(img_ref, caption="แบบอ้างอิง", use_container_width=True)
with col_b:
    img_site = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if img_site: st.image(img_site, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันแชทต่อ
def ask_more(text):
    if not st.session_state.engine: return
    st.session_state.chat_log.append({"role": "user", "content": text})
    resp = st.session_state.engine.generate_content("ในฐานะ BHOON KHARN AI: " + text)
    st.session_state.chat_log.append({"role": "assistant", "content": resp.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine:
        st.error("ระบบ AI ไม่พร้อมใช้งาน")
    elif img_site or img_ref:
        with st.spinner('BHOON KHARN AI กำลังประมวลผล...'):
            try:
                # Prompt แบบเน้นโครงสร้าง (ตัดทักทาย)
                prompt = (
                    "คุณคือที่ปรึกษา BHOON KHARN AI วิเคราะห์ภาพนี้โดยเริ่มทันที:\n"
                    "🔍 วิเคราะห์หน้างาน: (สรุปสถานะปัจจุบัน)\n"
                    "⏱️ จุดตายวิกฤต: (ระบุความเสี่ยงที่ต้องระวัง)\n"
                    "⚠️ ผลกระทบต่อเนื่อง: (Domino Effect และงบประมาณซ่อม)\n"
                    "🏗️ มาตรฐานเทคนิค: (วสท./มยผ./สากลที่เกี่ยวข้อง)\n"
                    "🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน: (สรุปเป็นข้อๆ พร้อม Emoji และเว้นบรรทัดใหม่ 2 ครั้งทุกข้อ)\n"
                    "ท้ายรายงานให้แนะนำ 3 คำถามสั้นๆ ขึ้นต้นด้วย 'ถามช่าง:'"
                )
                
                input_data = [prompt]
                if img_ref: input_data.append(Image.open(img_ref))
                if img_site: input_data.append(Image.open(img_site))
                
                response = st.session_state.engine.generate_content(input_data)
                res_text = response.text
                
                # แยกคำถามมาทำปุ่ม
                qs = re.findall(r"ถามช่าง: (.+)", res_text)
                st.session_state.btns = [q.strip() for q in qs[:3]]
                
                # ทำความสะอาดรายงาน
                st.session_state.report = re.sub(r"ถามช่าง: .*", "", res_text, flags=re.DOTALL).strip()
                st.session_state.chat_log = [{"role": "assistant", "content": st.session_state.report}]
                st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. แสดงผลรายงาน ---
if st.session_state.report:
    st.divider()
    st.subheader("📋 ผลการตรวจสอบโดย BHOON KHARN AI")
    
    full_txt = st.session_state.report
    # ระบบแยกหัวข้อแบบยืดหยุ่นสูง
    heads = [
        ("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"),
        ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
        ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
        ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
        ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")
    ]
    
    pos = []
    for title, pat in heads:
        match = re.search(pat, full_txt)
        if match: pos.append((match.start(), title, match.end()))
    
    pos.sort()
    
    if not pos:
        st.markdown(full_txt)
    else:
        for i in range(len(pos)):
            s_idx = pos[i][2]
            e_idx = pos[i+1][0] if i+1 < len(pos) else len(full_txt)
            title = pos[i][1]
            content = full_txt[s_idx:e_idx].strip().strip(':').strip()
            
            if "🔍" in title:
                st.info(content)
            elif "🏠" in title:
                # หัวข้อเจ้าของบ้าน: คลีนๆ ไม่จ้าตา
                st.markdown(f"#### {title}")
                st.markdown(f"<div class='homeowner-box'>", unsafe_allow_html=True)
                st.markdown(content)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{title}**"):
                    st.markdown(content)

    st.download_button("📥 บันทึกรายงาน", st.session_state.report, "BK_Report.txt")

    # ส่วนถามต่อ (Small UI)
    if st.session_state.btns:
        st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
        btn_cols = st.columns(len(st.session_state.btns))
        for idx, q_txt in enumerate(st.session_state.btns):
            if btn_cols[idx].button(f"🔎 {q_txt}", key=f"bk_{idx}", use_container_width=True):
                ask_more(q_txt)

    # แชทประวัติ
    if len(st.session_state.chat_log) > 1:
        st.divider()
        for msg in st.session_state.chat_log[1:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_input := st.chat_input("สอบถามเพิ่มเติมได้ที่นี่..."):
        ask_more(user_input)

    # 7. ข้อกำหนดการใช้งาน (Maroon)
    st.markdown("""
    <div class="disclaimer-text">
        <strong>ข้อกำหนดการใช้งาน:</strong><br>
        • ข้อมูลนี้เป็นการประเมินเบื้องต้นจากรูปถ่ายเท่านั้น ข้อมูลที่ได้รับอาจไม่ครบถ้วนและไม่สามารถใช้แทนการตรวจสอบหน้างานจริงโดยวิศวกรวิชาชีพได้<br>
        • ความแม่นยำขึ้นอยู่กับความคมชัดของภาพที่ท่านอัปโหลด หากรูปภาพไม่ชัดเจนแนะนำให้ถ่ายภาพใหม่ในมุมที่หลากหลายขึ้น<br>
        • โปรดปรึกษาวิศวกรควบคุมงานของท่านก่อนดำเนินการใดๆ เพื่อความปลอดภัยสูงสุด
    </div>
    """, unsafe_allow_html=True)
