import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='darkgrid')

def get_total_count_by_hour_df(hour_df):
    hour_count_df = hour_df.groupby(by="hr").agg(cnt=("cnt", "sum")).reset_index()
    hour_count_df.rename(columns={"hr": "hours"}, inplace=True)
    return hour_count_df

def count_by_day_df(day_df):
    daily_count = day_df.groupby(by="dteday").agg(total_rentals_on_day=("cnt", "sum")).reset_index()
    return daily_count

def load_and_preprocess_data(data_folder, day_file, hour_file):
    try:
        days_df = pd.read_csv(data_folder + day_file)
        hours_df = pd.read_csv(data_folder + hour_file)
    except FileNotFoundError:
        st.error(f"Pastikan file '{day_file}' dan '{hour_file}' ada di folder '{data_folder}'.")
        st.stop()
    days_df["dteday"] = pd.to_datetime(days_df["dteday"])
    hours_df["dteday"] = pd.to_datetime(hours_df["dteday"])
    days_df.sort_values(by="dteday", inplace=True)
    days_df.reset_index(drop=True, inplace=True)
    hours_df.sort_values(by="dteday", inplace=True)
    hours_df.reset_index(drop=True, inplace=True)
    return days_df, hours_df

def setup_sidebar():
    with st.sidebar:
        st.title("Bike Sharing")
        st.image("https://upload.wikimedia.org/wikipedia/commons/8/82/Melbourne_City_Bikes.JPG", use_column_width=True)


def display_daily_analysis(filtered_days_df, start_date, end_date):
    st.header('Analisis Penyewaan Harian')
    daily_rentals_filtered = count_by_day_df(filtered_days_df)
    
    if daily_rentals_filtered.empty:
        st.info("Tidak ada data harian untuk rentang tanggal yang dipilih.")
        return

    top_day_filtered = daily_rentals_filtered.sort_values(by="total_rentals_on_day", ascending=False).iloc[0]
    least_day_filtered = daily_rentals_filtered.sort_values(by="total_rentals_on_day", ascending=True).iloc[0]
    
    st.markdown(f"**Rentang Tanggal:** {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")
    st.markdown(f"**Tanggal Terbanyak:** **{top_day_filtered['dteday'].strftime('%A, %d %B %Y')}** ({top_day_filtered['total_rentals_on_day']} penyewaan).")
    st.markdown(f"**Tanggal Tersedikit:** **{least_day_filtered['dteday'].strftime('%A, %d %B %Y')}** ({least_day_filtered['total_rentals_on_day']} penyewaan).")
    
    fig_day, ax_day = plt.subplots(figsize=(12, 6))
    top_10_days_filtered = daily_rentals_filtered.sort_values(by="total_rentals_on_day", ascending=False).head(10)
    sns.barplot(x="dteday", y="total_rentals_on_day", data=top_10_days_filtered, palette="viridis", ax=ax_day)
    ax_day.set_title(f"10 Tanggal dengan Penyewaan Terbanyak", fontsize=18)
    ax_day.set_xlabel("Tanggal", fontsize=14)
    ax_day.set_ylabel("Jumlah Penyewaan", fontsize=14)
    ax_day.tick_params(axis='x', rotation=45, labelsize=10)
    plt.tight_layout()
    st.pyplot(fig_day)
    st.markdown("---")

def display_hourly_analysis(filtered_hours_df, start_date, end_date):
    st.header('Analisis Penyewaan per Jam')
    hourly_rentals_filtered = get_total_count_by_hour_df(filtered_hours_df)
    
    if hourly_rentals_filtered.empty:
        st.info("Tidak ada data per jam untuk rentang tanggal yang dipilih.")
        return

    top_hour_filtered = hourly_rentals_filtered.sort_values(by="cnt", ascending=False).iloc[0]
    least_hour_filtered = hourly_rentals_filtered.sort_values(by="cnt", ascending=True).iloc[0]
    
    st.markdown(f"**Rentang Tanggal:** {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")
    st.markdown(f"**Jam Terbanyak:** Jam **{top_hour_filtered['hours']}** ({top_hour_filtered['cnt']} penyewaan).")
    st.markdown(f"**Jam Tersedikit:** Jam **{least_hour_filtered['hours']}** ({least_hour_filtered['cnt']} penyewaan).")
    
    fig_hour, ax_hour = plt.subplots(figsize=(10, 6))
    sns.barplot(x="hours", y="cnt", data=hourly_rentals_filtered, palette="magma", ax=ax_hour)
    ax_hour.set_title(f"Total Penyewaan per Jam", fontsize=18)
    ax_hour.set_xlabel("Jam", fontsize=14)
    ax_hour.set_ylabel("Jumlah Penyewaan", fontsize=14)
    ax_hour.set_xticks(range(0, 24))
    plt.tight_layout()
    st.pyplot(fig_hour)

def main():
    st.set_page_config(layout="wide")
    
    data_folder = "BikeSharingProject\Dashboard/"
    day_file = "day.csv"
    hour_file = "hour.csv"
    days_df, hours_df = load_and_preprocess_data(data_folder, day_file, hour_file)
    
    min_date_full_data = days_df["dteday"].min()
    max_date_full_data = days_df["dteday"].max()
    
    setup_sidebar() 

    st.title('Dashboard')

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            label='Tanggal Mulai',
            min_value=min_date_full_data,
            max_value=max_date_full_data,
            value=min_date_full_data
        )
    with col2:
        end_date = st.date_input(
            label='Tanggal Akhir',
            min_value=min_date_full_data,
            max_value=max_date_full_data,
            value=max_date_full_data
        )

    filtered_days_df = days_df[(days_df["dteday"] >= pd.to_datetime(start_date)) & (days_df["dteday"] <= pd.to_datetime(end_date))]
    filtered_hours_df = hours_df[(hours_df["dteday"] >= pd.to_datetime(start_date)) & (hours_df["dteday"] <= pd.to_datetime(end_date))]
    
    display_daily_analysis(filtered_days_df, start_date, end_date)
    display_hourly_analysis(filtered_hours_df, start_date, end_date)
    
    st.caption('Dibuat Oleh RD MUHAMAD ERFAN SALAHUDIN')

if __name__ == "__main__":
    main()