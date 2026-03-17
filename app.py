import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าจอ Streamlit
st.set_page_config(layout="wide", page_title="Test Login BHOON KHARN AI")

# 2. โค้ด HTML + JS แบบเน้นระบบ Login อย่างเดียว (ไม่มีดีไซน์ซับซ้อน)
html_code = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>ทดสอบ Login</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background: #f0f2f6; }
        .hidden { display: none; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        button { padding: 15px 30px; font-size: 16px; cursor: pointer; border: none; border-radius: 5px; margin: 10px; font-weight: bold; }
        #login-btn { background-color: #4285F4; color: white; }
        #logout-btn { background-color: #dc3545; color: white; }
    </style>
</head>
<body>

    <div id="login-section" class="card">
        <h2>ทดสอบระบบ Login</h2>
        <p>กดปุ่มด้านล่างเพื่อทดสอบการเข้าสู่ระบบ</p>
        <button id="login-btn">เข้าสู่ระบบด้วย Google</button>
    </div>

    <div id="main-content" class="card hidden">
        <h2 style="color: #28a745;">เข้าสู่ระบบสำเร็จ!</h2>
        <p>ระบบ Login ของ Firebase ทำงานได้อย่างสมบูรณ์</p>
        <button id="logout-btn">ออกจากระบบ</button>
    </div>

    <script type="module">
        // นำเข้าเครื่องมือจาก Firebase
        import { initializeApp } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-app.js";
        import { getAuth, signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/12.10.0/firebase-auth.js";

        // กุญแจ Firebase 
        // *** หมายเหตุ: ถ้าคุณสร้างโปรเจกต์ใหม่ใน Firebase แล้ว ให้นำกุญแจชุดใหม่มาใส่แทนตรงนี้นะครับ ***
        const firebaseConfig = {
            apiKey: "AIzaSyDHSZ6VGPTzku5WP-GSEP4tNicqvDbFIYg",
            authDomain: "gen-lang-client-0559819500.firebaseapp.com",
            projectId: "gen-lang-client-0559819500",
            storageBucket: "gen-lang-client-0559819500.firebasestorage.app",
            messagingSenderId: "358673361686",
            appId: "1:358673361686:web:44662c193968817f4e3e37",
            measurementId: "G-N90LYXXPPF"
        };

        // เริ่มต้นระบบ Firebase
        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();

        // เชื่อมปุ่มใน HTML กับคำสั่ง
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const loginSection = document.getElementById('login-section');
        const mainContent = document.getElementById('main-content');

        // สั่งให้ปุ่ม Login ทำงาน
        loginBtn.addEventListener('click', async () => {
            try {
                await signInWithPopup(auth, provider);
            } catch (error) {
