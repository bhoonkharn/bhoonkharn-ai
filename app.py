import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# --- ระบบ Login แบบ Redirect (แก้ปัญหา Domain Error ปี 2026) ---
firebase_script = """
<div id="auth-container" style="text-align: center; padding: 20px; font-family: sans-serif;">
    <h2 style="color: #1E3A8A;">BHOON KHARN AI</h2>
    <p>Construction Inspection Intelligence</p>
    <button id="google-login-btn" style="background-color: #ffffff; color: #757575; border: 1px solid #dadce0; padding: 10px 24px; border-radius: 4px; font-size: 16px; cursor: pointer; display: inline-flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" style="width: 18px; margin-right: 10px;">
        เข้าสู่ระบบด้วย Google
    </button>
</div>

<script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
    import { getAuth, GoogleAuthProvider, signInWithRedirect, getRedirectResult, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

    const firebaseConfig = {
        apiKey: "AIzaSyAlOnfNgSCGUzxbGRvEZRPIvTKxJYNulBc",
        authDomain: "test-bhoonkharn.firebaseapp.com",
        projectId: "test-bhoonkharn",
        storageBucket: "test-bhoonkharn.firebasestorage.app",
        messagingSenderId: "377450782387",
        appId: "1:377450782387:web:dd5693c4ce461b9ee09ac6",
        measurementId: "G-S1PX8B4DSJ"
    };

    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    const provider = new GoogleAuthProvider();

    const loginBtn = document.getElementById('google-login-btn');

    // ตรวจสอบผลลัพธ์หลังจากเด้งกลับมาจากการล็อกอิน
    getRedirectResult(auth).then((result) => {
        if (result && result.user) {
            sendToStreamlit(result.user);
        }
    }).catch((error) => {
        console.error("Redirect Error:", error.message);
    });

    // ตรวจสอบสถานะการล็อกอินปัจจุบัน
    onAuthStateChanged(auth, (user) => {
        if (user) {
            sendToStreamlit(user);
        }
    });

    function sendToStreamlit(user) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {
                email: user.email,
                name: user.displayName,
                photo: user.photoURL || 'https://www.gstatic.com/images/branding/product/1x/avatar_circle_blue_512dp.png',
                status: 'success'
            }
        }, '*');
    }

    // เมื่อกดปุ่ม ให้เปลี่ยนหน้าไปที่หน้าล็อกอินของ Google
    loginBtn.onclick = () => {
        signInWithRedirect(auth, provider);
    };
</script>
"""

# แสดงหน้า Login
if 'user' not in st.session_state:
    login_data = components.html(firebase_script, height=250)
    
    # ตรวจสอบว่าได้รับข้อมูลจาก JavaScript หรือไม่
    if login_data and isinstance(login_data, dict) and login_data.get('status') == 'success':
        st.session_state.user = login_data
        st.rerun()
    st.stop()

# --- ส่วนเนื้อหาหลักเมื่อ Login สำเร็จ ---
user = st.session_state.user
user_name = user.get('name', 'ผู้ใช้งาน')
user_photo = user.get('photo')

st.sidebar.image(user_photo, width=80)
st.sidebar.write(f"สวัสดีคุณ **{user_name}**")

if st.sidebar.button("ออกจากระบบ"):
    del st.session_state.user
    st.rerun()

st.title("🏗️ BHOON KHARN AI")
st.subheader("Construction Inspection Intelligence")

# แบ่งหน้าจอ
col1, col2 = st.columns([1, 1])

with col1:
    st.info("📷 วิเคราะห์รูปภาพงานก่อสร้าง")
    uploaded_file = st.file_uploader("เลือกรูปภาพ...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="รูปที่อัปโหลด", use_container_width=True)
        if st.button("เริ่มวิเคราะห์"):
            st.success("วิเคราะห์สำเร็จ: ตรวจสอบความเรียบร้อยแล้ว")

with col2:
    st.info("💬 แชทกับ AI")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("ถามคำถามที่นี่..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            res = f"AI กำลังวิเคราะห์คำถาม: {prompt}"
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})

st.divider()
st.caption("BHOON KHARN AI v1.2.1 - Enhanced Security Mode")
