import html
import json
import os
import time
import warnings
from io import BytesIO

import pandas as pd
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except ModuleNotFoundError:
    st_autorefresh = None


if st_autorefresh:
    st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="Holdings", layout="wide")

DEFAULT_FILE = "Stocks_Holdings_Statement_14-02-2026.xlsx"

warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet",
)


def render_html(markup):
    if hasattr(st, "html"):
        st.html(markup)
    else:
        st.markdown(markup, unsafe_allow_html=True)


@st.cache_data
def load_portfolio(file, file_bytes=None):
    excel_source = BytesIO(file_bytes) if file_bytes is not None else file
    df_raw = pd.read_excel(excel_source, sheet_name=0)
    df = df_raw.iloc[10:].copy()
    df.columns = df_raw.iloc[9]
    df = df[1:]
    df = df.dropna(subset=["Stock Name"])
    df.reset_index(drop=True, inplace=True)

    numeric_cols = [
        "Quantity",
        "Average buy price",
        "Buy value",
        "Closing price",
        "Closing value",
        "Unrealised P&L",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def get_latest_feed(feed_path):
    if os.path.exists(feed_path):
        with open(feed_path, "r") as f:
            try:
                return json.load(f), os.path.getmtime(feed_path)
            except json.JSONDecodeError:
                return None, None
    return None, None


def format_inr(value, decimals=2):
    if pd.isna(value):
        value = 0

    sign = "-" if value < 0 else ""
    value = abs(float(value))
    formatted = f"{value:.{decimals}f}"
    whole, fraction = formatted.split(".") if "." in formatted else (formatted, "")

    if len(whole) > 3:
        last_three = whole[-3:]
        rest = whole[:-3]
        pairs = []
        while len(rest) > 2:
            pairs.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            pairs.insert(0, rest)
        whole = ",".join(pairs + [last_three])

    if decimals == 0:
        return f"{sign}\u20b9{whole}"
    return f"{sign}\u20b9{whole}.{fraction}"


def money_class(value):
    if pd.isna(value):
        return "muted"
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "muted"


def first_available(row, columns, default=0):
    for column in columns:
        value = row.get(column, default)
        if not pd.isna(value):
            return value
    return default


def css():
    render_html(
        """
        <style>
            .block-container {
                max-width: 1120px;
                padding-top: 1.4rem;
            }

            h1, h2, h3, p {
                letter-spacing: 0;
            }

            .holdings-title {
                color: #7c8190;
                font-size: 22px;
                font-weight: 700;
                margin: 0 0 28px;
            }

            .summary-card {
                border: 1px solid #e6e8ef;
                border-radius: 14px;
                padding: 28px 26px 24px;
                margin-bottom: 30px;
                background: #fff;
            }

            .summary-top {
                display: flex;
                justify-content: space-between;
                gap: 18px;
                align-items: flex-start;
                border-bottom: 1px dashed #dfe2ea;
                padding-bottom: 22px;
                margin-bottom: 18px;
            }

            .metric-label {
                color: #8d93a3;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 8px;
            }

            .metric-main {
                color: #4d5368;
                font-size: 28px;
                font-weight: 800;
                line-height: 1.1;
            }

            .analyse-btn {
                border: 1px solid #e5e7ed;
                border-radius: 10px;
                color: #555b70;
                font-size: 14px;
                font-weight: 700;
                padding: 10px 16px;
                white-space: nowrap;
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 20px;
                align-items: end;
            }

            .summary-item:nth-child(2),
            .summary-item:nth-child(3) {
                text-align: right;
            }

            .metric-value {
                color: #4d5368;
                font-size: 18px;
                font-weight: 800;
                line-height: 1.3;
            }

            .positive {
                color: #00a77b;
            }

            .negative {
                color: #ff4d32;
            }

            .muted {
                color: #798092;
            }

            .holdings-table {
                border: 1px solid #e6e8ef;
                border-radius: 14px;
                overflow: hidden;
                background: #fff;
            }

            .table-header,
            .table-row {
                display: grid;
                grid-template-columns: minmax(220px, 1.35fr) minmax(135px, 0.9fr) minmax(145px, 1fr) minmax(145px, 1fr) minmax(160px, 1fr);
                column-gap: 18px;
                align-items: center;
            }

            .table-header {
                min-height: 70px;
                padding: 0 26px;
                background: #fafafa;
                border-bottom: 1px solid #e9ebf1;
                color: #747b8c;
                font-size: 14px;
                font-weight: 800;
            }

            .table-row {
                min-height: 98px;
                padding: 0 30px;
                border-bottom: 1px solid #eceef4;
            }

            .table-row:last-child {
                border-bottom: none;
            }

            .cell-right {
                text-align: right;
            }

            .stock-name,
            .primary-value {
                color: #4d5368;
                font-size: 16px;
                font-weight: 600;
                line-height: 1.3;
            }

            .sub-value {
                color: #808698;
                font-size: 14px;
                font-weight: 500;
                margin-top: 10px;
                line-height: 1.2;
            }

            .sub-value.positive,
            .sub-value.negative {
                font-weight: 700;
            }

            @media (max-width: 760px) {
                .summary-top {
                    flex-direction: column;
                }

                .summary-grid,
                .table-header,
                .table-row {
                    grid-template-columns: 1fr;
                }

                .summary-item,
                .summary-item:nth-child(2),
                .summary-item:nth-child(3),
                .cell-right {
                    text-align: left;
                }

                .table-header {
                    display: none;
                }

                .table-row {
                    gap: 14px;
                    padding: 20px 22px;
                }
            }
        </style>
        """
    )


css()

uploaded_file = st.sidebar.file_uploader("Upload Portfolio", type=["xlsx"])
analyse_clicked = st.sidebar.button("Analyse latest data", type="primary", use_container_width=True)

if analyse_clicked:
    load_portfolio.clear()
    st.rerun()

portfolio_df = (
    load_portfolio(uploaded_file.name, uploaded_file.getvalue())
    if uploaded_file
    else load_portfolio(DEFAULT_FILE)
)
portfolio_source = uploaded_file.name if uploaded_file else DEFAULT_FILE
st.sidebar.caption(f"Portfolio: {portfolio_source}")
st.sidebar.caption(f"Loaded holdings: {len(portfolio_df)}")

with open("instrument_map.json", "r") as f:
    instrument_names = json.load(f)

feed_path = os.path.join(os.path.dirname(__file__), "latest_feed.json")
feed, last_modified = get_latest_feed(feed_path)

if not feed:
    st.warning("Waiting for live feed...")
    st.stop()

feeds = feed.get("feeds", {})
market_data = {}

for symbol, data in feeds.items():
    try:
        instrument_key = symbol.split("|")[1]
        name = instrument_names.get(instrument_key, instrument_key)

        market_ff = data["fullFeed"]["marketFF"]
        ltpc = market_ff["ltpc"]
        ltp = ltpc["ltp"]
        prev_close = ltpc.get("cp")

        ohlc_list = market_ff.get("marketOHLC", {}).get("ohlc", [])
        for entry in ohlc_list:
            if prev_close is None and entry.get("interval") == "1d":
                prev_close = entry.get("close")
                break

        if prev_close is None and ohlc_list:
            prev_close = ohlc_list[0].get("close")

        market_data[name] = {"ltp": ltp, "prev_close": prev_close}
    except (KeyError, IndexError, TypeError):
        continue

rows = []
for _, row in portfolio_df.iterrows():
    stock_name = row["Stock Name"]
    qty = row["Quantity"]

    if pd.isna(qty):
        continue

    live_quote = market_data.get(stock_name)
    has_live = bool(live_quote and live_quote.get("ltp") is not None)
    ltp = live_quote["ltp"] if has_live else None
    prev_close = live_quote.get("prev_close") if has_live else None

    invested = row.get("Buy value", 0)
    avg_price = row.get("Average buy price", 0)
    uploaded_current_value = first_available(row, ["Closing value", "Buy value"], 0)
    uploaded_total_return = first_available(row, ["Unrealised P&L"], uploaded_current_value - invested)

    current_value = qty * ltp if has_live else uploaded_current_value
    total_return = current_value - invested if has_live else uploaded_total_return
    total_return_pct = (total_return / invested) * 100 if invested else 0

    day_price_change = ltp - prev_close if has_live and prev_close else None
    day_pct = (day_price_change / prev_close) * 100 if day_price_change is not None and prev_close else None
    day_pl = qty * day_price_change if day_price_change is not None else None

    rows.append(
        {
            "Stock": stock_name,
            "Qty": qty,
            "Avg Price": avg_price,
            "Invested": invested,
            "LTP": ltp,
            "Prev Close": prev_close,
            "Current Value": current_value,
            "Day Price Change": day_price_change,
            "Day P/L": day_pl,
            "Day P/L %": day_pct,
            "Total Return": total_return,
            "Total Return %": total_return_pct,
            "Has Live": has_live,
        }
    )

result_df = pd.DataFrame(rows)

if result_df.empty:
    st.warning("No valid holdings found in the uploaded portfolio.")
    st.stop()

result_df = result_df.sort_values("Stock")

total_current_value = result_df["Current Value"].sum()
total_invested = result_df["Invested"].sum()
live_result_df = result_df[result_df["Has Live"]]
missing_live_df = result_df[~result_df["Has Live"]]
total_day_pl = live_result_df["Day P/L"].sum()
total_prev_value = live_result_df["Qty"].mul(live_result_df["Prev Close"].fillna(live_result_df["LTP"])).sum()
total_day_pct = (total_day_pl / total_prev_value) * 100 if total_prev_value else 0
total_returns = total_current_value - total_invested
total_returns_pct = (total_returns / total_invested) * 100 if total_invested else 0

last_updated = ""
if last_modified:
    last_updated = time.strftime("%d %b %Y, %I:%M:%S %p", time.localtime(last_modified))

title_col, analyse_col = st.columns([0.82, 0.18], vertical_alignment="center")
with title_col:
    render_html(f"<div class='holdings-title'>Holdings ({len(result_df)})</div>")
with analyse_col:
    if st.button("Analyse", use_container_width=True):
        load_portfolio.clear()
        st.rerun()

st.caption(
    f"Showing {len(result_df)} holdings from {portfolio_source}. "
    f"Live prices available for {len(live_result_df)} holdings; "
    f"{len(missing_live_df)} holdings are not present in latest_feed.json."
)

if not missing_live_df.empty:
    missing_names = ", ".join(missing_live_df["Stock"].head(8).astype(str))
    suffix = "..." if len(missing_live_df) > 8 else ""
    st.info(f"Missing live feed for: {missing_names}{suffix}")

render_html(
    f"""
    <section class="summary-card">
        <div class="summary-top">
            <div>
                <div class="metric-label">Current value</div>
                <div class="metric-main">{format_inr(total_current_value, 0)}</div>
            </div>
        </div>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="metric-label">Invested value</div>
                <div class="metric-value">{format_inr(total_invested, 0)}</div>
            </div>
            <div class="summary-item">
                <div class="metric-label">Today's P/L</div>
                <div class="metric-value {money_class(total_day_pl)}">
                    {format_inr(total_day_pl)} ({total_day_pct:.2f}%)
                </div>
            </div>
            <div class="summary-item">
                <div class="metric-label">Total returns</div>
                <div class="metric-value {money_class(total_returns)}">
                    {format_inr(total_returns)} ({total_returns_pct:.2f}%)
                </div>
            </div>
        </div>
    </section>
    """
)

if last_updated:
    st.caption(f"Last updated: {last_updated}")

sort_options = {
    "Company": "Stock",
    "Market price": "LTP",
    "Today's P/L": "Day P/L",
    "Total returns": "Total Return",
    "Current (Invested)": "Current Value",
}

if "sort_label" not in st.session_state:
    st.session_state.sort_label = "Company"
if "sort_order" not in st.session_state:
    st.session_state.sort_order = "Ascending"

search_text = st.text_input("Search company", placeholder="Search holdings...")

sort_cols = st.columns([1.35, 0.9, 1, 1, 1], vertical_alignment="top")
for index, label in enumerate(sort_options):
    with sort_cols[index]:
        label_col, asc_col, desc_col = st.columns([0.62, 0.19, 0.19], vertical_alignment="center")
        label_col.caption(label)
        if asc_col.button("\u2191", key=f"sort_{index}_asc", help=f"Sort {label} ascending"):
            st.session_state.sort_label = label
            st.session_state.sort_order = "Ascending"
            st.rerun()
        if desc_col.button("\u2193", key=f"sort_{index}_desc", help=f"Sort {label} descending"):
            st.session_state.sort_label = label
            st.session_state.sort_order = "Descending"
            st.rerun()

table_df = result_df.copy()
if search_text:
    table_df = table_df[
        table_df["Stock"].astype(str).str.contains(search_text.strip(), case=False, na=False)
    ]

sort_label = st.session_state.sort_label
sort_order = st.session_state.sort_order
sort_column = sort_options[sort_label]
table_df = table_df.sort_values(
    sort_column,
    ascending=sort_order == "Ascending",
    na_position="last",
    kind="mergesort",
)

sort_arrow = "\u2191" if sort_order == "Ascending" else "\u2193"
headers = {
    label: f"{label} {sort_arrow}" if label == sort_label else label
    for label in sort_options
}

if search_text:
    st.caption(f"Displaying {len(table_df)} matching holdings.")

table_rows = []
for _, row in table_df.iterrows():
    stock = html.escape(str(row["Stock"]))
    qty = int(row["Qty"]) if float(row["Qty"]).is_integer() else row["Qty"]
    day_change = row["Day Price Change"]
    day_pl = row["Day P/L"]
    day_pct = row["Day P/L %"]
    total_return = row["Total Return"]
    total_return_pct = row["Total Return %"]
    has_live = row["Has Live"]
    ltp_text = format_inr(row["LTP"]) if has_live else "N/A"
    day_change_text = (
        f'{format_inr(day_change)} / share ({day_pct:.2f}%)'
        if has_live and not pd.isna(day_change) and not pd.isna(day_pct)
        else "Live feed unavailable"
    )
    day_pl_text = format_inr(day_pl) if has_live and not pd.isna(day_pl) else "N/A"
    day_pl_subtext = f"{qty} x {format_inr(day_change)}" if has_live and not pd.isna(day_change) else "Update latest_feed.json"

    table_rows.append(
        f"""
        <div class="table-row">
            <div>
                <div class="stock-name">{stock}</div>
                <div class="sub-value">{qty} shares &bull; Avg. {format_inr(row["Avg Price"])}</div>
            </div>
            <div class="cell-right">
                <div class="primary-value">{ltp_text}</div>
                <div class="sub-value {money_class(day_change)}">
                    {day_change_text}
                </div>
            </div>
            <div class="cell-right">
                <div class="primary-value {money_class(day_pl)}">{day_pl_text}</div>
                <div class="sub-value {money_class(day_pl)}">
                    {day_pl_subtext}
                </div>
            </div>
            <div class="cell-right">
                <div class="primary-value {money_class(total_return)}">{format_inr(total_return)}</div>
                <div class="sub-value {money_class(total_return_pct)}">{total_return_pct:.2f}%</div>
            </div>
            <div class="cell-right">
                <div class="primary-value">{format_inr(row["Current Value"])}</div>
                <div class="sub-value">{format_inr(row["Invested"])}</div>
            </div>
        </div>
        """
    )

if table_rows:
    render_html(
        f"""
        <section class="holdings-table">
            <div class="table-header">
                <div>{headers["Company"]}</div>
                <div class="cell-right">{headers["Market price"]}</div>
                <div class="cell-right">{headers["Today's P/L"]}</div>
                <div class="cell-right">{headers["Total returns"]}</div>
                <div class="cell-right">{headers["Current (Invested)"]}</div>
            </div>
            {''.join(table_rows)}
        </section>
        """
    )
else:
    st.info("No holdings match your search.")
