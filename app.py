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
    
    # Tempat menampilkan log secara real-time
    log_container = st.container()
    with log_container:
        st.write("### 📝 Log Aktivitas Bot")
        status_log = st.empty()
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 30) # Waktu tunggu ditingkatkan ke 30 detik

        # TAHAP 1: Akses Halaman Login
        status_log.code("LOG: Mengakses halaman login SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        # TAHAP 2: Login
        status_log.code("LOG: Memasukkan NIM dan Password...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(3)
        status_log.code("LOG: Berhasil Login! Menuju halaman mata kuliah...")

        # TAHAP 3: Buka Halaman Absensi
        driver.get(url)
        status_log.code(f"LOG: Halaman {nama_matkul} berhasil dibuka.")

        # TAHAP 4: Deteksi Tombol Absen
        status_log.code("LOG: Mencari tombol 'Submit attendance'...")
        try:
            # Mencari tombol dengan teks 'Submit attendance' atau 'Ajukan kehadiran'
            submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            submit_btn.click()
            status_log.code("LOG: Tombol ditemukan dan diklik.")
        except:
            status_log.empty()
            st.warning("⚠️ **Log Akhir:** Berhasil Login, tetapi **Tombol Absen TIDAK ditemukan**.")
            st.error(f"Sesi absen untuk **{nama_matkul}** belum dibuka oleh dosen atau link salah.")
            return

        # TAHAP 5: Pilih Hadir & Simpan
        status_log.code("LOG: Memilih opsi 'Hadir'...")
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()
        
        driver.find_element(By.ID, "id_submitbutton").click()
        status_log.empty()
        st.success(f"✅ **LOG: PROSES SELESAI.** Presensi {nama_matkul} sukses.")

    except Exception as e:
        status_log.empty()
        st.error(f"❌ **Log Error:** Terjadi Timeout. Halaman terlalu lambat dimuat atau struktur web berubah.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Peringatan input kosong
if st.button("🚀 Jalankan Presensi", use_container_width=True):
    if not nim_input or not pass_input or pilihan_nama == "Pilih Mata Kuliah":
        st.warning("⚠️ Mohon lengkapi NIM, Password, dan pilih Mata Kuliah.")
    else:
        proses_absen(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
