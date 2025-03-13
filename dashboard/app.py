import pandas as pd
import os
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# ================== SETUP CONFIGURATION ==================
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# Menentukan path dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ambil direktori file saat ini
DATA_PATH = os.path.join(BASE_DIR, "main_dataset.csv")

# ================== LOAD DATA ==================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    
    # Konversi ke datetime
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")

    # Hitung waktu pengiriman dalam hari (shipping_time)
    df["shipping_time"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
    
    # Fitur tambahan
    df["order_hour"] = df["order_purchase_timestamp"].dt.hour  # Jam pesanan
    df["year_month"] = df["order_purchase_timestamp"].dt.to_period("M")  # Format YYYY-MM

    return df

df = load_data()

# ================== SIDEBAR INTERACTIVE FEATURES ==================
st.sidebar.title("⚙️ Interactive Features")

st.sidebar.markdown("""
- **📅 Date Selection**  
- **📦 Product Category Filter**  
- **💳 Payment Method Filter**  
- **💰 Price Range**   
""")

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("🔍 Data Filters")

# Filter Tanggal
start_date = st.sidebar.date_input("📅 Select Start Date", df["order_purchase_timestamp"].min().date())
end_date = st.sidebar.date_input("📅 Select End Date", df["order_purchase_timestamp"].max().date())

# Filter Kategori Produk
categories = df["product_category_name"].dropna().unique()
selected_category = st.sidebar.multiselect("📦 Select Product Category", categories, default=categories[:5])

# Filter Metode Pembayaran
payment_methods = df["payment_type"].dropna().unique()
selected_payment = st.sidebar.multiselect("💳 Select Payment Method", payment_methods, default=payment_methods)

# Filter Rentang Harga
min_price, max_price = st.sidebar.slider("💰 Purchase Price Range (IDR)", 
                                         float(df["payment_value"].min()), 
                                         float(df["payment_value"].max()), 
                                         (float(df["payment_value"].min()), float(df["payment_value"].max())))

# Terapkan filter
filtered_df = df[(df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                 (df["order_purchase_timestamp"] <= pd.to_datetime(end_date)) & 
                 (df["product_category_name"].isin(selected_category)) &
                 (df["payment_type"].isin(selected_payment)) &
                 (df["payment_value"].between(min_price, max_price))]

st.sidebar.markdown("<br><br><br><br><br><p style='font-size: 10px; text-align: center;'>Dashboard Created by Suartana12 ❤️</p>", unsafe_allow_html=True)

# ================== DASHBOARD TITLE ==================
st.title("📊 E-Commerce Dashboard")
st.write("### Product Category Analysis, Revenue Patterns, and Shipping Time")

# ================== TABS ==================
tab1, tab2, tab3, tab4 = st.tabs(["📦 Product Category", "📈 Revenue Analysis", "⏳ Order Time Distribution", "🚚 Shipping Time"])

# 📌 TAB 1: Kategori Produk Terlaris
with tab1:
    st.write("### 🔹 The 10 Most Purchased Product Categories")
    top_categories = (
        filtered_df["product_category_name"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_categories.columns = ["Product Category", "Purchase Quantity"]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        x="Purchase Quantity",
        y="Product Category",
        data=top_categories,
        palette="viridis",
        ax=ax
    )
    plt.xlabel("Purchase Quantity")
    plt.ylabel("Product Category")
    plt.title("The 10 Most Purchased Product Categories")
    st.pyplot(fig)

# 📌 TAB 2: Pola Pendapatan Bulanan
with tab2:
    st.write("### 🔹 Monthly Income Patterns in 2018")
    monthly_revenue = filtered_df[filtered_df["order_purchase_timestamp"].dt.year == 2018].groupby("year_month")["payment_value"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(x=monthly_revenue["year_month"].astype(str), y=monthly_revenue["payment_value"], marker="o", ax=ax)
    plt.xticks(rotation=45)
    plt.xlabel("Month (2018)")
    plt.ylabel("Total Revenue (IDR)")
    plt.title("Monthly Revenue Trends (January - December 2018)")
    st.pyplot(fig)

# 📌 TAB 3: Distribusi Waktu Pesanan
with tab3:
    st.write("### 🔹 Distribution of Ordering Time in a Day")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(filtered_df["order_hour"], bins=24, kde=True, color="blue", ax=ax)
    plt.xlabel("Order Time")
    plt.ylabel("Order Quantity")
    plt.xticks(range(0, 24))
    plt.title("Distribution of Ordering Time in a Day")
    st.pyplot(fig)

# 📌 TAB 4: Rata-rata Waktu Pengiriman
with tab4:
    st.write("### 🔹 Average Delivery Time by Product Category")
    avg_shipping_time = filtered_df.groupby("product_category_name")["shipping_time"].mean().dropna().sort_values(ascending=True).head(10)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=avg_shipping_time.values, y=avg_shipping_time.index, palette="coolwarm", ax=ax)
    plt.xlabel("Average Delivery Time (days)")
    plt.ylabel("Product Category")
    plt.title("Average Delivery Time per Product Category (Fastest 10)")
    st.pyplot(fig)

# ================== INTERACTIVE SUMMARY ==================
st.write("## 📌 Data Summary")
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = len(filtered_df)
    st.metric(label="📦 Total Orders", value=total_orders)

with col2:
    total_customers = filtered_df["customer_id"].nunique()
    st.metric(label="👥 Unique Customers", value=total_customers)

with col3:
    total_revenue = filtered_df["payment_value"].sum()
    st.metric(label="💰 Total Revenue", value=f"IDR {total_revenue:,.0f}")

st.markdown("<br><br><br><p style='font-size: 12px; text-align: center;'>Dashboard Created by Suartana12 ❤️</p>", unsafe_allow_html=True)
