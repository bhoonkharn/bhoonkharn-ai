import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE (แก้ไขเรื่องการทับซ้อนและสีพื้นหลัง) ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Sarabun', sans-serif; 
        line-height: 1.6; /* ป้องกันตัวหนังสือทับซ้อน */
    }
    
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 20px; }
    
    /* กล่องสำหรับเจ้าของบ้าน - ปรับสีให้อ่านง่าย */
    .owner-box { 
        background-color: #EBF2FF; /* สีฟ้าอ่อนที่ตัดกับตัวหนังสือ */
        border-left: 6px solid #1E3A8A; 
        padding: 20px; 
        border-radius: 8px; 
        margin: 15px 0;
        color: #1A1A1A; /* ตัวหนังสือสีเข้ม */
        font-size: 1.05rem;
    }
    
    .q-label { font-size: 0.9rem; font-weight: bold; color: #1E3A8A; margin-top: 20px; }
    
    /* ปุ่มจิ๋ว 0.7rem */
    div.stButton > button { 
        font-size: 0.75rem !important; 
        border-radius: 15px !important;
    }

    /* หมายเหตุสีแดงเลือดหมู */
    .maroon-note { 
        color: #8B0000; 
        font-size: 0.85rem; 
        border-top: 1px solid #ddd; 
        margin-top: 30px; 
        padding-top: 15px; 
        text-align: center;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบเลือก Model ที่โควตาเยอะ) ---
def init_ai_engine():
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    if not api_key: return None, "❌ ไม่พบ API Key"
    
    try:
        genai.configure(api_key=api_key)
        # เน้นใช้ 1.5-flash เพื่อประหยัดโควตาและทำงานเร็ว
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        # ทดสอบสั้นๆ
        model.generate_content("test", generation_config={"max_output_tokens": 1})
        return model, "✅ ระบบพร้อมทำงาน (Flash Mode)"
    except Exception as e:
        # หาก 1.5-flash มีปัญหา ให้ลองดึงรุ่นอื่นจากลิสต์
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name), f"✅ พร้อมใช้งาน ({m.name})"
        except: pass
        return None, f"❌ ข้อผิดพลาด: {str(e)}"

if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# Session States
for k in ["chat", "rep", "qs"]:
    if k not in st.session_state: st.session_state[k] = [] if k != "rep" else ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ การตั้งค่า")
    st.info(st.session_state.status)
    if st.button("🔄 รีเซ็ตระบบ"):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
    mode = st.radio("เลือกโหมดผู้ใช้งาน:", ["🏠 เจ้าของบ้าน", "📊 เทคนิค/วิศวกร"])
    if st.button("🗑️ ล้างข้อมูลทั้งหมด"):
        st.session_state.chat, st.session_state.rep, st.session_state.qs = [], "", []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แนบรูปแปลน", type=['jpg','jpeg','png'])
    if bp: st.image(bp, caption="แปลนก่อสร้าง")
with c2:
    site = st.file_uploader("📸 แนบรูปหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site, caption="ภาพถ่ายหน้างานจริง")

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน")
        return

    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์ข้อมูล..."):
        try:
            prompt = f"""วิเคราะห์ภาพในฐานะ BHOON KHARN AI โหมด: {mode}
            กรุณาแบ่งเนื้อหาดังนี้:
            [ANALYSIS] สรุปการวิเคราะห์หน้างาน
            [RISK] จุดวิกฤต/จุดตายที่ต้องระวัง
            [STANDARD] มาตรฐานวิศวกรรมที่เกี่ยวข้อง
            [OWNER_NOTE] คำแนะนำสำคัญถึงผู้ว่าจ้างหรือเจ้าของบ้าน
            และปิดท้ายด้วยคำถามแนะนำ 3 ข้อ โดยขึ้นต้นว่า 'ถามช่าง: ' ทุกข้อ"""
            
            inps = [prompt]
            if bp: inps.append(Image.open(bp))
            if site: inps.append(Image.open(site))
            
            response = st.session_state.engine.generate_content(inps)
            txt = response.text
            
            # ดึงคำถามชวนคุยต่อ
            st.session_state.qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            # เก็บผลวิเคราะห์
            st.session_state.rep = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            # เก็บเข้า Chat History
            st.session_state.chat = [{"role": "assistant", "content": "วิเคราะห์ภาพหน้างานเสร็จเรียบร้อยครับ"}]
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def ask_more(query):
    if st.session_state.engine:
        res = st.session_state.engine.generate_content(f"ในฐานะ BHOON KHARN AI ตอบคำถามนี้: {query}")
        st.session_state.chat.append({"role": "user", "content": query})
        st.session_state.chat.append({"role": "assistant", "content": res.text})

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site: run_analysis()
    else: st.warning("กรุณาอัปโหลดรูปภาพก่อนเริ่มการวิเคราะห์")

if st.session_state.rep:
    st.divider()
    res = st.session_state.rep
    
    sections = [
        ("🔍 วิเคราะห์หน้างาน", "[ANALYSIS]"),
        ("⏱️ จุดวิกฤตที่ต้องระวัง", "[RISK]"),
        ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"),
        ("🏠 คำแนะนำสำหรับเจ้าของบ้าน", "[OWNER_NOTE]")
    ]
    
    for title, tag in sections:
        if tag in res:
            content = res.split(tag)[1].split("[")[0].strip()
            if tag == "[OWNER_NOTE]":
                st.markdown(f"<div class='owner-box'><strong>{title}</strong><br>{content}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{title}**", expanded=True if tag=="[ANALYSIS]" else False):
                    st.write(content)

    # ปุ่มคำถามชวนคุยต่อ
    if st.session_state.qs:
        st.markdown("<p class='q-label'>💡 ถาม BHOON KHARN AI ต่อ (ชวนคุย):</p>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state.qs))
        for i, qv in enumerate(st.session_state.qs):
            if cols[i].button("🔎 " + qv, key=f"qbtn_{i}", use_container_width=True):
                ask_more(qv)
                st.rerun()

    # Chat History
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if u_input := st.chat_input("สอบถามรายละเอียดเพิ่มเติมเกี่ยวกับงานช่าง..."):
        ask_more(u_input)
        st.rerun()

    # หมายเหตุเกี่ยวกับการให้ข้อมูล (แดงเลือดหมู)
    st.markdown("""
    <div class='maroon-note'>
        <strong>หมายเหตุ:</strong> การประเมินนี้ทำโดยวิศวกรรม AI จากรูปภาพเบื้องต้นเท่านั้น <br>
        ข้อมูลนี้ไม่สามารถนำไปใช้อ้างอิงทางกฎหมาย หรือทดแทนการตรวจสอบหน้างานจริงโดยวิศวกรวิชาชีพได้ <br>
        กรุณาปรึกษาวิศวกรควบคุมงานของท่านอีกครั้งเพื่อความถูกต้องตามหลักวิชาชีพ
    </div>
    """, unsafe_allow_html=True)
