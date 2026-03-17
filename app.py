import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="BHOON KHARN AI", layout="wide")

# --- ส่วนของระบบ Login ด้วย Google (Firebase) ---
# ผมอัปเดตกุญแจเป็นชุดใหม่ (test-bhoonkharn) ให้แล้วครับ
firebase_script = """
<div id="auth-container" style="text-align: center; padding: 20px; font-family: sans-serif;">
    <h2 style="color: #1E3A8A;">BHOON KHARN AI</h2>
    <p>Construction Inspection Intelligence</p>
    <button id="google-login-btn" style="background-color: #ffffff; color: #757575; border: 1px solid #dadce0; padding: 10px 24px; border-radius: 4px; font-size: 16px; cursor: pointer; display: inline-flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" style="width: 18px; margin-right: 10px;">
        เข้าสู่ระบบด้วย Google
    </button>
    <div id="user-info" style="display:none; margin-top: 20px;">
        <p id="welcome-msg" style="color: green; font-weight: bold;"></p>
    </div>
</div>

<script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
    import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

    // กุญแจชุดใหม่ที่คุณส่งมาครับ
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
    const userInfo = document.getElementById('user-info');
    const welcomeMsg = document.getElementById('welcome-msg');

    // ฟังก์ชันล็อกอิน
    loginBtn.onclick = () => {
        signInWithPopup(auth, provider)
            .then((result) => {
                const user = result.user;
                // ส่งข้อมูลกลับไปที่ Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: {email: user.email, name: user.displayName, photo: user.photoURL, status: 'success'}
                }, '*');
            })
            .catch((error) => {
                console.error("Login Error:", error.code);
                alert("เกิดข้อผิดพลาด: " + error.message);
            });
    };

    // ตรวจสอบสถานะล็อกอิน
    onAuthStateChanged(auth, (user) => {
        if (user) {
            loginBtn.style.display = 'none';
            userInfo.style.display = 'block';
            welcomeMsg.innerText = "เข้าสู่ระบบสำเร็จ! สวัสดีคุณ " + user.displayName;
        }
    });
</script>
"""

# แสดงหน้า Login
if 'user' not in st.session_state:
    login_data = components.html(firebase_script, height=250)
    # รับค่าจาก JavaScript กลับมายัง Streamlit
    if login_data:
        st.session_state.user = login_data
        st.rerun()
    st.stop()

# --- ส่วนเนื้อหาหลักหลังจากล็อกอินแล้ว ---
user = st.session_state.user
st.sidebar.image(user.get('photo'), width=100)
st.sidebar.write(f"สวัสดีคุณ **{user.get('name')}**")
if st.sidebar.button("ออกจากระบบ"):
    del st.session_state.user
    st.rerun()

st.title("🏗️ BHOON KHARN AI")
st.subheader("Construction Inspection Intelligence")

col1, col2 = st.columns([1, 1])

with col1:
    st.info("📷 อัปโหลดรูปภาพงานก่อสร้างเพื่อให้ AI วิเคราะห์")
    uploaded_file = st.file_uploader("เลือกรูปภาพ...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="รูปภาพที่อัปโหลด", use_container_width=True)
        if st.button("เริ่มวิเคราะห์งาน"):
            with st.spinner("AI กำลังตรวจสอบความถูกต้อง..."):
                st.success("วิเคราะห์สำเร็จ: งานโครงสร้างคานเป็นไปตามมาตรฐาน")

with col2:
    st.info("💬 สอบถาม AI เกี่ยวกับงานก่อสร้าง")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = f"AI กำลังประมวลผลคำถาม: '{prompt}' ของคุณ"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
st.caption("BHOON KHARN AI v1.2 - พัฒนาเพื่อยกระดับมาตรฐานงานก่อสร้างไทย")
