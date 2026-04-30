import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import shutil

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

col1, col2 = st.columns(2)
with col1:
    nim_input = st.text_input("NIM", placeholder="141250324")
with col2:
    pass_input = st.text_input("Password", type="password")
pilihan_nama = st.selectbox("Pilih Mata Kuliah:", list(JADWAL_MATKUL.keys()))

def jalankan_bot(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Deteksi otomatis path chromium dan driver di server Linux
    chrome_options.binary_location = "/usr/bin/chromium"
    driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"

    st.markdown("---")
    st.write("### 📝 Log Aktivitas")
    log_status = st.empty()
    
    try:
        # Menggunakan driver sistem yang sesuai dengan versi browser
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 45)
        
        log_status.code("LOG: Membuka halaman login...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        
        time.sleep(5)
        log_status.code("LOG: Berhasil masuk. Menuju link absen...")

        driver.get(url)
        
        try:
            log_status.code("LOG: Mencari tombol kehadiran...")
            btn_absen = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            btn_absen.click()
            
            log_status.code("LOG: Memilih opsi 'Hadir'...")
            xpath_hadir = "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')] | //label[contains(., 'Hadir')]"
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hadir))).click()
            
            driver.find_element(By.ID, "id_submitbutton").click()
            st.success(f"✅ **Berhasil!** Presensi {nama_matkul} sukses.")
        except:
            st.error(f"❌ Tombol absen tidak ditemukan.")

    except Exception as e:
        st.error(f"⚠️ Terjadi kesalahan versi: {str(e)[:150]}...")
    finally:
        if 'driver' in locals():
            driver.quit()

if st.button("🚀 Jalankan Presensi"):
    if nim_input and pass_input and pilihan_nama != "Pilih Mata Kuliah":
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("⚠️ Mohon lengkapi data.")
