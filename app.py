import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Data Jadwal Mata Kuliah (Sesuaikan LINK dengan URL SPADA yang asli)
JADWAL_MATKUL = {
    "Pilih Mata Kuliah": {"link": "", "hari": ""},
    "Manajemen Operasi": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=1", "hari": "Senin 07:01"},
    "Statistika Bisnis": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=2", "hari": "Selasa 14:31"},
    "Akuntansi Biaya": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=3", "hari": "Rabu 07:21"},
    "Ekonomi Makro": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=4", "hari": "Kamis 12:01"},
    "Manajemen Pemasaran": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=5", "hari": "Jumat 07:31"},
    "Perilaku Organisasi": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=6", "hari": "Selasa 08:01"},
    "Etika Bisnis": {"link": "https://spada.upnvy.ac.id/mod/attendance/view.php?id=7", "hari": "Senin 09:31"}
}

st.set_page_config(page_title="Auto Absen SPADA", page_icon="🎓")
st.title("🎓 Portal Absensi Otomatis SPADA")

# Sidebar Kredensial
with st.sidebar:
    st.header("🔑 Data Akun")
    nim = st.text_input("NIM", value="141250324") # NIM Anda otomatis terisi
    password = st.text_input("Password SPADA", type="password")

# Area Utama: Pemilihan Matkul
st.subheader("Pilih Jadwal Kuliah")
pilihan_nama = st.selectbox("Daftar Mata Kuliah Anda:", list(JADWAL_MATKUL.keys()))

if pilihan_nama != "Pilih Mata Kuliah":
    info_matkul = JADWAL_MATKUL[pilihan_nama]
    st.info(f"**Matkul:** {pilihan_nama} | **Jadwal:** {info_matkul['hari']}")

def proses_absen(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # Login
        driver.get("https://spada.upnvy.ac.id/login/index.php")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()

        # Ke Link Absen
        driver.get(url)
        st.write(f"🔄 Mencoba absen untuk {nama_matkul}...")

        # Klik 'Submit attendance'
        submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Submit attendance")))
        submit_btn.click()

        # Pilih 'Hadir'
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        # Simpan
        driver.find_element(By.ID, "id_submitbutton").click()
        st.success(f"✅ Berhasil absen di matkul: {nama_matkul}")

    except Exception as e:
        st.error(f"❌ Gagal: Pastikan sesi absen sudah dibuka di SPADA. Error: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

# Tombol Eksekusi
if st.button("🚀 Jalankan Absen Sekarang"):
    if nim and password and pilihan_nama != "Pilih Mata Kuliah":
        proses_absen(nim, password, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("⚠️ Pastikan NIM, Password, dan Mata Kuliah sudah dipilih.")
