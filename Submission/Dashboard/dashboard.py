import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

filepath = r"C:\Users\astennu\Downloads\Air-quality-dataset\Dashboard\merged_data.csv"
df = pd.read_csv(filepath)

df['year'] = pd.to_numeric(df['year'], errors='coerce')

mdc_clean = df.copy()  

pm_trend = mdc_clean.groupby("year")[["PM2.5", "PM10"]].mean()

with st.sidebar:
    st.title('Proyek Akhir: Analisis Data Peminjaman Sepeda :sparkles:')
    st.header('Nama: M Fajrin Wirattama')
    st.subheader('Email: fajrinwirattama21@gmail.com')
    st.subheader('Id Dicoding: wirattama')

st.title("Proyek akhir: Analisis Kualitas Udara :sparkles:")
st.subheader("Tren PM2.5 dan PM10 dari Tahun ke Tahun")
st.write("Konsentrasi PM2.5 dan PM10 fluktuatif (2013-2017), puncak 2014, turun hingga 2016, naik kembali 2017, menunjukkan ketidakstabilan kualitas udara.")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(pm_trend.index, pm_trend["PM2.5"], marker="o", linestyle="-", label="PM2.5", color="red")
ax.plot(pm_trend.index, pm_trend["PM10"], marker="s", linestyle="-", label="PM10", color="blue")
ax.set_xlabel("Tahun")
ax.set_ylabel("Konsentrasi Rata-rata")
ax.set_title("Tren PM2.5 dan PM10 dari Tahun ke Tahun")
ax.legend()
ax.grid()

st.pyplot(fig)

stations = mdc_clean["station"].unique().tolist()
selected_stations = st.sidebar.multiselect("Pilih Stasiun", stations, default=["Aotizhongxin", "Changping"])

filtered_data = mdc_clean[mdc_clean["station"].isin(selected_stations)]
co_no2_trend = filtered_data.groupby(["year", "station"])[["CO", "NO2"]].mean().reset_index()

st.subheader("Tren CO dan NO2 Berdasarkan Tahun dan Stasiun")
st.write("Tren CO dan NO2 di Aotizhongxin dan Changping fluktuatif, dengan peningkatan signifikan pada 2017, menunjukkan kualitas udara tidak membaik secara konsisten.")

plt.figure(figsize=(10, 5))
for station in selected_stations:
    subset = co_no2_trend[co_no2_trend["station"] == station]
    plt.plot(subset["year"], subset["CO"], marker="o", linestyle="-", label=f"CO - {station}")
    plt.plot(subset["year"], subset["NO2"], marker="s", linestyle="--", label=f"NO2 - {station}")

plt.xlabel("Tahun")
plt.ylabel("Konsentrasi Rata-rata")
plt.title("Tren CO dan NO2 per Stasiun")
plt.legend()
plt.grid()
st.pyplot(plt)