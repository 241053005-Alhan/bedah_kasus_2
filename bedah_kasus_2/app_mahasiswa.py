import streamlit as st
import pandas as pd
import os

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Bedah Kasus 2 - Data Mahasiswa",
    page_icon="🎓",
    layout="wide"
)

# ============================================================
# 2. FUNGSI LOAD DATA (ANTI-ERROR)
# ============================================================
@st.cache_data
def load_data():
    # Script ini akan mencari file CSV di berbagai kemungkinan folder
    # di dalam repository GitHub Anda.
    kandidat_path = [
        "data_sintesis.csv",                        # Di folder yang sama
        "bedah_kasus_2/data_sintesis.csv",          # Di dalam sub-folder
        "../data_sintesis.csv",                     # Di luar folder (folder induk)
        "data/data_sintesis.csv",                   # Di dalam folder 'data'
        os.path.join(os.path.dirname(__file__), "data_sintesis.csv"),
        os.path.join(os.path.dirname(__file__), "..", "data_sintesis.csv")
    ]
    
    # Looping untuk mencari file
    for path in kandidat_path:
        if os.path.exists(path):
            # st.success(f"✅ Data berhasil dimuat dari: {path}") # Buka komentar jika ingin melihat path
            return pd.read_csv(path)

    # --- JIKA FILE TIDAK DITEMUKAN, TAMPILKAN DIAGNOSA ---
    st.error("❌ File 'data_sintesis.csv' tidak ditemukan di repository GitHub Anda.")
    
    st.subheader("🔍 Informasi Diagnosa:")
    st.write("Pastikan Anda sudah meng-upload file `data_sintesis.csv` ke repository `bedah_kasus_2`.")
    
    st.write("**Isi folder saat ini:**")
    try:
        st.code("\n".join(os.listdir(".")))
    except:
        pass
        
    st.write("**Isi folder bedah_kasus_2 (jika ada):**")
    try:
        if os.path.exists("bedah_kasus_2"):
            st.code("\n".join(os.listdir("bedah_kasus_2")))
    except:
        pass
        
    st.stop()

# Panggil fungsi load data
df = load_data()

# ============================================================
# 3. SIDEBAR - FILTER DATA
# ============================================================
st.sidebar.header("🔎 Filter Data")
filtered_df = df.copy()

# Filter otomatis untuk kolom teks/kategori (seperti Jurusan, Prodi, dll)
for col in df.select_dtypes(include=["object", "category"]).columns:
    unique_vals = df[col].dropna().unique().tolist()
    # Hanya buat filter jika jumlah uniknya masuk akal (tidak terlalu banyak)
    if 1 < len(unique_vals) <= 30: 
        pilihan = st.sidebar.multiselect(f"Pilih {col}:", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(pilihan)]

# Filter untuk kolom angka (seperti IPK, Semester, dll)
for col in df.select_dtypes(include=["number"]).columns:
    min_val = float(df[col].min())
    max_val = float(df[col].max())
    # Hanya buat slider jika ada rentang nilai
    if min_val < max_val:
        rentang = st.sidebar.slider(
            f"Rentang {col}:",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        filtered_df = filtered_df[
            (filtered_df[col] >= rentang[0]) & (filtered_df[col] <= rentang[1])
        ]

# ============================================================
# 4. HALAMAN UTAMA - METRIK & TABEL
# ============================================================
st.title("🎓 Dashboard Data Mahasiswa")
st.markdown("Aplikasi ini menampilkan data sintesis mahasiswa. Gunakan sidebar di kiri untuk memfilter data.")

# Menampilkan Metrik Ringkasan
col1, col2, col3 = st.columns(3)
col1.metric("📄 Total Baris Data", f"{len(filtered_df):,}")
col2.metric("📊 Total Kolom", f"{df.shape[1]}")

# Coba tampilkan rata-rata IPK jika kolomnya ada
if "IPK" in filtered_df.columns:
    col3.metric("📈 Rata-rata IPK", f"{filtered_df['IPK'].mean():.2f}")
else:
    # Jika tidak ada IPK, tampilkan metrik numerik pertama yang ditemukan
    num_cols = filtered_df.select_dtypes(include=["number"]).columns
    if not num_cols.empty:
        col3.metric(f"📈 Rata-rata {num_cols[0]}", f"{filtered_df[num_cols[0]].mean():.2f}")
    else:
        col3.metric("📈 Rata-rata", "-")

st.divider()

# Tampilkan Tabel Data
st.subheader("📋 Tabel Data Mahasiswa")
st.dataframe(filtered_df, use_container_width=True)

# ============================================================
# 5. STATISTIK & VISUALISASI
# ============================================================
with st.expander("📈 Lihat Statistik Deskriptif"):
    st.write(filtered_df.describe(include="all"))

# Visualisasi sederhana (Histogram)
num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
if num_cols:
    st.subheader("📊 Visualisasi Data")
    kolom_grafik = st.selectbox("Pilih kolom untuk melihat grafik distribusi:", num_cols)
    # Menggunakan bar chart dari value_counts untuk melihat sebaran
    st.bar_chart(filtered_df[kolom_grafik].value_counts().sort_index())

# ============================================================
# 6. FITUR DOWNLOAD DATA
# ============================================================
st.subheader("⬇️ Unduh Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Data Terfilter (CSV)",
    data=csv,
    file_name="data_mahasiswa_terfilter.csv",
    mime="text/csv",
)
