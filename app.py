import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Konfigurasi Kredensial Otomatis
NIM_USER = "141250324"
PASS_USER = "Arveyalfap7_"

# Data Jadwal Mata Kuliah
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

st.set_page_config(page_title="Auto Absen SPADA", page_icon="⚡")
st.title("⚡ Auto-Presensi SPADA")
st.write(f"Sistem otomatis untuk NIM: **{NIM_USER}**")

def proses_absen(url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    status_placeholder = st.empty()
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # Login Otomatis
        status_placeholder.info(f"🔄 Sedang login untuk {nama_matkul}...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(NIM_USER)
        driver.find_element(By.ID, "password").send_keys(PASS_USER)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(2)

        # Menuju Link Absen
        driver.get(url)
        
        # Klik Submit Attendance
        submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
        submit_btn.click()

        # Pilih Hadir
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        # Simpan
        driver.find_element(By.ID, "id_submitbutton").click()
        
        status_placeholder.empty()
        st.success(f"✅ BERHASIL: Presensi {nama_matkul} sukses dilakukan!")

    except Exception as e:
        status_placeholder.empty()
        st.error(f"❌ GAGAL: Sesi absen {nama_matkul} belum tersedia atau sudah ditutup.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Tampilan Utama: Hanya Pilih Matkul
pilihan_nama = st.selectbox("Pilih Mata Kuliah untuk Absen:", list(JADWAL_MATKUL.keys()))

# Bot Langsung Berjalan Begitu Matkul Dipilih
if pilihan_nama != "Pilih Mata Kuliah":
    proses_absen(JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
