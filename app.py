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

# Konfigurasi UI/UX Streamlit
st.set_page_config(page_title="Auto-Absen SPADA", page_icon="🎓", layout="centered")

# Custom CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Portal Absensi Otomatis")
st.subheader("Manajemen Informatika & Bisnis")
st.write("Silakan masukkan kredensial untuk mulai melakukan presensi otomatis.")

# Input Section (Data dihapus dari kode demi keamanan GitHub)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nim_input = st.text_input("NIM", placeholder="Masukkan NIM Anda") 
    with col2:
        pass_input = st.text_input("Password", type="password", placeholder="Password SPADA")

    pilihan_nama = st.selectbox("Pilih Mata Kuliah:", list(JADWAL_MATKUL.keys()))

def jalankan_bot(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Placeholder untuk Log
    st.info(f"🚀 Memulai bot untuk mata kuliah: **{nama_matkul}**")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 45) # Mengikuti durasi tunggu bot.py yang stabil
        
        # Step 1: Login
        status_text.text("Menuju halaman login...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        progress_bar.progress(20)
        
        status_text.text("Memasukkan kredensial...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        progress_bar.progress(40)
        
        time.sleep(3) # Jeda stabilisasi sesi
        
        # Step 2: Halaman Absen
        status_text.text(f"Membuka link absen {nama_matkul}...")
        driver.get(url)
        progress_bar.progress(60)
        
        # Step 3: Klik Submit
        status_text.text("Mencari tombol kehadiran...")
        try:
            # Menggunakan logika pencarian teks yang lebih luwes
            btn_absen = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            btn_absen.click()
            status_text.text("Tombol absen ditemukan!")
        except:
            st.error(f"❌ Tombol absen tidak ditemukan. Sesi untuk {nama_matkul} mungkin belum dibuka.")
            return

        progress_bar.progress(80)
        
        # Step 4: Pilih Hadir & Simpan
        status_text.text("Memilih opsi 'Hadir'...")
        opsi_hadir = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')]")))
        opsi_hadir.click()
        
        driver.find_element(By.ID, "id_submitbutton").click()
        progress_bar.progress(100)
        
        st.success(f"✅ **Berhasil!** Presensi **{nama_matkul}** telah tercatat di sistem.")
        status_text.empty()

    except Exception as e:
        st.error(f"⚠️ Terjadi kendala teknis. Pastikan server SPADA tidak sedang down.")
    finally:
        if 'driver' in locals():
            driver.quit()

# Trigger Tombol
if st.button("🚀 Jalankan Presensi Sekarang"):
    # Validasi Input (Deteksi Campuran)
    errors = []
    if not nim_input: errors.append("NIM belum diisi.")
    if not pass_input: errors.append("Password belum diisi.")
    if pilihan_nama == "Pilih Mata Kuliah": errors.append("Anda belum memilih mata kuliah.")
    
    if errors:
        for err in errors:
            st.warning(f"⚠️ {err}")
    else:
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)

st.markdown("---")
st.caption("Aplikasi ini dibuat untuk membantu otomatisasi presensi mahasiswa UPNVY. Gunakan dengan bijak.")
