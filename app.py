import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import shutil
import pytz
from datetime import datetime

# --- KONFIGURASI WAKTU INDONESIA (WIB) ---
def get_wib_time():
    try:
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime("%H:%M:%S")
    except:
        return time.strftime("%H:%M:%S")

# --- DATA MATA KULIAH ---
JADWAL_MATKUL = {
    "Pilih Mata Kuliah": {"link": ""},
    "EKO MAKRO": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=750171"},
    "KEWIRAUSAHAAN": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=746515"},
    "STABIS": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=756354"},
    "KOMBIS": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=748414"},
    "BELNEG": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=762229"},
    "OLAHRAGA": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=761521"},
    "PENDIDIKAN PANCASILA": {"link": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=766147"}
}

st.set_page_config(page_title="SPADA Auto-Pilot", page_icon="⚡", layout="centered")

# --- HTML & CSS CUSTOM ---
st.markdown("""
    <style>
    /* Mengubah Background Utama */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Styling Card/Container */
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    /* Animasi Title */
    .title-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: -webkit-linear-gradient(#eee, #333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 40px;
        margin-bottom: 10px;
    }

    /* Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        border-radius: 12px;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5);
    }

    /* Log Box Styling */
    .stCodeBlock {
        border-radius: 10px !important;
        border: 1px solid #4facfe !important;
    }
    </style>
    
    <div class="title-text">⚡ SPADA AUTO-PILOT</div>
    <p style="text-align: center; color: #b0b0b0;">Automated Attendance System for Management Students</p>
    """, unsafe_allow_html=True)

# --- INPUT SECTION ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nim_input = st.text_input("NIM", placeholder="Contoh: 141250324")
    with col2:
        pass_input = st.text_input("Password SPADA", type="password")
    
    pilihan_nama = st.selectbox("Pilih Mata Kuliah", list(JADWAL_MATKUL.keys()))
    st.markdown('</div>', unsafe_allow_html=True)

# --- JAVASCRIPT UNTUK NOTIFIKASI ---
# (Opsional: Memberikan alert browser saat proses selesai)
def browser_notification(msg):
    js_code = f"alert('{msg}');"
    st.components.v1.html(f"<script>{js_code}</script>", height=0)

# --- CORE FUNCTION ---
def jalankan_bot(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"

    st.write("### 📝 Live System Logs")
    log_area = st.empty()
    logs = []

    def update_log(msg):
        logs.append(f"[{get_wib_time()}] {msg}")
        log_area.code("\n".join(logs))

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 40)
        
        update_log("🚀 Initiating connection to SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        # Deteksi Elemen Login
        user_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        update_log("🔑 Injecting credentials...")
        user_field.send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(5)
        if "login" in driver.current_url:
            update_log("❌ Error: Unauthorized access. Check NIM/Pass.")
            st.error("Credential mismatch.")
            return

        update_log(f"🔓 Authorized! Accessing {nama_matkul}...")
        driver.get(url)
        
        try:
            update_log("🔍 Scanning for attendance button...")
            btn_absen = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            btn_absen.click()
            
            update_log("🎯 Selecting 'Hadir' option...")
            xpath_hadir = "//span[contains(text(), 'Hadir')] | //label[contains(., 'Hadir')]"
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hadir))).click()
            
            driver.find_element(By.ID, "id_submitbutton").click()
            update_log("✅ Protocol Success: Data synced to SPADA.")
            st.balloons()
            browser_notification(f"Absen {nama_matkul} Berhasil!")
        except:
            update_log("⚠️ Status: Button not found. You might already be checked-in.")

    except Exception as e:
        update_log(f"💥 System Crash: {str(e)[:50]}")
    finally:
        if 'driver' in locals():
            driver.quit()

# --- TRIGGER ---
if st.button("🚀 DEPLOY PROTOCOL"):
    if nim_input and pass_input and pilihan_nama != "Pilih Mata Kuliah":
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("Please fill all required fields.")

st.markdown("<p style='text-align: center; margin-top: 50px; opacity: 0.5;'>Built for UPNVY Management Students</p>", unsafe_allow_html=True)
