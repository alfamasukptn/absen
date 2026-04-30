import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

st.set_page_config(page_title="Bot Absen SPADA", page_icon="⚡")
st.title("⚡ Auto-Presensi SPADA")
st.write("Masukkan NIM/Password secara manual untuk keamanan data di GitHub.")

# Input Manual
col1, col2 = st.columns(2)
with col1:
    nim_input = st.text_input("NIM", placeholder="141250324")
with col2:
    pass_input = st.text_input("Password", type="password")

pilihan_nama = st.selectbox("Pilih Mata Kuliah:", list(JADWAL_MATKUL.keys()))

def proses_absen(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    status = st.empty()
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 15) # Timeout lebih singkat agar cepat terdeteksi jika gagal

        # 1. Login
        status.info("⏳ Mencoba login...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(2)

        # 2. Cek apakah halaman absen bisa dibuka
        status.info(f"🔄 Membuka presensi {nama_matkul}...")
        driver.get(url)
        
        # 3. Deteksi Tombol Absen (Poin 4)
        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            submit_btn.click()
        except:
            status.empty()
            st.error(f"❌ **Tombol Absen Tidak Ditemukan:** Sesi absen untuk **{nama_matkul}** belum dibuka oleh dosen atau sudah berakhir.")
            return

        # 4. Pilih Hadir
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        driver.find_element(By.ID, "id_submitbutton").click()
        status.empty()
        st.success(f"✅ **BERHASIL!** Presensi **{nama_matkul}** sukses.")
        
    except Exception as e:
        status.empty()
        st.error(f"❌ **Kesalahan Sistem:** Terjadi kendala saat memproses absen. Pastikan koneksi stabil.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Logika Tombol & Peringatan Terdeteksi (Poin 1, 2, 3, 5)
if st.button("🚀 Jalankan Presensi", use_container_width=True):
    errors = []
    
    if not nim_input:
        errors.append("NIM masih kosong.")
    if not pass_input:
        errors.append("Password masih kosong.")
    if pilihan_nama == "Pilih Mata Kuliah":
        errors.append("Mata Kuliah belum dipilih.")
    
    if errors:
        # Menampilkan semua error yang terdeteksi secara campuran
        for err in errors:
            st.warning(f"⚠️ {err}")
    else:
        # Jika semua input valid, jalankan bot
        proses_absen(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
