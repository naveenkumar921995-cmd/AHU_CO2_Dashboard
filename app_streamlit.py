# app_streamlit.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

THRESHOLD = 1000

st.set_page_config(page_title="AHU CO₂ Monitoring Dashboard", layout="wide")

st.title("🏢 AHU CO₂ Monitoring Dashboard")
st.subheader(f"CO₂ Threshold: **{THRESHOLD} ppm**")

uploaded_file = st.file_uploader("Upload CO₂ Excel File (.xlsx)", type="xlsx")

if uploaded_file is not None:
    # Load data
    df = pd.read_excel(uploaded_file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour

    # Convert wide → long
    df_long = df.melt(
        id_vars=['Timestamp', 'Hour'],
        var_name='AHU',
        value_name='CO2_ppm'
    ).dropna()

    # Filter exceedance
    exceed = df_long[df_long['CO2_ppm'] > THRESHOLD]

    # ===== SUMMARY TABLE =====
    summary = (
        exceed.groupby('AHU')
        .agg(
            Max_CO2=('CO2_ppm', 'max'),
            Avg_CO2=('CO2_ppm', 'mean'),
            Exceed_Count=('CO2_ppm', 'count')
        )
        .reset_index()
    )

    st.markdown("### 📊 Management Summary")
    st.dataframe(summary)

    st.markdown("### 🚨 CO₂ Exceedance Details")
    st.dataframe(exceed)

    # ===== GRAPH 1: LINE TREND =====
    st.markdown("### 📈 CO₂ Trend")
    plt.figure(figsize=(12,5))
    sns.lineplot(data=df_long, x='Timestamp', y='CO2_ppm', hue='AHU', legend=False)
    plt.axhline(THRESHOLD, color='red', linestyle='--')
    plt.title("CO₂ Trend – All AHUs")
    plt.ylabel("CO₂ (ppm)")
    st.pyplot(plt.gcf())
    plt.close()

    # ===== GRAPH 2: BAR – EXCEEDANCE COUNT =====
    st.markdown("### 📊 Exceedance Count by AHU")
    bar_data = exceed.groupby('AHU').size().reset_index(name='Count')
    plt.figure(figsize=(10,5))
    sns.barplot(data=bar_data, x='AHU', y='Count')
    plt.xticks(rotation=90)
    plt.title("CO₂ Exceedance Count (>1000 ppm)")
    st.pyplot(plt.gcf())
    plt.close()

    # ===== GRAPH 3: BOX PLOT =====
    st.markdown("### 📦 CO₂ Distribution (Box Plot)")
    plt.figure(figsize=(12,5))
    sns.boxplot(data=df_long, x='AHU', y='CO2_ppm')
    plt.axhline(THRESHOLD, color='red', linestyle='--')
    plt.xticks(rotation=90)
    plt.title("CO₂ Distribution by AHU")
    st.pyplot(plt.gcf())
    plt.close()

    # ===== GRAPH 4: HEATMAP (Hour vs AHU) =====
    st.markdown("### 🕒 Hourly CO₂ Heatmap")
    heatmap_data = df_long.pivot_table(
        index='Hour',
        columns='AHU',
        values='CO2_ppm',
        aggfunc='mean'
    )
    plt.figure(figsize=(14,6))
    sns.heatmap(heatmap_data, cmap='coolwarm')
    plt.title("Average CO₂ Heatmap (Hour vs AHU)")
    st.pyplot(plt.gcf())
    plt.close()
