import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Data Jadwal Mata Kuliah Terbaru
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

st.set_page_config(page_title="Bot Absen SPADA", page_icon="🎓")
st.title("🎓 Portal Absensi Otomatis SPADA")

def proses_absen(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # 1. Login
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        st.info("🔄 Melakukan Login...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()

        time.sleep(2) 

        # 2. Menuju Link Absen
        driver.get(url)
        st.info(f"🔄 Membuka halaman {nama_matkul}...")

        # 3. Klik Submit
        submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
        submit_btn.click()

        # 4. Pilih Hadir
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        # 5. Simpan
        driver.find_element(By.ID, "id_submitbutton").click()
        st.success(f"✅ Berhasil presensi: {nama_matkul}!")

    except Exception as e:
        st.error(f"❌ Gagal: Sesi absen mungkin belum dibuka atau elemen tidak ditemukan.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Sidebar dengan Tombol Login di bawah Password
with st.sidebar:
    st.header("🔑 Data Akun")
    nim_input = st.text_input("NIM", value="141250324") 
    pass_input = st.text_input("Password SPADA", type="password")
    
    # Tombol Login diletakkan di sini
    btn_login = st.button("🚀 Jalankan Presensi", use_container_width=True)

# Area Utama: Pemilihan Matkul
st.subheader("Pilih Mata Kuliah")
pilihan_nama = st.selectbox("Daftar Mata Kuliah Anda:", list(JADWAL_MATKUL.keys()))

if pilihan_nama != "Pilih Mata Kuliah":
    st.info(f"**Matkul Terpilih:** {pilihan_nama}")

# Logika ketika tombol di sidebar diklik
if btn_login:
    if nim_input and pass_input and pilihan_nama != "Pilih Mata Kuliah":
        proses_absen(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("⚠️ Isi password dan pilih mata kuliah terlebih dahulu!")
