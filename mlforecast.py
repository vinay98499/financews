# mlforecast.py

import streamlit as st
import pandas as pd
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt


# You can move this to a config file or fetch dynamically
SYMBOL_LOOKUP = {
    "ADANI ENTERPRISES LIMITED": "ADANIENT.NS",
    "ADANI POWER LTD": "ADANIPOWER.NS",
    "AXIS BANK LIMITED": "AXISBANK.NS",
    "ADANI PORT & SEZ LTD": "ADANIPORTS.NS"
    # Add more mappings as needed

}


def run_forecast(stock_name: str):
    if stock_name not in SYMBOL_LOOKUP:
        st.warning("⚠️ Ticker not mapped yet for this stock. Please update SYMBOL_LOOKUP.")
        return

    symbol = SYMBOL_LOOKUP[stock_name]

    st.info(f"Fetching historical prices for **{symbol}**...")

    hist = yf.download(symbol, period="3y", interval="1d")["Close"].dropna()

    if len(hist) < 200:
        st.warning("Not enough data for modeling.")
        return

    model = ARIMA(hist, order=(5, 1, 0)).fit()
    steps = 120  # ~6 months

    fc = model.get_forecast(steps=steps)
    fc_index = pd.date_range(
        start=hist.index[-1] + pd.Timedelta(days=1),
        periods=steps, freq="B"
    )
    fc_series = pd.Series(fc.predicted_mean, index=fc_index)

    full_series = pd.concat([hist, fc_series])

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 4))
    hist.plot(ax=ax, label="Historical")
    fc_series.plot(ax=ax, label="Forecast")
    ax.set_title(f"{stock_name} – Price Forecast (ARIMA)")
    ax.set_ylabel("Price (₹)")
    ax.legend()
    st.pyplot(fig)

    # Show return metric
    last_price = float(hist.iloc[-1])
    fc_price = float(fc_series.iloc[-1])
    ret_pct = float((fc_price - last_price) / last_price * 100)



    st.metric(
        label="📊 6-Month Forecasted Return",
        value=f"{ret_pct:.2f}%",
        delta=f"{fc_price:,.2f} ₹"
    )
