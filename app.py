import streamlit as st
import google.generativeai as genai
from PIL import Image
import re

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Sarabun', sans-serif; }
    .main-title { color: #1E3A8A; text-align: center; font-weight: 700; margin-bottom: 20px; }
    .owner-box { background-color: #f0f4f8; border-left: 5px solid #1E3A8A; padding: 18px; border-radius: 5px; margin: 10px 0; }
    .status-box { padding: 10px; border-radius: 10px; margin-bottom: 10px; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. ENGINE (ระบบแก้ปัญหา 404 ขั้นเด็ดขาด) ---
def init_ai_engine():
    # ดึง API Key จาก Secrets
    api_key = st.secrets.get("GOOGLE_API_KEY") or next((st.secrets[k] for k in st.secrets if "API_KEY" in k.upper()), None)
    
    if not api_key:
        return None, "❌ ไม่พบ API Key ใน Secrets"
    
    try:
        genai.configure(api_key=api_key)
        
        # ค้นหารุ่นที่มีอยู่จริง (ป้องกัน 404 โดยการถาม Google ตรงๆ ว่ามีรุ่นไหนให้ใช้บ้าง)
        valid_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # เก็บชื่อเต็ม เช่น 'models/gemini-1.5-flash'
                    valid_models.append(m.name)
        except Exception as e:
            return None, f"❌ ไม่สามารถดึงรายชื่อ Model ได้: {str(e)}"

        if not valid_models:
            return None, "❌ บัญชีนี้ไม่มีรุ่นที่รองรับ generateContent"

        # เลือกใช้ตามลำดับความเทพ (เอาตัวที่ใหม่และรองรับ Vision)
        # 1. ลองหา 1.5-flash (รุ่นมาตรฐานที่พี่ต้องการ)
        # 2. ถ้าไม่เจอ ลองหา 1.5-pro
        # 3. ถ้าไม่เจออีก เอาตัวแรกที่ Google ส่งมาให้
        selected_m = None
        for target in ["1.5-flash", "1.5-pro", "gemini-pro-vision", "gemini-pro"]:
            for actual in valid_models:
                if target in actual:
                    selected_m = actual
                    break
            if selected_m: break
        
        if not selected_m:
            selected_m = valid_models[0]

        # สร้าง Model Object
        model = genai.GenerativeModel(model_name=selected_m)
        return model, f"✅ เชื่อมต่อสำเร็จ (ใช้รุ่น: {selected_m})"
        
    except Exception as e:
        return None, f"❌ ข้อผิดพลาดการเชื่อมต่อ: {str(e)}"

# ตรวจสอบและสร้าง Engine ครั้งเดียว
if "engine" not in st.session_state:
    st.session_state.engine, st.session_state.status = init_ai_engine()

# เตรียม Session States
for key in ["chat_history", "analysis_result", "suggested_qs"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "analysis_result" else ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏗️ BHOON KHARN AI")
    if "✅" in st.session_state.status:
        st.success(st.session_state.status)
    else:
        st.error(st.session_state.status)
        
    if st.button("🔄 รีเซ็ตและหา Model ใหม่", use_container_width=True):
        st.session_state.engine, st.session_state.status = init_ai_engine()
        st.rerun()
        
    mode = st.radio("มุมมองการวิเคราะห์:", ["📊 เทคนิค/วิศวกร", "🏠 เจ้าของบ้าน"])
    
    if st.button("🗑️ ล้างหน้าจอ", use_container_width=True):
        st.session_state.chat_history, st.session_state.analysis_result, st.session_state.suggested_qs = [], "", []
        st.rerun()

# --- 4. MAIN UI ---
st.markdown("<h1 class='main-title'>🏗️ BHOON KHARN AI</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    bp = st.file_uploader("📋 แนบรูปแปลน", type=['jpg','jpeg','png'])
    if bp: st.image(bp, caption="Blueprint")
with c2:
    site = st.file_uploader("📸 แนบรูปหน้างาน", type=['jpg','jpeg','png'])
    if site: st.image(site, caption="Site Photo")

# --- 5. LOGIC ---
def run_analysis():
    if not st.session_state.engine:
        st.error("AI ไม่พร้อมใช้งาน กรุณาตรวจสอบ API Key")
        return

    with st.spinner("BHOON KHARN AI กำลังวิเคราะห์..."):
        try:
            prompt = f"""วิเคราะห์ภาพงานก่อสร้างนี้ในฐานะวิศวกร (โหมด: {mode})
            สรุปหัวข้อตามนี้:
            [ANALYSIS] สรุปหน้างาน
            [RISK] จุดวิกฤตที่ต้องระวัง
            [STANDARD] มาตรฐานวิศวกรรมที่เกี่ยวข้อง
            [OWNER_NOTE] ข้อแนะนำสำหรับเจ้าของบ้าน
            ปิดท้ายด้วยคำถามแนะนำ 3 ข้อ โดยขึ้นต้นว่า 'ถามช่าง: ' ทุกข้อ"""
            
            payload = [prompt]
            if bp: payload.append(Image.open(bp))
            if site: payload.append(Image.open(site))
            
            response = st.session_state.engine.generate_content(payload)
            txt = response.text
            
            # สกัดคำถามและเนื้อหา
            st.session_state.suggested_qs = [q.strip() for q in re.findall(r"ถามช่าง:\s*(.*)", txt)[:3]]
            st.session_state.analysis_result = re.sub(r"ถามช่าง:.*", "", txt, flags=re.DOTALL).strip()
            
        except Exception as e:
            st.error(f"การวิเคราะห์ล้มเหลว: {str(e)}")
            if "404" in str(e):
                st.info("💡 คำแนะนำ: ระบบตรวจพบรุ่นเก่า ลองกดปุ่ม 'รีเซ็ตและหา Model ใหม่' ที่ด้านซ้ายครับ")

# --- 6. DISPLAY ---
if st.button("🚀 เริ่มการวิเคราะห์อัจฉริยะ", use_container_width=True, type="primary"):
    if bp or site:
        run_analysis()
    else:
        st.warning("⚠️ กรุณาอัปโหลดรูปภาพอย่างน้อย 1 รูป")

if st.session_state.analysis_result:
    st.divider()
    res = st.session_state.analysis_result
    
    sections = [("🔍 วิเคราะห์หน้างาน", "[ANALYSIS]"), ("⏱️ จุดตายวิกฤต", "[RISK]"), 
                ("🏗️ มาตรฐานวิศวกรรม", "[STANDARD]"), ("🏠 ข้อแนะนำสำหรับเจ้าของบ้าน", "[OWNER_NOTE]")]
    
    for title, tag in sections:
        if tag in res:
            content = res.split(tag)[1].split("[")[0].strip()
            if tag == "[OWNER_NOTE]":
                st.markdown(f"<div class='owner-box'><b>{title}</b><br>{content}</div>", unsafe_allow_html=True)
            else:
                with st.expander(f"**{title}**", expanded=True if tag=="[ANALYSIS]" else False):
                    st.write(content)

    if st.session_state.suggested_qs:
        st.write("---")
        st.markdown("**💡 ถาม AI ต่อ:**")
        cols = st.columns(len(st.session_state.suggested_qs))
        for i, q in enumerate(st.session_state.suggested_qs):
            if cols[i].button(f"💬 {q}", key=f"btn_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                res_q = st.session_state.engine.generate_content(f"ตอบในฐานะ BHOON KHARN AI: {q}")
                st.session_state.chat_history.append({"role": "assistant", "content": res_q.text})
                st.rerun()

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(msg["content"] if 'msg' in locals() else m["content"])

    if user_i := st.chat_input("สอบถามเพิ่มเติม..."):
        st.session_state.chat_history.append({"role": "user", "content": user_i})
        res_i = st.session_state.engine.generate_content(f"ตอบในฐานะ BHOON KHARN AI: {user_i}")
        st.session_state.chat_history.append({"role": "assistant", "content": res_i.text})
        st.rerun()

st.markdown("<div style='text-align:center; color:gray; font-size:0.7rem; margin-top:50px;'>BHOON KHARN AI - ระบบช่วยเหลือวิศวกรและเจ้าของบ้านเบื้องต้น</div>", unsafe_allow_html=True)
