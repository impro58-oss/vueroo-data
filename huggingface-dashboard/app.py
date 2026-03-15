# Roo Crypto Intelligence Dashboard
# Streamlit app for visualizing TrojanLogic4H scan data

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json

# Page config
st.set_page_config(
    page_title="Roo Crypto Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .signal-long { color: #00cc00; font-weight: bold; }
    .signal-short { color: #ff4444; font-weight: bold; }
    .signal-hold { color: #888888; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Data URLs (GitHub raw)
LATEST_URL = "https://raw.githubusercontent.com/impro58-oss/rooquest1/main/data/crypto/crypto_latest.json"
HISTORY_URL = "https://raw.githubusercontent.com/impro58-oss/rooquest1/main/data/crypto/crypto_history.json"

@st.cache_data(ttl=300)
def load_data():
    """Load data from GitHub."""
    try:
        latest_response = requests.get(LATEST_URL, timeout=10)
        latest_response.encoding = 'utf-8-sig'  # Handle BOM
        latest_data = latest_response.json()
        
        history_response = requests.get(HISTORY_URL, timeout=10)
        history_response.encoding = 'utf-8-sig'  # Handle BOM
        history_data = history_response.json()
        
        return latest_data, history_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def create_signal_chart(df):
    """Create signal distribution chart."""
    signal_counts = df['signal'].value_counts()
    
    colors = {'LONG': '#00cc00', 'SHORT': '#ff4444', 'HOLD': '#888888'}
    fig = px.pie(
        values=signal_counts.values,
        names=signal_counts.index,
        title="Signal Distribution",
        color=signal_counts.index,
        color_discrete_map=colors
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_confidence_chart(df):
    """Create confidence distribution chart."""
    fig = px.histogram(
        df,
        x='confidence',
        nbins=20,
        title="Confidence Distribution",
        labels={'confidence': 'Confidence Score', 'count': 'Number of Signals'},
        color='signal',
        color_discrete_map={'LONG': '#00cc00', 'SHORT': '#ff4444', 'HOLD': '#888888'}
    )
    return fig

def create_top_opportunities(df):
    """Create top opportunities table."""
    # Filter for actionable signals
    opportunities = df[
        (df['signal'].isin(['LONG', 'SHORT'])) & 
        (df['confidence'] >= 0.45)
    ].sort_values('confidence', ascending=False).head(10)
    
    return opportunities[['symbol', 'signal', 'confidence', 'price', 'cs_rsi_red', 'regime']]

def create_trend_chart(history_df, symbol):
    """Create trend chart for specific symbol."""
    symbol_data = history_df[history_df['symbol'] == symbol].sort_values('timestamp')
    
    if len(symbol_data) == 0:
        return None
    
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(
        x=symbol_data['timestamp'],
        y=symbol_data['price'],
        name='Price',
        line=dict(color='blue', width=2),
        yaxis='y'
    ))
    
    # Confidence line
    fig.add_trace(go.Scatter(
        x=symbol_data['timestamp'],
        y=symbol_data['confidence'] * 100,
        name='Confidence %',
        line=dict(color='orange', width=2),
        yaxis='y2'
    ))
    
    # Signal markers
    for signal_type, color in [('LONG', 'green'), ('SHORT', 'red')]:
        signal_data = symbol_data[symbol_data['signal'] == signal_type]
        if len(signal_data) > 0:
            fig.add_trace(go.Scatter(
                x=signal_data['timestamp'],
                y=signal_data['price'],
                mode='markers',
                name=f'{signal_type} Signal',
                marker=dict(color=color, size=10, symbol='diamond')
            ))
    
    fig.update_layout(
        title=f"{symbol} - Price & Signal History",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        yaxis2=dict(
            title="Confidence %",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified'
    )
    
    return fig

# Main app
def main():
    st.markdown('<p class="main-header">📊 Roo Crypto Intelligence Dashboard</p>', unsafe_allow_html=True)
    st.markdown("*Real-time analysis from TrojanLogic4H scans*")
    
    # Load data
    with st.spinner("Loading data from GitHub..."):
        latest_data, history_data = load_data()
    
    if latest_data is None:
        st.error("Failed to load data. Please check the data source.")
        return
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    
    # Last update time
    last_update = latest_data.get('timestamp', 'Unknown')
    st.sidebar.info(f"Last Update: {last_update}")
    
    # Filter by strategy
    strategy_filter = st.sidebar.multiselect(
        "Filter by Strategy",
        ['FUTURES', 'HOLD', 'MONITOR'],
        default=['FUTURES', 'HOLD']
    )
    
    # Convert to DataFrame
    df = pd.DataFrame(latest_data.get('results', []))
    
    if len(df) == 0:
        st.warning("No data available.")
        return
    
    # Apply filters
    if strategy_filter:
        df = df[df['strategy'].isin(strategy_filter)]
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Symbols", len(df))
    with col2:
        long_count = len(df[df['signal'] == 'LONG'])
        st.metric("LONG Signals", long_count, delta=f"{long_count/len(df)*100:.1f}%")
    with col3:
        short_count = len(df[df['signal'] == 'SHORT'])
        st.metric("SHORT Signals", short_count, delta=f"{short_count/len(df)*100:.1f}%")
    with col4:
        high_conf = len(df[df['confidence'] >= 0.65])
        st.metric("High Confidence", high_conf)
    
    # Charts row
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Signal Distribution")
        fig_signals = create_signal_chart(df)
        st.plotly_chart(fig_signals, use_container_width=True)
    
    with col2:
        st.subheader("Confidence Distribution")
        fig_conf = create_confidence_chart(df)
        st.plotly_chart(fig_conf, use_container_width=True)
    
    # Top opportunities
    st.markdown("---")
    st.subheader("🎯 Top Opportunities")
    
    opportunities = create_top_opportunities(df)
    if len(opportunities) > 0:
        # Format for display
        display_df = opportunities.copy()
        display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
        display_df['price'] = '$' + display_df['price'].round(2).astype(str)
        
        # Color coding
        def color_signal(val):
            if val == 'LONG':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'SHORT':
                return 'background-color: #f8d7da; color: #721c24'
            return ''
        
        styled_df = display_df.style.applymap(color_signal, subset=['signal'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No high-confidence opportunities found.")
    
    # Symbol detail view
    st.markdown("---")
    st.subheader("📈 Symbol Detail View")
    
    selected_symbol = st.selectbox(
        "Select a symbol to view trends",
        options=sorted(df['symbol'].unique()),
        index=0 if len(df) > 0 else None
    )
    
    if selected_symbol and history_data:
        history_df = pd.DataFrame(history_data.get('history', []))
        if len(history_df) > 0:
            trend_fig = create_trend_chart(history_df, selected_symbol)
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)
            else:
                st.info(f"No historical data for {selected_symbol}")
    
    # Raw data view
    st.markdown("---")
    with st.expander("View Raw Data"):
        st.dataframe(df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Data source: <a href='https://github.com/impro58-oss/rooquest1'>GitHub Repository</a> | "
        "Strategy: TrojanLogic4H (CS RSI MTF + RtoM Channels)"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
