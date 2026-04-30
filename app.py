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

# Header Antarmuka
st.title("⚡ Auto-Presensi SPADA")
st.write("Masukkan NIM dan Password manual untuk keamanan repositori GitHub.")

# Input Manual (Keamanan)
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
    chrome_options.add_argument("--window-size=1920x1080")
    
    # Wadah Log Real-time
    st.markdown("---")
    st.write("### 📝 Log Aktivitas Bot")
    status_log = st.empty()
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Pengaturan Timeout Extra (60 Detik)
        wait = WebDriverWait(driver, 60)
        driver.set_page_load_timeout(60)

        # LANGKAH 1: Login
        status_log.code("LOG: Membuka halaman login SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        status_log.code("LOG: Mengisi kredensial...")
        wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        
        # Jeda 5 detik agar server SPADA sempat memproses sesi login
        time.sleep(5)
        status_log.code("LOG: Login Berhasil! Menuju link absensi...")

        # LANGKAH 2: Buka Halaman Absen
        driver.get(url)
        status_log.code(f"LOG: Halaman {nama_matkul} termuat.")

        # LANGKAH 3: Cari Tombol Absen
        status_log.code("LOG: Mencari tombol 'Submit attendance'...")
        try:
            # Mencari tombol dengan teks parsial untuk fleksibilitas bahasa
            submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            submit_btn.click()
            status_log.code("LOG: Tombol absen ditemukan dan diklik.")
        except:
            status_log.empty()
            st.warning(f"⚠️ **Log Akhir:** Login sukses, namun tombol absen untuk **{nama_matkul}** tidak ditemukan.")
            st.info("Kemungkinan besar sesi absen belum dibuka oleh dosen atau sudah berakhir.")
            return

        # LANGKAH 4: Pilih Hadir & Simpan
        status_log.code("LOG: Memilih opsi 'Hadir'...")
        # Menggunakan XPATH untuk mencari teks "Hadir" atau "Present"
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()
        
        status_log.code("LOG: Menyimpan kehadiran...")
        driver.find_element(By.ID, "id_submitbutton").click()
        
        status_log.empty()
        st.success(f"✅ **LOG SELESAI:** Presensi **{nama_matkul}** telah berhasil dilakukan secara otomatis!")

    except Exception as e:
        status_log.empty()
        st.error("❌ **Log Error: Timeout.**")
        st.write("Server SPADA terlalu lambat merespons atau sedang dalam beban tinggi. Silakan coba lagi beberapa saat lagi.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Tombol Eksekusi
if st.button("🚀 Jalankan Presensi Sekarang", use_container_width=True):
    # Validasi Input
    if not nim_input:
        st.warning("⚠️ NIM belum diisi.")
    elif not pass_input:
        st.warning("⚠️ Password belum diisi.")
    elif pilihan_nama == "Pilih Mata Kuliah":
        st.warning("⚠️ Silakan pilih mata kuliah terlebih dahulu.")
    else:
        proses_absen(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
