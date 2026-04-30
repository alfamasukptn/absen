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
    
    status = st.empty()
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20) # Waktu tunggu ditambah untuk mengatasi server lambat

        # 1. Tahap Login
        status.info("⏳ Mencoba login ke SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        try:
            wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "loginbtn").click()
        except:
            st.error("❌ Gagal Login: Kolom username/password tidak ditemukan. Cek server SPADA.")
            return

        time.sleep(2)

        # 2. Tahap Buka Link Absen
        status.info(f"🔄 Membuka presensi {nama_matkul}...")
        driver.get(url)
        
        # 3. Deteksi Tombol Absen Spesifik (Poin 4)
        try:
            submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            submit_btn.click()
        except:
            st.error(f"❌ **Tombol Absen Tidak Ada:** Sesi untuk {nama_matkul} belum dibuka dosen.")
            return

        # 4. Pilih Hadir
        try:
            present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
            present_option.click()
            driver.find_element(By.ID, "id_submitbutton").click()
            st.success(f"✅ **BERHASIL!** Presensi {nama_matkul} sukses.")
        except:
            st.error("❌ Gagal memilih opsi 'Hadir'. Mungkin format halaman berubah.")

    except Exception as e:
        st.error(f"❌ **Kesalahan Sistem:** Terjadi kendala teknis (Timeout).")
    finally:
        status.empty()
        if 'driver' in locals():
            driver.quit()

# Sistem Peringatan Terdeteksi (Poin 1, 2, 3, 5)
if st.button("🚀 Jalankan Presensi", use_container_width=True):
    errors = []
    if not nim_input: errors.append("NIM kosong.") # Poin 1
    if not pass_input: errors.append("Password kosong.") # Poin 2
    if pilihan_nama == "Pilih Mata Kuliah": errors.append("Matkul belum dipilih.") # Poin 3
    
    if errors:
        for err in errors:
            st.warning(f"⚠️ {err}") # Deteksi campuran
    else:
        proses_absen(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
