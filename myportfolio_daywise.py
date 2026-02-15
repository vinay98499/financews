import streamlit as st
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
import numpy as np

# --- Load Default File ---
DEFAULT_FILE = "Stocks_Holdings_Statement_14-02-2026.xlsx"

@st.cache_data
def load_portfolio(file):
    df_raw = pd.read_excel(file, sheet_name=0)
    df = df_raw.iloc[10:].copy()
    df.columns = df_raw.iloc[9]
    df = df[1:]
    df = df.dropna(subset=["Stock Name"])
    df.reset_index(drop=True, inplace=True)

    numeric_cols = [
        "Quantity", "Average buy price", "Buy value",
        "Closing price", "Closing value", "Unrealised P&L"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Optional: mock Sector if not present
    if "Sector" not in df.columns:
        import random
        sectors = ["Finance", "Energy", "IT", "Consumer", "Infra"]
        df["Sector"] = [random.choice(sectors) for _ in range(len(df))]

    return df

# --- UI ---
st.set_page_config(page_title="AI Financial Advisor", layout="wide")
st.title("📊 Personal AI Financial Advisor")

# File uploader
st.sidebar.header("📤 Upload a different portfolio")
uploaded_file = st.sidebar.file_uploader("Choose Excel file", type=["xlsx"])

# Load data
df = load_portfolio(uploaded_file) if uploaded_file else load_portfolio(DEFAULT_FILE)
st.caption("📂 Showing: " + ("Uploaded Portfolio" if uploaded_file else "Default Portfolio (Person X)"))

# --- Display Data ---
st.subheader("💼 Portfolio Overview")
st.dataframe(df, use_container_width=True)

# --- Metrics ---
total_invested = df["Buy value"].sum()
total_value = df["Closing value"].sum()
total_pnl = df["Unrealised P&L"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📥 Total Invested", f"₹{total_invested:,.2f}")
col2.metric("📈 Current Value", f"₹{total_value:,.2f}")
col3.metric("💰 Unrealised P&L", f"₹{total_pnl:,.2f}", delta=f"{(total_pnl/total_invested)*100:.2f}%")

# --- Pie Chart: Stock Allocation ---
st.subheader("📌 Allocation by Stock")
st.plotly_chart({
    "data": [{
        "type": "pie",
        "labels": df["Stock Name"],
        "values": df["Closing value"],
        "hole": 0.4
    }],
    "layout": {"title": "Portfolio Allocation"}
})

# --- Pie Chart: Sector Allocation ---
if "Sector" in df.columns:
    st.subheader("🗂️ Allocation by Sector")
    sector_data = df.groupby("Sector")["Closing value"].sum().reset_index()
    st.plotly_chart({
        "data": [{
            "type": "pie",
            "labels": sector_data["Sector"],
            "values": sector_data["Closing value"],
            "hole": 0.4
        }],
        "layout": {"title": "Sector-Wise Allocation"}
    })

# --- Bar Chart: P&L per Stock ---
st.subheader("📊 Stock-wise Unrealised P&L")
st.bar_chart(df.set_index("Stock Name")["Unrealised P&L"])

# --- Big Gainers / Losers ---
st.subheader("📈 Top Gainers & 📉 Top Losers")

gain_df = df.sort_values(by="Unrealised P&L", ascending=False)
top_gainers = gain_df.head(3)
top_losers = gain_df.tail(3).sort_values(by="Unrealised P&L")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🚀 Top Gainers")
    st.table(top_gainers[["Stock Name", "Unrealised P&L"]])
with col2:
    st.markdown("### 🧨 Top Losers")
    st.table(top_losers[["Stock Name", "Unrealised P&L"]])

# --- ML Return Forecast (ARIMA) ---
with st.expander("📈 ML Return Forecast (ARIMA)"):
    # Show all unique stock names for mapping help
    st.write("**Stocks in your portfolio:**", list(df["Stock Name"].unique()))
    # Example mapping: expand as needed for your stocks
    ticker_map = {
        # Add your mappings here, e.g.:
        "RELIANCE INDUSTRIES LTD": "RELIANCE.NS"
        # "TATA CONSULTANCY SERVICES LTD": "TCS.NS",
        # "INFOSYS LTD": "INFY.NS",
    }
    available_stocks = [name for name in df["Stock Name"].unique() if name in ticker_map]
    if not available_stocks:
        st.info("No stocks in your portfolio have a valid Yahoo ticker mapping. Please update the mapping in the code above. See the list of stock names above and add them to the mapping.")
    else:
        stock_choice = st.selectbox("Choose a stock to forecast", available_stocks)
        ticker = ticker_map.get(stock_choice)
        if st.button("Run Forecast"):
            if ticker:
                try:
                    data = yf.download(ticker, period="2y", interval="1d")
                    st.write("Downloaded data shape:", data.shape)
                    st.write("Downloaded data head:", data.head())
                    # Handle multi-index columns (sometimes happens with yfinance)
                    if isinstance(data.columns, pd.MultiIndex):
                        st.write("MultiIndex columns:", list(data.columns))
                        # Try to find any column with 'Close' in the first level
                        close_candidates = [col for col in data.columns if col[0] == "Close"]
                        if close_candidates:
                            close_prices = data[close_candidates[0]].dropna()
                        else:
                            st.warning("MultiIndex columns found, but no 'Close' price in any subcolumn. Check columns above.")
                            close_prices = pd.Series(dtype=float)
                    else:
                        close_prices = data["Close"].dropna() if "Close" in data.columns else pd.Series(dtype=float)
                    if close_prices.size > 30 and close_prices.ndim == 1:
                        model = ARIMA(close_prices, order=(1,1,1))
                        model_fit = model.fit()
                        forecast = model_fit.forecast(steps=126)  # ~6 months
                        last_price = close_prices.iloc[-1]
                        forecasted_price = forecast.iloc[-1]
                        forecast_return = (forecasted_price - last_price) / last_price * 100
                        st.metric("📊 6-Month Forecasted Return", f"{forecast_return:.2f}%", f"{forecasted_price-last_price:,.2f} ₹")
                        st.line_chart(np.concatenate([close_prices.values, forecast.values]))
                    else:
                        st.warning("No sufficient univariate historical data found for this stock. See the data above for details.")
                except Exception as e:
                    st.error(f"Forecasting failed: {e}")
            else:
                st.warning("No Yahoo ticker mapping found for this stock. Please update the mapping in the code.")
