
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page configuration
st.set_page_config(
    page_title="Food Price Monitoring Chad",
    page_icon="🌾",
    layout="wide"
)

# Application title
st.title("🌾 Food Price Monitoring System in Chad")

st.markdown(
    "An interactive platform for monitoring and analyzing "
    "food prices across markets in Chad."
)

# Load dataset
@st.cache_data
def load_data():
    path = os.path.join(
        os.path.dirname(__file__),
        "cleaned_food_prices.csv"
    )

    data = pd.read_csv(path)

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data["price"] = pd.to_numeric(
        data["price"],
        errors="coerce"
    )

    return data.dropna(
        subset=["date", "market", "commodity", "price"]
    )

try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Data Filters")

products = sorted(df["commodity"].dropna().unique())

selected_product = st.sidebar.selectbox(
    "Select a food product",
    products
)

product_df = df[
    (df["commodity"] == selected_product) &
    (df["unit"] == "KG")
].copy()

markets = sorted(product_df["market"].dropna().unique())

selected_market = st.sidebar.selectbox(
    "Select a market",
    ["All Markets"] + markets
)

if selected_market != "All Markets":
    filtered_df = product_df[
        product_df["market"] == selected_market
    ].copy()
else:
    filtered_df = product_df.copy()

if filtered_df.empty:
    st.warning("No data available for this selection.")
    st.stop()

# Main statistics
st.subheader("Price Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total observations",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Average price",
    f"{filtered_df['price'].mean():,.2f} XAF"
)

col3.metric(
    "Minimum price",
    f"{filtered_df['price'].min():,.2f} XAF"
)

col4.metric(
    "Maximum price",
    f"{filtered_df['price'].max():,.2f} XAF"
)

# Monthly price analysis
st.subheader("Monthly Price Evolution")

monthly = (
    filtered_df.set_index("date")
    .resample("ME")["price"]
    .mean()
    .dropna()
    .reset_index()
)

if not monthly.empty:
    fig = px.line(
        monthly,
        x="date",
        y="price",
        title=f"Monthly Average Price of {selected_product}",
        markers=True,
        labels={
            "date": "Date",
            "price": "Average price (XAF/KG)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

# Market comparison
st.subheader("Price Comparison Across Markets")

market_comparison = (
    product_df.groupby("market")["price"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_market = px.bar(
    market_comparison,
    x="market",
    y="price",
    title="Top 10 Markets by Average Price",
    labels={
        "market": "Market",
        "price": "Average price (XAF/KG)"
    }
)

st.plotly_chart(fig_market, use_container_width=True)

# Data table
st.subheader("Food Price Records")

st.dataframe(
    filtered_df.sort_values("date", ascending=False),
    use_container_width=True
)

# Download filtered data
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data (CSV)",
    data=csv,
    file_name="chad_food_prices.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.caption(
    "Food Price Monitoring System in Chad | "
    "Academic Data Science Project"
)
