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
# 2. FUNGSI LOAD DATA (DIPERBAIKI)
# ============================================================
@st.cache_data
def load_data():
    # Nama file yang benar sesuai gambar Anda
    nama_file = "data_mahasiswa_sintesis.csv"
    
    kandidat_path = [
        nama_file,                        # Di folder yang sama
        f"bedah_kasus_2/{nama_file}",     # Di dalam sub-folder bedah_kasus_2
        f"../{nama_file}",                # Di luar folder
        f"../bedah_kasus_2/{nama_file}"   # Di folder induk bedah_kasus_2
    ]
    
    # Looping untuk mencari file
    for path in kandidat_path:
        if os.path.exists(path):
            # st.success(f"✅ Data berhasil dimuat dari: {path}") 
            return pd.read_csv(path)

    st.error(f"❌ File '{nama_file}' masih tidak ditemukan.")
    st.stop()

# Panggil fungsi load data
df = load_data()

# ============================================================
# 3. SIDEBAR - FILTER DATA
# ============================================================
st.sidebar.header("🔎 Filter Data")
filtered_df = df.copy()

# Filter otomatis untuk kolom teks/kategori
for col in df.select_dtypes(include=["object", "category"]).columns:
    unique_vals = df[col].dropna().unique().tolist()
    if 1 < len(unique_vals) <= 30: 
        pilihan = st.sidebar.multiselect(f"Pilih {col}:", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(pilihan)]

# Filter untuk kolom angka
for col in df.select_dtypes(include=["number"]).columns:
    min_val = float(df[col].min())
    max_val = float(df[col].max())
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

if "IPK" in filtered_df.columns:
    col3.metric("📈 Rata-rata IPK", f"{filtered_df['IPK'].mean():.2f}")
else:
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

# Visualisasi sederhana
num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
if num_cols:
    st.subheader("📊 Visualisasi Data")
    kolom_grafik = st.selectbox("Pilih kolom untuk melihat grafik distribusi:", num_cols)
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
