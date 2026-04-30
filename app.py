import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Konfigurasi Kredensial Otomatis (Hardcoded)
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

# Header Aplikasi
st.title("⚡ Auto-Presensi SPADA")
st.caption(f"Sistem Otomatis | Pengguna: {NIM_USER}")
st.divider()

def proses_absen(url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Placeholder untuk status progres
    status = st.empty()
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # 1. Login Otomatis
        status.info(f"⏳ Sedang login ke SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(NIM_USER)
        driver.find_element(By.ID, "password").send_keys(PASS_USER)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(2)

        # 2. Menuju Link Absen
        status.info(f"🔄 Membuka presensi {nama_matkul}...")
        driver.get(url)
        
        # 3. Klik Submit Attendance
        submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
        submit_btn.click()

        # 4. Pilih Hadir
        status.info(f"🖊️ Mengisi kehadiran 'Hadir'...")
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        # 5. Simpan
        driver.find_element(By.ID, "id_submitbutton").click()
        
        status.empty()
        st.success(f"✅ **BERHASIL!** Presensi untuk mata kuliah **{nama_matkul}** telah tercatat.")

    except Exception as e:
        status.empty()
        st.error(f"❌ **GAGAL:** Sesi absen untuk **{nama_matkul}** belum dibuka atau sudah berakhir.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Tampilan Utama
pilihan_nama = st.selectbox(
    "Silakan Pilih Mata Kuliah:", 
    list(JADWAL_MATKUL.keys()),
    help="Bot akan langsung berjalan setelah Anda memilih mata kuliah."
)

# Eksekusi Otomatis (Zero-Click)
if pilihan_nama != "Pilih Mata Kuliah":
    proses_absen(JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)

# Footer info
st.divider()
st.markdown("<small>Aplikasi ini berjalan di cloud. Tidak menggunakan resource laptop Anda.</small>", unsafe_allow_html=True)
