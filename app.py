# --- แก้ไขฟังก์ชันโหลดโมเดลให้โชว์ Error จริง ---
@st.cache_resource
def initialize_bhoonkharn_ai(keys):
    if not keys:
        return None, "ไม่พบกุญแจในระบบ (Secrets ว่างเปล่า)"
    
    # ลองสุ่มกุญแจ
    random_keys = keys.copy()
    random.shuffle(random_keys)
    
    last_error = ""
    for key in random_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            # ทดสอบเรียกสั้นๆ
            model.generate_content("test") 
            return model, "Success"
        except Exception as e:
            last_error = str(e) # เก็บ Error ล่าสุดไว้ดู
            continue
            
    return None, f"กุญแจใช้ไม่ได้: {last_error}"
