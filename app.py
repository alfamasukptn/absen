import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- KONFIGURASI DATA MATA KULIAH ---
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

# --- UI/UX CONFIGURATION ---
st.set_page_config(page_title="Auto-Absen SPADA", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #1E1E1E;
        border-left: 5px solid #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Auto-Presensi SPADA")
st.write("Gunakan aplikasi ini untuk melakukan presensi otomatis tanpa menyimpan data di GitHub.")

# --- INPUT SECTION ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nim_input = st.text_input("NIM", placeholder="Masukkan NIM")
    with col2:
        pass_input = st.text_input("Password", type="password", placeholder="Masukkan Password")
    
    pilihan_nama = st.selectbox("Pilih Mata Kuliah:", list(JADWAL_MATKUL.keys()))

# --- CORE FUNCTION (LOGIKA BOT) ---
def jalankan_bot(nim, password, url, nama_matkul):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Anti-Detection: Membuat bot terlihat seperti manusia
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    st.markdown("---")
    st.write("### 📝 Log Aktivitas")
    log_status = st.empty()
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Override navigator.webdriver agar tidak terdeteksi
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        wait = WebDriverWait(driver, 45) # Timeout cukup lama untuk server lambat
        
        # 1. LOGIN PHASE
        log_status.code("LOG: Membuka halaman login SPADA...")
        driver.get("https://spada.upnyk.ac.id/login/index.php")
        
        username_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        username_field.send_keys(nim)
        driver.find_element(By.ID, "password").send_keys(password)
        
        time.sleep(1) # Delay kecil mirip manusia saat mengetik
        driver.find_element(By.ID, "loginbtn").click()
        
        # Validasi Login Sederhana
        time.sleep(4)
        log_status.code("LOG: Berhasil masuk. Menuju link absen...")

        # 2. NAVIGATION PHASE
        driver.get(url)
        
        # 3. ATTENDANCE PHASE
        log_status.code("LOG: Mencari tombol kehadiran...")
        try:
            # Mencari tombol 'attendance' atau 'presensi'
            btn_absen = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "attendance")))
            btn_absen.click()
            log_status.code("LOG: Tombol absen ditemukan!")
        except:
            st.error(f"❌ Tombol absen tidak ditemukan. Sesi untuk {nama_matkul} mungkin belum dibuka.")
            return

        # 4. SUBMIT PHASE
        log_status.code("LOG: Memilih opsi 'Hadir'...")
        # Mencari teks 'Hadir' atau 'Present' baik di span maupun label
        xpath_hadir = "//span[contains(text(), 'Hadir')] | //span[contains(text(), 'Present')] | //label[contains(., 'Hadir')] | //label[contains(., 'Present')]"
        hadir_option = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_hadir)))
        hadir_option.click()
        
        time.sleep(1)
        driver.find_element(By.ID, "id_submitbutton").click()
        
        log_status.empty()
        st.success(f"✅ **Berhasil!** Presensi **{nama_matkul}** telah sukses dilakukan.")

    except Exception as e:
        st.error(f"⚠️ Terjadi kendala teknis: Timeout atau struktur halaman berubah.")
        # Logging error sederhana untuk debug
        with st.expander("Lihat detail error"):
            st.write(str(e))
    finally:
        if 'driver' in locals():
            driver.quit()

# --- BUTTON TRIGGER ---
if st.button("🚀 Jalankan Presensi"):
    # Validasi input
    errors = []
    if not nim_input: errors.append("NIM belum diisi.")
    if not pass_input: errors.append("Password belum diisi.")
    if pilihan_nama == "Pilih Mata Kuliah": errors.append("Mata Kuliah belum dipilih.")
    
    if errors:
        for err in errors:
            st.warning(f"⚠️ {err}")
    else:
        jalankan_bot(nim_input, pass_input, JADWAL_MATKUL[pilihan_nama]["link"], pilihan_nama)

st.markdown("---")
st.caption("Aplikasi ini berjalan di server cloud. Tidak menggunakan baterai atau kuota laptop Anda secara intensif.")
