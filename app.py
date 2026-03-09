import streamlit as st
import google.generativeai as genai
from PIL import Image
import random
import re

# 1. ตั้งค่าหน้าเว็บ BHOON KHARN Branding
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# CSS: ปรับแต่ง UI ให้คลีน สบายตา และสัดส่วนถูกต้อง
st.markdown("""
    <style>
    .disclaimer-text {
        color: #8B0000; 
        font-size: 0.8rem;
        line-height: 1.5;
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    .check-box {
        padding: 5px 0 5px 20px;
        border-left: 4px solid #1E3A8A;
        margin-bottom: 25px;
        color: #31333F;
        line-height: 1.8;
    }
    /* ปุ่มคำถามด่วน: เล็กจิ๋วและสะอาดตา */
    .stButton>button {
        font-size: 0.7rem !important; 
        padding: 2px 8px !important;
        min-height: 24px !important;
        height: 24px !important;
        border-radius: 4px !important;
        color: #666 !important;
        border: 1px solid #eee !important;
    }
    /* หัวข้อถามต่อ: เล็กและถ่อมตัว */
    .quick-q-label {
        font-size: 0.7rem !important;
        color: #999 !important;
        margin-bottom: 8px !important;
        margin-top: 20px !important;
        font-weight: normal !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ BHOON KHARN AI Analysis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>วิเคราะห์งานก่อสร้างและประเมินความเสี่ยงอัจฉริยะ</p>", unsafe_allow_html=True)
st.divider()

# 2. ระบบจัดการ API Key
def get_working_keys():
    keys = []
    if "GOOGLE_API_KEY" in st.secrets:
        keys.append(st.secrets["GOOGLE_API_KEY"])
    for k in st.secrets.keys():
        if "GOOGLE_API_KEY" in k and st.secrets[k] not in keys:
            keys.append(st.secrets[k])
    return keys

@st.cache_resource
def init_engine(keys):
    if not keys: return None, "ไม่พบ API Key"
    shuffled = keys.copy()
    random.shuffle(shuffled)
    for k in shuffled:
        try:
            genai.configure(api_key=k)
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target = [m for m in models if "flash" in m.lower()][0] if models else None
            if not target: continue
            model = genai.GenerativeModel(target)
            model.generate_content("ping")
            return model, "Ready"
        except: continue
    return None, "การเชื่อมต่อล้มเหลว"

if "engine" not in st.session_state:
    engine, status = init_engine(get_working_keys())
    st.session_state.engine = engine
    st.session_state.status = status

# ระบบ Session ข้อมูล
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "quick_qs" not in st.session_state: st.session_state.quick_qs = []

# 3. Sidebar แถบตั้งค่าด้านซ้าย
with st.sidebar:
    st.title("⚙️ BHOON KHARN AI")
    if st.session_state.engine:
        st.success("🟢 ระบบพร้อมใช้งาน")
    else:
        st.error(f"🔴 {st.session_state.get('status', 'ขัดข้อง')}")
    
    if st.button("🔄 รีเซ็ตระบบ"):
        st.session_state.engine = None
        st.rerun()
    st.divider()
    mode = st.radio("รูปแบบรายงาน:", ["📊 เทคนิคเชิงลึก", "🏠 สำหรับเจ้าของบ้าน"])
    if st.button("🗑️ ล้างประวัติทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.final_report = ""
        st.session_state.quick_qs = []
        st.rerun()

# 4. ส่วนอัปโหลดรูปภาพ (วางไว้ด้านบนเพื่อให้แสดงผลตลอดเวลา)
col_l, col_r = st.columns(2)
with col_l:
    blueprint = st.file_uploader("📋 แบบแปลน / สเปกวัสดุ", type=['jpg', 'png', 'jpeg'])
    if blueprint: st.image(blueprint, caption="แบบอ้างอิง", use_container_width=True)

with col_r:
    site_photo = st.file_uploader("📸 ภาพหน้างานจริง", type=['jpg', 'png', 'jpeg'])
    if site_photo: st.image(site_photo, caption="หน้างานจริง", use_container_width=True)

# ฟังก์ชันส่งคำถามต่อเนื่อง
def run_query(q):
    if not st.session_state.engine: return
    st.session_state.chat_history.append({"role": "user", "content": q})
    res = st.session_state.engine.generate_content("วิเคราะห์ในฐานะ BHOON KHARN: " + q)
    st.session_state.chat_history.append({"role": "assistant", "content": res.text})
    st.rerun()

# 5. ปุ่มเริ่มการวิเคราะห์ (วางไว้นอกเงื่อนไขเพื่อให้โชว์ตลอดเวลา)
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True):
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน")
    elif site_photo or blueprint:
        with st.spinner('BHOON KHARN AI กำลังประมวลผลข้อมูล...'):
            try:
                # Prompt: บังคับหัวข้อชัดเจน ไม่แนะนำตัว
                prompt_text = (
                    "วิเคราะห์ภาพในฐานะที่ปรึกษา BHOON KHARN โดยเริ่มทันทีที่หัวข้อแรก:\n"
                    "🔍 [วิเคราะห์หน้างาน]: (ระบุงานและสถานะปัจจุบัน)\n"
                    "⏱️ [จุดตายวิกฤต]: (ความเสี่ยงแฝงที่ต้องระวัง)\n"
                    "⚠️ [ผลกระทบต่อเนื่อง]: (Domino Effect และงบประมาณซ่อมแซม)\n"
                    "🏗️ [มาตรฐานเทคนิค]: (มาตรฐาน วสท./มยผ./สากล)\n"
                    "🏠 [จุดสังเกตสำคัญสำหรับเจ้าของบ้าน]: (สรุปเป็นข้อๆ พร้อม Emoji และขึ้นบรรทัดใหม่ 2 ครั้งทุกข้อ)\n"
                    "แนะนำ 3 คำถามสั้นๆ เริ่มด้วย 'ถามช่าง:' (ห้ามแสดงหัวข้อคำถามในเนื้อหา) "
                    "โหมด: " + mode
                )
                
                imgs = [Image.open(f) for f in [blueprint, site_photo] if f]
                resp = st.session_state.engine.generate_content([prompt_text] + imgs)
                full_text = resp.text
                
                # แยกคำถามด่วนออกจากเนื้อหา
                found_qs = re.findall(r"ถามช่าง: (.+)", full_text)
                st.session_state.quick_qs = [q.strip() for q in found_qs[:3]]
                clean_report = re.sub(r"ถามช่าง: .*", "", full_text, flags=re.DOTALL).strip()
                
                st.session_state.final_report = clean_report
                st.session_state.chat_history = [{"role": "assistant", "content": clean_report}]
                st.rerun()
            except Exception as e:
                st.error("เกิดข้อผิดพลาดในการวิเคราะห์: " + str(e))
    else:
        st.warning("กรุณาอัปโหลดรูปภาพก่อนครับ")

# --- 6. ส่วนการแสดงผลรายงาน ---
if st.session_state.final_report:
    st.divider()
    st.markdown("### 📋 ผลการตรวจสอบและวิเคราะห์")
    
    text = st.session_state.final_report
    sections = [
        ("🔍 วิเคราะห์หน้างาน", r"🔍.*?วิเคราะห์หน้างาน"),
        ("⏱️ จุดตายวิกฤต", r"⏱️.*?จุดตายวิกฤต"),
        ("⚠️ ผลกระทบต่อเนื่อง", r"⚠️.*?ผลกระทบต่อเนื่อง"),
        ("🏗️ มาตรฐานเทคนิค", r"🏗️.*?มาตรฐานเทคนิค"),
        ("🏠 จุดสังเกตสำคัญสำหรับเจ้าของบ้าน", r"🏠.*?จุดสังเกตสำคัญสำหรับเจ้าของบ้าน")
    ]
    
    pos = []
    for title, pattern in sections:
        m = re.search(pattern, text)
        if m: pos.append((m.start(), title, m.end()))
    
    pos.sort()

    if not pos:
        st.markdown(text) 
    else:
        for i in range(len(pos)):
            start_content = pos[i][2]
            end_content = pos[i+1][0] if i+1 < len(pos) else len(text)
            title = pos[i][1]
            content = text[start_content:end_content].strip().strip(':').strip()
            
            if "🔍" in title:
                st.info(content)
            elif "🏠" in title:
                st.markdown("#### " + title)
                st.markdown("<div class='check-box'>", unsafe_allow_html=True)
                st.markdown(content) # แสดงเป็น List ตาม Markdown
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                with st.expander("**" + title + " (คลิกดูรายละเอียด)**"):
                    st.markdown(content)
    
    st.download_button("📥 บันทึกรายงาน (TXT)", st.session_state.final_report, "BK_Analysis.txt")

    # --- ส่วนถามต่อ (Quick Reply) - เล็กและถ่อมตัว ---
    if st.session_state.quick_qs:
        st.markdown("<p class='quick-q-label'>💡 ถาม BHOON KHARN AI ต่อในประเด็นนี้:</p>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.quick_qs))
        for idx, q in enumerate(st.session_state.quick_qs):
            if cols[idx].button("🔎 " + q, key="q_" + str(idx), use_container_width=True):
                run_query(q)

    # ประวัติการแชท
    if len(st.session_state.chat_history) > 1:
        st.divider()
        for msg in st.session_state.chat_history[1:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_q := st.chat_input("พิมพ์คำถามอื่น ๆ ที่ท่านสงสัย..."):
        run_query(user_q)
    
    # 7. ข้อกำหนดการใช้งาน (สีแดงเลือดหมู)
    st.markdown("""
    <div class="disclaimer-text">
        <strong>ข้อกำหนดการใช้งาน:</strong><br>
        • การวิเคราะห์นี้เป็นการประเมินเบื้องต้นจากข้อมูลรูปถ่ายเท่านั้น ข้อมูลที่ได้รับอาจไม่ครบถ้วนสมบูรณ์ตามสภาพหน้างานจริง และไม่สามารถใช้แทนการตรวจสอบโดยวิศวกรวิชาชีพในสถานที่ก่อสร้างได้<br>
        • ผลลัพธ์ขึ้นอยู่กับคุณภาพ ความคมชัด และมุมมองของรูปภาพที่ท่านอัปโหลด หากระบบไม่สามารถระบุรายละเอียดได้ชัดเจน แนะนำให้ถ่ายภาพใหม่ในมุมที่หลากหลายและมีแสงสว่างเพียงพอ<br>
        • BHOON KHARN AI ให้ข้อมูลเพื่อเป็นแนวทางประกอบการตัดสินใจเบื้องต้นเท่านั้น โปรดปรึกษาวิศวกรผู้ควบคุมงานของท่านก่อนดำเนินการในขั้นตอนถัดไป
    </div>
    """, unsafe_allow_html=True)
