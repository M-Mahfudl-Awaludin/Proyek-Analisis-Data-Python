import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from datetime import datetime
sns.set(style='dark')

# Load dataset
day_df = pd.read_csv("day_data.csv")
hour_df = pd.read_csv("hour_data.csv")
df = pd.read_csv("all_data.csv")

# Pastikan kolom 'date' bertipe datetime
day_df["date"] = pd.to_datetime(day_df["date"])
hour_df["date"] = pd.to_datetime(hour_df["date"])

# Sorting data berdasarkan tanggal
day_df = day_df.sort_values(by="date")
hour_df = hour_df.sort_values(by="date")

# Hitung Moving Average
hour_df['rolling_mean'] = hour_df['total_rentals'].rolling(window=24).mean()  # 24 jam rata-rata
day_df['rolling_mean'] = day_df['total_rentals'].rolling(window=7).mean()  # 7 hari rata-rata

# Identifikasi hari dengan penyewaan di atas/bawah rata-rata
mean_rentals = day_df['total_rentals'].mean()
std_rentals = day_df['total_rentals'].std()

day_df['rental_category'] = day_df['total_rentals'].apply(
    lambda x: 'High' if x > (mean_rentals + std_rentals) else ('Low' if x < (mean_rentals - std_rentals) else 'Normal')
)

# Rentang tanggal minimal dan maksimal
min_date = day_df["date"].min()
max_date = day_df["date"].max()

# judul dashboard interaktif
text = "Welcome to Mahfud GoBike Dashboard :bicyclist:"
titlePlaceholder = st.empty()
titleText = ""
for char in text:
    titleText += char
    titlePlaceholder.markdown(f"### {titleText}")
    time.sleep(0.03)
st.image("dataset-cover.jpg") # gambar didapatkan pada sumber dataset (kaggle)


# sidebar yang berisi filtering
with st.sidebar:
    st.header("GoBike Dashboard :bicyclist:")
    st.image("dataset-cover.jpg")

    # Pilihan mode filter waktu (Rentang Waktu atau Tahun & Bulan), hanya bisa menggunakan salah satu
    useDateRange = st.checkbox(" Use range time", value=True)

    if useDateRange:
        # jika pakai rentang waktu, filter tahun dan bulan dinonaktifkan
        start_date, end_date = st.date_input(
            label=':calendar: Range time',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
        year_filter = None
        month_filter = None
    else:
        # jika pakai filter tahun & bulan, rentang waktu dinonaktifkan
        start_date, end_date = None, None
        year_filter = st.selectbox(":date: Select Year", sorted(day_df["year"].unique()))
        month_filter = st.selectbox(":calendar: Select Month", sorted(day_df["month"].unique()))

    # Filter cuaca bisa filter cuaca apa saja yang mau ditampilkan
    weatherFilter = st.sidebar.multiselect(
        ":sun_behind_rain_cloud: Select weather condition",
        day_df["weather_situation"].unique(),
        default=day_df["weather_situation"].unique()
    
    )

# menampilkan hasil pilihan
st.write("### :mag: Selected Filter:")

if useDateRange:
    st.write(f"Range time: {start_date} to {end_date}")
else:
    st.write(f"Year: {year_filter}, Month: {month_filter}")

# Filter dataset berdasarkan input pengguna
if useDateRange:
    dayFiltered = day_df[
        (day_df["date"] >= pd.to_datetime(start_date)) &
        (day_df["date"] <= pd.to_datetime(end_date)) &
        (day_df["weather_situation"].isin(weatherFilter))
    ]
    hourFiltered = hour_df[
        (hour_df["date"] >= pd.to_datetime(start_date)) &
        (hour_df["date"] <= pd.to_datetime(end_date)) &
        (hour_df["weather_situation"].isin(weatherFilter))
    ]
else:
    dayFiltered = day_df[
        (day_df["date"].dt.year == year_filter) &
        (day_df["date"].dt.month == month_filter) &
        (day_df["weather_situation"].isin(weatherFilter))
    ]
    hourFiltered = hour_df[
        (hour_df["date"].dt.year == year_filter) &
        (hour_df["date"].dt.month == month_filter) &
        (hour_df["weather_situation"].isin(weatherFilter))
    ]

# Visualisasi Moving Average
st.write("## 📈 Bike Rental Trend (7-day Moving Average)")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(dayFiltered["date"], dayFiltered["rolling_mean"], label="7-day Moving Average", color="blue")
ax.scatter(dayFiltered["date"], dayFiltered["total_rentals"], label="Daily Rentals", alpha=0.5, color="orange")
ax.axhline(mean_rentals, color="red", linestyle="dashed", label="Average Rentals")
ax.set_xlabel("Date")
ax.set_ylabel("Total Rentals")
ax.set_title("Tren Penyewaan Sepeda (7-day Moving Average)")
ax.legend()
st.pyplot(fig)

# Tampilkan kategori hari berdasarkan rental
st.write("## 📊 Rental Category Analysis")
category_counts = dayFiltered["rental_category"].value_counts()
st.bar_chart(category_counts)

st.write("### ℹ️ Explanation:")
st.write("""
- **High**: Penyewaan di atas rata-rata + standar deviasi
- **Normal**: Penyewaan dalam rentang rata-rata
- **Low**: Penyewaan di bawah rata-rata - standar deviasi
""")

# Statistik umum
st.write("## 📊 Summary Statistics")
st.write(dayFiltered.describe())

# bar chart total penyewaan sepeda berdasarkan filter cuaca yang dipilih (default, semua cuaca terlihat)
st.subheader("Bike rentals by weather condition")
weatherTotal = day_df.groupby("weather_situation")[["casual_rentals", "registered_rentals"]].sum()
st.bar_chart(weatherTotal)

# data display, statistik deskriptif
st.subheader(":bar_chart: Filtered Data")
st.dataframe(dayFiltered.style.set_properties(**{'background-color': '#f9f9f9', 'color': 'black'}))

# tambahan info mengenai data
st.subheader(":pushpin: Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Rentals", dayFiltered["total_rentals"].sum())
col2.metric("Avg Rentals per Day", round(dayFiltered["total_rentals"].mean(), 2))
col3.metric("Max Rentals in a Day", dayFiltered["total_rentals"].max())

# Download data jika ingin
st.subheader(" Download filtered data")
st.download_button(
    label="Download as CSV",
    data=dayFiltered.to_csv().encode('utf-8'),
    file_name='bike sharing data recap.csv',
    mime='text/csv',
)

# copyright hehe
st.write("\u00A9 2025 Dicoding Indonesia. All Rights Reserved.")