import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style untuk visualisasi
sns.set(style='darkgrid') # Mengubah style menjadi darkgrid agar lebih jelas

# Mendapatkan path absolut ke direktori tempat skrip ini berjalan
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR saat ini akan menjadi: C:\Users\astennu\Downloads\Submission\Dashboard

# Untuk mengakses folder 'Data' yang berada satu tingkat di atas 'Dashboard',
# kita perlu pergi ke direktori induk dari BASE_DIR, lalu gabungkan dengan 'Data'.
parent_dir = os.path.dirname(BASE_DIR)
# parent_dir akan menjadi: C:\Users\astennu\Downloads\Submission

data_folder = os.path.join(parent_dir, "Data")
# data_folder sekarang akan menjadi: C:\Users\astennu\Downloads\Submission\Data

# Gabungkan path folder data dengan nama file
aotizhongxin_filepath = os.path.join(data_folder, "PRSA_Data_Aotizhongxin_20130301-20170228.csv")
changping_filepath = os.path.join(data_folder, "PRSA_Data_Changping_20130301-20170228.csv")

# Fungsi untuk memuat data dengan caching
@st.cache_data
def load_and_clean_data():
    """
    Memuat dan membersihkan data kualitas udara dari dua stasiun.
    Menggunakan st.cache_data agar data hanya dimuat sekali.
    """
    try:
        Aotizhongxin = pd.read_csv(aotizhongxin_filepath)
        Changping = pd.read_csv(changping_filepath)
    except FileNotFoundError:
        st.error(f"File data tidak ditemukan. Pastikan file CSV berada di dalam folder 'Data' pada direktori yang sama dengan skrip ini.")
        st.error(f"Mencari file di: {aotizhongxin_filepath} dan {changping_filepath}")
        st.stop()

    # Pilih kolom yang relevan
    data_cols = ["year", "month", "day", "hour", "PM2.5", "PM10", "NO2", "CO", "station", "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
    df_aotizhongxin_selected = Aotizhongxin[data_cols]
    df_changping_selected = Changping[data_cols]

    # Gabungkan kedua dataframe
    merged_data = pd.concat([df_aotizhongxin_selected, df_changping_selected], ignore_index=True)

    # Bersihkan data: dropna dan drop_duplicates
    mdc = merged_data.dropna()
    mdc_clean = mdc.drop_duplicates()

    # Buat kolom datetime
    mdc_clean['datetime'] = pd.to_datetime(mdc_clean[['year', 'month', 'day', 'hour']])

    return mdc_clean

# Muat data
df_clean = load_and_clean_data()

# --- Sidebar untuk Informasi Proyek ---
with st.sidebar:
    st.title('Proyek Analisis Data: Kualitas Udara :sparkles:')
    st.header('Nama: M Fajrin Wirattama')
    st.subheader('Email: fajrinwirattama21@gmail.com')
    st.subheader('ID Dicoding: wirattama')

    st.markdown("---")
    st.header('Filter Data')

    # Filter Tahun
    all_years = sorted(df_clean['year'].unique())
    selected_years = st.multiselect('Pilih Tahun', all_years, default=all_years)

    # Filter Bulan
    all_months = sorted(df_clean['month'].unique())
    selected_months = st.multiselect('Pilih Bulan', all_months, default=all_months)

    # Filter Stasiun
    all_stations = sorted(df_clean['station'].unique())
    selected_stations = st.multiselect('Pilih Stasiun', all_stations, default=all_stations)

# Filter data berdasarkan pilihan pengguna
filtered_df = df_clean[
    (df_clean['year'].isin(selected_years)) &
    (df_clean['month'].isin(selected_months)) &
    (df_clean['station'].isin(selected_stations))
]

# --- Main Content ---
st.title("Proyek Analisis Data: Kualitas Udara")
st.markdown("Memahami tren dan pola polusi udara di Beijing dari Maret 2013 hingga Februari 2017.")

# Menampilkan pesan jika tidak ada data yang cocok
if filtered_df.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Silakan ubah filter Anda.")
else:
    # --- Pertanyaan Bisnis 1: Tren PM2.5 dan PM10 per Stasiun ---
    st.header('1. Tren Konsentrasi PM2.5 dan PM10 per Stasiun')
    st.write("Grafik ini menunjukkan bagaimana konsentrasi rata-rata PM2.5 dan PM10 berubah dari tahun ke tahun di Stasiun Aotizhongxin dan Stasiun Changping.")

    # Agregasi data untuk visualisasi: rata-rata tahunan per stasiun
    pm_trend_yearly_by_station = filtered_df.groupby(['year', 'station'])[['PM2.5', 'PM10']].mean().reset_index()

    if not pm_trend_yearly_by_station.empty:
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='year', y='PM2.5', hue='station', data=pm_trend_yearly_by_station,
                     marker='o', linestyle='-', palette='coolwarm', ax=ax1)
        sns.lineplot(x='year', y='PM10', hue='station', data=pm_trend_yearly_by_station,
                     marker='s', linestyle='--', palette='viridis', ax=ax1) # Warna berbeda untuk PM10
        ax1.set_xlabel("Tahun")
        ax1.set_ylabel("Konsentrasi Rata-rata ($\mu g/m^3$)")
        ax1.set_title(f"Tren Konsentrasi Rata-rata PM2.5 dan PM10 (Stasiun: {', '.join(selected_stations)})")
        ax1.set_xticks(pm_trend_yearly_by_station['year'].unique()) # Memastikan semua tahun ditampilkan
        ax1.grid(True)
        ax1.legend(title='Polutan & Stasiun')
        st.pyplot(fig1)
    else:
        st.info("Tidak ada data tren PM2.5 dan PM10 untuk filter yang dipilih.")


    # --- Pertanyaan Bisnis 2: Pola Tahunan (Bulanan) CO dan NO2 ---
    st.header('2. Pola Tahunan Konsentrasi CO dan NO2')
    st.write("Grafik ini menampilkan pola musiman (rata-rata bulanan) untuk CO dan NO2 di Stasiun Aotizhongxin dan Stasiun Changping. Perhatikan bagaimana konsentrasi polutan berfluktuasi sepanjang tahun.")

    # Agregasi data untuk visualisasi: rata-rata bulanan per stasiun
    co_no2_monthly_pattern = filtered_df.groupby(['month', 'station'])[['CO', 'NO2']].mean().reset_index()

    if not co_no2_monthly_pattern.empty:
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='month', y='CO', hue='station', data=co_no2_monthly_pattern,
                     marker='o', linestyle='-', palette='plasma', ax=ax2)
        sns.lineplot(x='month', y='NO2', hue='station', data=co_no2_monthly_pattern,
                     marker='s', linestyle='--', palette='cividis', ax=ax2) # Warna berbeda untuk NO2
        ax2.set_xlabel("Bulan")
        ax2.set_ylabel("Konsentrasi Rata-rata ($\mu g/m^3$)")
        ax2.set_title(f"Pola Bulanan Rata-rata CO dan NO2 (Stasiun: {', '.join(selected_stations)})")
        ax2.set_xticks(range(1, 13)) # Menampilkan semua bulan (1-12)
        ax2.grid(True)
        ax2.legend(title='Polutan & Stasiun')
        st.pyplot(fig2)
    else:
        st.info("Tidak ada data pola bulanan CO dan NO2 untuk filter yang dipilih.")

    # --- Tambahan: Distribusi Konsentrasi Polutan dan Parameter Lingkungan ---
    st.header('Distribusi Konsentrasi Polutan dan Parameter Lingkungan')
    st.write("Pilih salah satu parameter untuk melihat distribusinya dalam data yang difilter.")
    
    available_cols = ['PM2.5', 'PM10', 'CO', 'NO2', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    selected_pollutant_dist = st.selectbox('Pilih Parameter', available_cols)

    if not filtered_df[selected_pollutant_dist].empty:
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.histplot(filtered_df[selected_pollutant_dist], bins=50, kde=True, ax=ax3, color='teal')
        ax3.set_xlabel(f"Nilai {selected_pollutant_dist}")
        ax3.set_ylabel("Frekuensi")
        ax3.set_title(f"Distribusi {selected_pollutant_dist} (Difilter)")
        st.pyplot(fig3)
    else:
        st.info(f"Tidak ada data {selected_pollutant_dist} untuk filter yang dipilih.")

    # --- Tampilan Dataframe (Opsional) ---
    st.subheader('Data yang Difilter (Beberapa Baris Pertama)')
    st.dataframe(filtered_df.head())
