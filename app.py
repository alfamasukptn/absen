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
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Menyamarkan identitas bot
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
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
        wait = WebDriverWait(driver, 40)
        
        # 1. TAHAP LOGIN DENGAN PENGALIHAN PAKSA
        update_log("Membuka halaman login SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        try:
            # Tunggu elemen username muncul secara visual
            user_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))
        except:
            update_log("⚠️ Halaman utama lambat. Mencoba akses alternatif...")
            driver.get("https://spada.upnyk.ac.id/login/index.php?authmethod=manual")
            user_field = wait.until(EC.visibility_of_element_located((By.ID, "username")))

        update_log("Mengisi kredensial...")
        user_field.clear()
        user_field.send_keys(nim)
        
        pass_field = driver.find_element(By.ID, "password")
        pass_field.clear()
        pass_field.send_keys(password)
        
        time.sleep(1)
        update_log("Mencoba Login...")
        driver.find_element(By.ID, "loginbtn").click()
        
        # Cek apakah login berhasil dengan memantau URL
        time.sleep(5)
        if "login" in driver.current_url:
            update_log("❌ GAGAL: Login ditolak. Periksa kembali NIM/Password.")
            st.error("Kredensial salah atau server menolak akses.")
            return

        update_log("✅ Login Berhasil! Mengakses mata kuliah...")

        # 2. TAHAP NAVIGASI
        driver.get(url)
        time.sleep(3)
        
        # 3. TAHAP ABSENSI
        try:
            update_log("Mencari tombol presensi...")
            # Coba cari tombol attendance
            btn_absen = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            btn_absen.click()
            
            update_log("Memilih opsi 'Hadir'...")
            time.sleep(2)
            # XPath yang lebih kuat untuk berbagai kondisi bahasa
            xpath_hadir = "//input[@type='radio'][following-sibling::*[contains(text(), 'Hadir') or contains(text(), 'Present')]] | //span[contains(text(), 'Hadir')] | //label[contains(., 'Hadir')]"
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hadir))).click()
            
            update_log("Menyimpan kehadiran...")
            driver.find_element(By.ID, "id_submitbutton").click()
            
            st.success(f"🎉 Sukses! Presensi {nama_matkul} tercatat pada {get_wib_time()} WIB.")
        except:
            update_log("🏁 Selesai: Tombol absen tidak ditemukan (Mungkin sudah absen atau belum buka).")
            st.info("Bot tidak menemukan tombol 'Submit attendance'.")

    except Exception as e:
        update_log(f"💥 ERROR: Terjadi gangguan pada koneksi server SPADA.")
        with st.expander("Detail Teknis"):
            st.write(str(e))
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Jalankan Presensi"):
    if nim_input and pass_input and pilihan_nama != "Pilih Mata Kuliah":
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("⚠️ Lengkapi data terlebih dahulu.")
