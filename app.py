import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# Sidebar Kredensial
with st.sidebar:
    st.header("🔑 Data Akun")
    # NIM Anda dimasukkan secara otomatis sebagai default
    nim = st.text_input("NIM", value="141250324") 
    password = st.text_input("Password SPADA", type="password")

# Area Utama: Pemilihan Matkul
st.subheader("Pilih Mata Kuliah")
pilihan_nama = st.selectbox("Daftar Mata Kuliah Anda:", list(JADWAL_MATKUL.keys()))

if pilihan_nama != "Pilih Mata Kuliah":
    info_matkul = JADWAL_MATKUL[pilihan_nama]
    st.info(f"**Matkul Terpilih:** {pilihan_nama}")

def proses_absen(nim, password, url, nama_matkul):
    chrome_options = Options()
    # Mode Headless agar bisa jalan di server cloud tanpa layar
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # 1. Buka halaman login
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        st.write("🔄 Melakukan Login...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()

        # 2. Periksa apakah login berhasil (mencari elemen profil atau dashboard)
        time.sleep(2) 

        # 3. Menuju Link Absen
        driver.get(url)
        st.write(f"🔄 Membuka halaman absensi {nama_matkul}...")

        # 4. Klik 'Submit attendance' (atau 'Ajukan kehadiran')
        # Menggunakan partial link text agar lebih fleksibel dengan bahasa Indonesia/Inggris
        submit_btn = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
        submit_btn.click()

        # 5. Pilih 'Hadir' (Present)
        # Mencari radio button atau teks yang mengandung 'Hadir'
        present_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        present_option.click()

        # 6. Simpan Perubahan
        driver.find_element(By.ID, "id_submitbutton").click()
        st.success(f"✅ Berhasil melakukan presensi untuk {nama_matkul}!")

    except Exception as e:
        st.error(f"❌ Gagal: Pastikan sesi absen sudah dibuka oleh dosen. \n\nLog: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

# Tombol Eksekusi
if st.button("🚀 Jalankan Presensi"):
    if nim and password and pilihan_nama != "Pilih Mata Kuliah":
        proses_absen(nim, password, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)
    else:
        st.warning("⚠️ Pastikan Password dan Mata Kuliah sudah diisi/dipilih.")
