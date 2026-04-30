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

# --- HTML & CSS CUSTOM (Premium Look) ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #1e1e2f, #0f0c29);
        color: #ffffff;
    }
    
    .main-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(0, 242, 254, 0.2);
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .title-text {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 45px;
    }

    div.stButton > button:first-child {
        width: 100%;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        border: none;
        color: white;
        padding: 18px;
        font-weight: bold;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
    }
    
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 198, 255, 0.6);
        transform: scale(1.02);
    }
    </style>
    
    <div class="title-text">⚡ SPADA AUTO-PILOT</div>
    <p style="text-align: center; color: #888; margin-bottom: 30px;">Digital Presence Protocol v2.0</p>
    """, unsafe_allow_html=True)

# --- INPUT SECTION ---
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nim_input = st.text_input("NIM Identity", placeholder="141250324")
    with col2:
        pass_input = st.text_input("Access Key", type="password")
    
    pilihan_nama = st.selectbox("Select Target Course", list(JADWAL_MATKUL.keys()))
    st.markdown('</div>', unsafe_allow_html=True)

def jalankan_bot(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"

    log_area = st.empty()
    logs = []

    def update_log(msg):
        logs.append(f"[{get_wib_time()}] {msg}")
        log_area.code("\n".join(logs))

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 50) # Ditambah menjadi 50 detik
        
        update_log("🚀 Bypassing Firewall & Connecting...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        # Penanganan Retry Login
        try:
            user_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        except:
            update_log("⚠️ Connection sluggish. Forcing reload...")
            driver.refresh()
            user_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))

        update_log("🔑 Credentials injected.")
        user_field.send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(5)
        update_log(f"🔓 Tunnel established to: {nama_matkul}")
        driver.get(url)
        
        try:
            # Cari tombol absen
            btn_absen = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "attendance")))
            driver.execute_script("arguments[0].click();", btn_absen) # Click via JS lebih stabil
            
            update_log("🎯 Scanning presence radio...")
            xpath_hadir = "//span[contains(text(), 'Hadir')] | //label[contains(., 'Hadir')]"
            target = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hadir)))
            driver.execute_script("arguments[0].click();", target)
            
            driver.find_element(By.ID, "id_submitbutton").click()
            update_log("✅ DATABASE SYNCED. PRESENCE SECURED.")
            st.balloons()
        except:
            update_log("🏁 Protocol Inactive: Attendance window closed or already signed.")

    except Exception as e:
        update_log(f"💥 SYSTEM OVERLOAD: Check your network/credentials.")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 DEPLOY PROTOCOL"):
    if nim_input and pass_input and pilihan_nama != "Pilih Mata KulIAL":
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
