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

st.set_page_config(page_title="Auto-Absen SPADA", page_icon="🎓")
st.title("🎓 Auto-Presensi SPADA")

# --- INPUT SECTION ---
col1, col2 = st.columns(2)
with col1:
    nim_input = st.text_input("NIM", placeholder="Masukkan NIM")
with col2:
    pass_input = st.text_input("Password", type="password")
pilihan_nama = st.selectbox("Pilih Mata Kuliah:", list(JADWAL_MATKUL.keys()))

def jalankan_bot(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080") # Resolusi HD agar elemen tidak tumpang tindih
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    chrome_options.binary_location = "/usr/bin/chromium"
    driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"

    st.markdown("---")
    st.write("### 📝 Log Aktivitas (WIB)")
    log_area = st.empty()
    logs = []

    def update_log(msg):
        logs.append(f"[{get_wib_time()}] {msg}")
        log_area.code("\n".join(logs))

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 45)
        
        # 1. TAHAP LOGIN
        update_log("Membuka halaman login SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        # Berikan waktu halaman untuk me-render JavaScript
        time.sleep(4) 
        
        update_log("Mengisi kredensial login...")
        try:
            # Gunakan visibility agar memastikan elemen benar-benar siap berinteraksi
            user_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
            user_field.clear()
            user_field.send_keys(nim)
            
            pass_field = driver.find_element(By.ID, "password")
            pass_field.clear()
            pass_field.send_keys(password)
            
            update_log("Mengklik tombol login...")
            time.sleep(1)
            driver.find_element(By.ID, "loginbtn").click()
        except Exception as e:
            update_log("GAGAL: Kolom login tidak merespons. Mencoba memuat ulang...")
            driver.refresh()
            time.sleep(5)
            # Re-attempt sederhana
            driver.find_element(By.ID, "username").send_keys(nim)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "loginbtn").click()

        # Jeda stabilisasi setelah login
        time.sleep(5)
        
        # Cek apakah login gagal (masih di halaman login)
        if "login" in driver.current_url.lower():
            update_log("GAGAL: Login ditolak. Periksa kembali NIM/Password Anda.")
            st.error("Login gagal. Pastikan kredensial Anda benar.")
            return

        update_log("Berhasil Login! Menuju halaman mata kuliah...")

        # 2. TAHAP NAVIGASI
        driver.get(url)
        time.sleep(3)
        update_log(f"Halaman {nama_matkul} termuat.")
        
        # 3. TAHAP ABSENSI
        try:
            update_log("Mencari tombol 'Submit attendance'...")
            # Menunggu tombol muncul dengan teks parsial
            btn_absen = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            btn_absen.click()
            
            update_log("Memilih opsi kehadiran 'Hadir'...")
            time.sleep(2)
            xpath_hadir = "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')] | //label[contains(., 'Hadir')]"
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hadir))).click()
            
            update_log("Menyimpan data kehadiran...")
            driver.find_element(By.ID, "id_submitbutton").click()
            
            st.success(f"✅ **Selesai!** Presensi {nama_matkul} sukses pada pukul {get_wib_time()} WIB.")
        except:
            update_log("SELESAI: Tombol absen tidak ditemukan. Sesi mungkin belum dibuka/sudah dilakukan.")
            st.info("Bot tidak menemukan tombol 'Submit attendance'. Silakan cek manual jika sesi seharusnya sudah buka.")

    except Exception as e:
        update_log(f"ERROR: {str(e)[:100]}...")
        st.error("Terjadi kesalahan teknis. Coba 'Reboot App' di dashboard Streamlit.")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Jalankan Presensi"):
    if nim_input and pass_input and pilihan_nama != "Pilih Mata Kuliah":
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("⚠️ Mohon lengkapi NIM, Password, dan Mata Kuliah.")
