<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BHOON KHARN AI - Final 2</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Kanit', sans-serif; background-color: #0f172a; color: white; }
        .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }
        .gradient-text { background: linear-gradient(90deg, #fbbf24, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="min-h-screen pb-10">

    <div id="login-section" class="flex flex-col items-center justify-center min-h-screen">
        <div class="glass-card p-8 rounded-2xl shadow-2xl w-full max-w-md text-center">
            <h1 class="text-4xl font-bold gradient-text mb-2">BHOON KHARN AI</h1>
            <p class="text-slate-400 mb-8">Construction Inspection Intelligence</p>
            <button id="login-btn" class="w-full bg-amber-500 hover:bg-amber-600 text-white font-bold py-3 px-6 rounded-xl transition-all transform hover:scale-105 flex items-center justify-center gap-2">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/action/google.svg" class="w-6 h-6 bg-white rounded-full p-1">
                เข้าสู่ระบบด้วย Google
            </button>
        </div>
    </div>

    <div id="main-content" class="hidden container mx-auto px-4 pt-8">
        <div class="text-center mb-10">
            <h1 class="text-5xl font-bold gradient-text mb-1">BHOON KHARN AI</h1>
            <p class="text-xl text-slate-300">Construction Inspection Intelligence</p>
            </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="space-y-6">
                <div class="glass-card p-6 rounded-2xl">
                    <h2 class="text-xl font-semibold mb-4 text-amber-400">อัปโหลดภาพตรวจงาน</h2>
                    <input type="file" id="imageInput" class="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-amber-500 file:text-white hover:file:bg-amber-600 cursor-pointer">
                    <div id="previewContainer" class="mt-4 hidden">
                        <img id="imagePreview" class="rounded-xl w-full border-2 border-slate-700">
                    </div>
                </div>

                <div class="glass-card p-6 rounded-2xl">
                    <h2 class="text-xl font-semibold mb-4 text-amber-400">งานลำดับถัดไป</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                        <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                            <h3 class="font-bold text-amber-300 mb-2 underline">งานปัจจุบัน</h3>
                            <ul class="list-disc list-inside space-y-1 text-slate-300">
                                <li>ติดตั้งโครงสร้างหลัก</li>
                                <li>เตรียมหน้างานพื้น</li>
                            </ul>
                        </div>
                        <div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
                            <h3 class="font-bold text-blue-300 mb-2 underline">งานถัดไปจากงานนี้</h3>
                            <ul class="list-disc list-inside space-y-1 text-slate-300">
                                <li>เทคอนกรีตพื้น</li>
                                <li>ติดตั้งระบบท่อ</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="space-y-6">
                <div class="glass-card p-6 rounded-2xl overflow-x-auto">
                    <h2 class="text-xl font-semibold mb-4 text-amber-400">รายการวัสดุและประมาณการราคา</h2>
                    <table class="w-full text-left text-sm">
                        <thead>
                            <tr class="border-b border-slate-700 text-slate-400">
                                <th class="pb-3">รายการวัสดุ</th>
                                <th class="pb-3 text-center">จำนวน</th>
                                <th class="pb-3 text-right">ประมาณการราคา</th>
                            </tr>
                        </thead>
                        <tbody class="text-slate-300">
                            <tr class="border-b border-slate-800/50"><td class="py-3">เหล็กเส้นฐานราก</td><td class="text-center">10 เส้น</td><td class="text-right">4,500.-</td></tr>
                            <tr class="border-b border-slate-800/50"><td class="py-3">ปูนซีเมนต์ปอร์ตแลนด์</td><td class="text-center">50 ถุง</td><td class="text-right">7,250.-</td></tr>
                            <tr class="border-b border-slate-800/50"><td class="py-3">หินก่อสร้าง 3/4</td><td class="text-center">5 คิว</td><td class="text-right">3,000.-</td></tr>
                            <tr class="border-b border-slate-800/50"><td class="py-3">ทรายหยาบ</td><td class="text-center">5 คิว</td><td class="text-right">2,750.-</td></tr>
                            <tr class="border-b border-slate-800/50"><td class="py-3">ตะปูตอกไม้/ลวดผูกเหล็ก</td><td class="text-center">5 กก.</td><td class="text-right">450.-</td></tr>
                            <tr class="border-b border-slate-800/50"><td class="py-3">คอนกรีตผสมเสร็จ</td><td class="text-center">8 คิว</td><td class="text-right">16,000.-</td></tr>
                            <tr><td class="py-3">แผ่นพื้นสำเร็จรูป</td><td class="text-center">20 แผ่น</td><td class="text-right">5,600.-</td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="glass-card p-6 rounded-2xl flex flex-col h-[300px]">
                    <h2 class="text-lg font-semibold mb-3 text-amber-400">AI Construction Chat</h2>
                    <div class="flex-grow bg-slate-900/50 rounded-xl mb-3 p-3 text-sm text-slate-400 overflow-y-auto" id="chatbox">
                        ยินดีต้อนรับครับ... สอบถามเรื่องวัสดุหรืองานก่อสร้างได้เลย
                    </div>
                    <div class="flex gap-2">
                        <input type="text" placeholder="พิมพ์ข้อความ..." class="flex-grow bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm">
                        <button class="bg-blue-600 px-4 py-2 rounded-lg text-sm font-bold">ส่ง</button>
                    </div>
                </div>

                <div class="text-center text-xs text-slate-500 space-y-1">
                    <p>ผู้ติดต่อ: ฝ่ายควบคุมงานก่อสร้าง 0xx-xxx-xxxx</p>
                    <p>หมายเหตุ: ข้อมูลการวิเคราะห์เบื้องต้นเพื่อความสะดวกในการวางแผน</p>
                    <button id="logout-btn" class="mt-4 text-slate-600 hover:text-red-400 underline">ออกจากระบบ</button>
                </div>
            </div>
        </div>
    </div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
        import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

        // กุญแจใหม่ที่คุณเตรียมมา
        const firebaseConfig = {
            apiKey: "AIzaSyDHSZ6VGPTzku5WP-GSEP4tNicqvDbFIYg",
            authDomain: "gen-lang-client-0559819500.firebaseapp.com",
            projectId: "gen-lang-client-0559819500",
            storageBucket: "gen-lang-client-0559819500.firebasestorage.app",
            messagingSenderId: "358673361686",
            appId: "1:358673361686:web:0d9d2e808287708b4e3e37",
            measurementId: "G-HE6NF53JJG"
        };

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();

        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const loginSection = document.getElementById('login-section');
        const mainContent = document.getElementById('main-content');

        // ฟังก์ชัน Login
        loginBtn.addEventListener('click', async () => {
            try {
                await signInWithPopup(auth, provider);
            } catch (error) {
                console.error("Login Error:", error);
                alert("เกิดข้อผิดพลาดในการเข้าสู่ระบบ");
            }
        });

        // ฟังก์ชัน Logout
        logoutBtn.addEventListener('click', () => signOut(auth));

        // ตรวจสอบสถานะการ Login
        onAuthStateChanged(auth, (user) => {
            if (user) {
                loginSection.classList.add('hidden');
                mainContent.classList.remove('hidden');
            } else {
                loginSection.classList.remove('hidden');
                mainContent.classList.add('hidden');
            }
        });

        // ฟังก์ชันแสดงตัวอย่างภาพ (Logic เดิม)
        document.getElementById('imageInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('imagePreview').src = event.target.result;
                    document.getElementById('previewContainer').classList.remove('hidden');
                }
                reader.readAsDataURL(file);
            }
        });
    </script>
</body>
</html>
