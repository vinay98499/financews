# FinanceWS

A personal finance and stock analytics workspace with Upstox API integration, Streamlit dashboards, and real-time market data tools.

## Features
- Portfolio analysis and visualization (Streamlit)
- Real-time market data feed via Upstox WebSocket
- Margin and funds API integration
- Secure API key management with `.env`
- Modular Python scripts for login, portfolio, and forecasting
- ARIMA-based ML forecasting for stock returns

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/vinay98499/financews.git
   cd financews
   ```
2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # Or
   source venv/bin/activate  # On Linux/Mac
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up your `.env` file:**
   - Copy `.env.example` to `.env` (or create `.env`)
   - Add your Upstox API access token:
     ```
     UPSTOX_ACCESS_TOKEN=your_access_token_here
     ```

## Usage
- **Streamlit Dashboard:**
  ```sh
  streamlit run finance2.py
  ```
- **Market Data Feed:**
  ```sh
  python marketfeed.py
  ```
- **Margin API Example:**
  ```sh
  python margin.py
  ```

## File Structure
- `finance2.py` — Main Streamlit dashboard for portfolio analytics
- `marketfeed.py` — Real-time market data via Upstox WebSocket
- `margin.py` — Example for margin/funds API
- `login`, `upstoxlogin.py` — Login and authentication helpers
- `mlforecast.py` — ML/ARIMA forecasting utilities
- `.env` — Store your API keys (never commit this file)
- `.gitignore` — Ignores venv, .env, and other sensitive files

## Notes
- Ensure your `.env` file is present and contains a valid Upstox access token.
- The Excel file `Stocks_Holdings_Statement_28-06-2025.xlsx` is used as a sample portfolio.
- For ARIMA forecasting, map your stock names to Yahoo tickers in `finance2.py`.

## License
MIT

from dotenv import load_dotenv
load_dotenv()
