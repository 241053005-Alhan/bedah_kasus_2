# app_mahasiswa.py
import streamlit as st
import pandas as pd
import os

# ============================================================
# Konfigurasi Halaman
# ============================================================
st.set_page_config(
    page_title="Bedah Kasus 2 - Data Mahasiswa",
    page_icon="🎓",
    layout="wide"
)

# ============================================================
# Fungsi Load Data
# ============================================================
@st.cache_data
def load_data(path: str = "data_sintesis.csv") -> pd.DataFrame:
    """
    Membaca file CSV dan mengembalikan DataFrame.
    Jika file tidak ditemukan, coba beberapa lokasi alternatif.
    """
    kandidat_path = [
        path,
        os.path.join("data", path),
        os.path.join("bedah_kasus_2", path),
        os.path.join(os.path.dirname(__file__), path),
    ]
    for p in kandidat_path:
        if os.path.exists(p):
            return pd.read_csv(p)

    st.error(
        f"❌ File '{path}' tidak ditemukan. "
        f"Pastikan file CSV berada di folder yang sama dengan script ini."
    )
    st.stop()


# ============================================================
# Muat Data  <-- INI BAGIAN YANG TADI ERROR (baris ~22)
# ============================================================
df = load_data("data_sintesis.csv")


# ============================================================
# Sidebar - Filter
# ============================================================
st.sidebar.header("🔎 Filter Data")

# Filter otomatis untuk kolom kategorikal (jika ada)
filtered_df = df.copy()

for col in df.select_dtypes(include=["object", "category"]).columns:
    unique_vals = df[col].dropna().unique().tolist()
    if 1 < len(unique_vals) <= 30:  # batasi agar sidebar tidak penuh
        pilihan = st.sidebar.multiselect(f"{col}", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(pilihan)]

# Filter numerik (opsional)
for col in df.select_dtypes(include=["number"]).columns:
    min_val = float(df[col].min())
    max_val = float(df[col].max())
    if min_val < max_val:
        rentang = st.sidebar.slider(
            f"{col}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        filtered_df = filtered_df[
            (filtered_df[col] >= rentang[0]) & (filtered_df[col] <= rentang[1])
        ]


# ============================================================
# Header & Ringkasan
# ============================================================
st.title("🎓 Bedah Kasus 2 — Dashboard Data Mahasiswa")
st.markdown("Aplikasi ini menampilkan data sintesis mahasiswa yang dapat difilter melalui sidebar.")

col1, col2, col3 = st.columns(3)
col1.metric("📄 Total Baris", f"{len(filtered_df):,}")
col2.metric("📊 Total Kolom", f"{df.shape[1]}")
if "IPK" in filtered_df.columns:
    col3.metric("📈 Rata-rata IPK", f"{filtered_df['IPK'].mean():.2f}")
else:
    col3.metric("📈 Rata-rata (kolom numerik)", 
                f"{filtered_df.select_dtypes('number').mean().mean():.2f}"
                if not filtered_df.select_dtypes('number').empty else "-")

st.divider()


# ============================================================
# Tabel Data
# ============================================================
st.subheader("📋 Tabel Data")
st.dataframe(filtered_df, use_container_width=True)


# ============================================================
# Statistik Deskriptif
# ============================================================
with st.expander("📈 Statistik Deskriptif"):
    st.write(filtered_df.describe(include="all"))


# ============================================================
# Grafik (jika ada kolom numerik)
# ============================================================
num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
if num_cols:
    st.subheader("📊 Visualisasi")
    kolom_grafik = st.selectbox("Pilih kolom untuk histogram:", num_cols)
    st.bar_chart(filtered_df[kolom_grafik].value_counts().sort_index())


# ============================================================
# Unduh Data
# ============================================================
st.subheader("⬇️ Unduh Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download data terfilter (CSV)",
    data=csv,
    file_name="data_mahasiswa_filtered.csv",
    mime="text/csv"
)
