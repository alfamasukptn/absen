import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Pengaturan Halaman Streamlit
st.set_page_config(page_title="Bot Absen SPADA", page_icon="🤖")
st.title("🤖 Bot Absen SPADA UPNVY")
st.write("Gunakan bot ini untuk otomatisasi kehadiran tanpa membebani laptop.")

# Sidebar untuk Input Kredensial
with st.sidebar:
    st.header("Konfigurasi Akun")
    nim = st.text_input("NIM", placeholder="141250324")
    password = st.text_input("Password SPADA", type="password")
    link_absen = st.text_input("Link Room Absensi", placeholder="https://spada.upnvy.ac.id/mod/attendance/view.php?id=xxxx")

def jalankan_absen(nim, password, url):
    # Setup Chrome Options untuk Cloud (Headless Mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    try:
        # Inisialisasi Driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        st.info("🔄 Menghubungi server SPADA...")
        driver.get("https://spada.upnvy.ac.id/login/index.php")

        # Proses Login
        st.info("🔑 Melakukan Login...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()

        # Menuju Link Absen
        st.info("📍 Menuju lokasi presensi...")
        driver.get(url)

        # Mencari Tombol "Submit Attendance" atau "Ajukan Kehadiran"
        # Catatan: Selektor CSS mungkin perlu disesuaikan dengan teks di SPADA
        submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Submit attendance")))
        submit_btn.click()

        # Memilih "Hadir" (Present)
        st.info("✅ Memilih status 'Hadir'...")
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        # Simpan Perubahan
        driver.find_element(By.ID, "id_submitbutton").click()
        
        st.success("🎉 Absensi Berhasil Disubmit!")

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

# Tombol Eksekusi
if st.button("🚀 Jalankan Bot Sekarang"):
    if nim and password and link_absen:
        jalankan_absen(nim, password, link_absen)
    else:
        st.warning("⚠️ Mohon isi semua kolom di sidebar terlebih dahulu.")
