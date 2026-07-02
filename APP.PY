import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from openbb import obb

# Page Config
st.set_page_config(page_title="Pro Financial Automation Dashboard", layout="wide")
st.title("📊 Financial Analytics & Automation Dashboard")
st.markdown("Powered by OpenBB Platform Core Resources")

# Sidebar Configuration for Data Ingestion
st.sidebar.header("Data Parameters")
ticker = st.sidebar.text_input("Ticker Symbol", value="TATASTEEL").upper()
provider = st.sidebar.selectbox("Data Provider", ["yfinance", "fmp", "polygon"], index=0)

# 1. Fetch Core Market Data using OpenBB Engine
@st.cache_data(ttl=300) # Cache for 5 minutes to optimize performance
def load_market_data(symbol, data_provider):
    try:
        # Utilizing standard OpenBB data routing
        res = obb.equity.price.historical(symbol=symbol, provider=data_provider)
        df = res.to_df()
        return df
    except Exception as e:
        st.error(f"Error fetching data via OpenBB: {e}")
        return pd.DataFrame()

df_data = load_market_data(ticker, provider)

if not df_data.empty:
    # Structure data cleanly
    if 'close' not in df_data.columns and 'Close' in df_data.columns:
        df_data.rename(columns={'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume'}, inplace=True)

    # Layout Zones
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Price Action: {ticker}")
        # Build interactive Candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df_data.index,
            open=df_data['open'],
            high=df_data['high'],
            low=df_data['low'],
            close=df_data['close'],
            name=ticker
        )])
        fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Key Metrics Summary")
        latest_close = df_data['close'].iloc[-1]
        prev_close = df_data['close'].iloc[-2]
        delta = ((latest_close - prev_close) / prev_close) * 100
        
        st.metric(label="Latest Closing Price", value=f"₹ {latest_close:,.2f}", delta=f"{delta:.2f}%")
        st.write("### Recent Data Records", df_data.tail(5))

    # 2. Advanced Technical Analysis Module (Leveraging OpenBB Extensions)
    st.markdown("---")
    st.subheader("⚙️ Automated Technical Signal Scan")
    
    # Simple Technical Analysis Overlay Logic
    df_data['SMA_20'] = df_data['close'].rolling(window=20).mean()
    df_data['SMA_50'] = df_data['close'].rolling(window=50).mean()
    
    st.write("#### Moving Average Convergence Status")
    col_sma1, col_sma2 = st.columns(2)
    col_sma1.metric("20-Day SMA", f"{df_data['SMA_20'].iloc[-1]:.2f}")
    col_sma2.metric("50-Day SMA", f"{df_data['SMA_50'].iloc[-1]:.2f}")
    
else:
    st.info("Please verify the ticker symbol or try changing the data provider in the sidebar.")
