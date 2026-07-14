import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import time
from datetime import datetime, timezone, timedelta

# 🎨 1. الإعدادات وتصميم الصفحة الرسومية الفاخرة المظلمة المعززة
st.set_page_config(page_title="منصة مستشار التداول المحترف العالمية", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; background-color: #0A0A0E; }
    h1, h2, h3, p, th, td, label { text-align: right; direction: rtl; font-family: 'Cairo', sans-serif; color: #FFFFFF; }
    .stDataFrame { background-color: #12121A; border-radius: 10px; }
    div[data-testid="stSidebar"] { background-color: #0E0E12; direction: rtl; }
    div.stButton > button { width: 100%; background-color: #1A1A26; color: #00FF00; border-radius: 5px; border: 1px solid #00FF00; }
    div.stButton > button:hover { background-color: #00FF00; color: black; }
    .trading-window { background-color: #0F0F17; border: 1px solid #222235; border-radius: 6px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 محطة الرصد والتحليل الفني المؤسساتي - ملهم")

TOTAL_CAPITAL = 25000      
RISK_PER_TRADE = 0.01     

def calculate_advanced_targets(entry_price, stop_loss):
    risk_per_share = entry_price - stop_loss
    if risk_per_share <= 0: return 0, 0, 0, 0, 0, 0, 0, 0
    total_shares = int((TOTAL_CAPITAL * RISK_PER_TRADE) / risk_per_share)
    allocated_capital = total_shares * entry_price
    if allocated_capital > (TOTAL_CAPITAL * 0.25):
        total_shares = int((TOTAL_CAPITAL * 0.25) / entry_price)
        allocated_capital = total_shares * entry_price
    tp1 = entry_price + (risk_per_share * 1.2)
    tp2 = entry_price + (risk_per_share * 2.5)   
    tp3 = entry_price + (risk_per_share * 4.0) 
    return total_shares, allocated_capital, tp1, int(total_shares*0.5), tp2, int(total_shares*0.3), tp3, total_shares - (int(total_shares*0.5) + int(total_shares*0.3))

real_market_prices = {
    "1120": {"name": "الراجحي", "price": 65.95}, "1180": {"name": "الأهلي", "price": 38.90},
    "1150": {"name": "الإنماء", "price": 24.20}, "7010": {"name": "اس تي سي", "price": 43.56}
}

# قراءة الملف مع إدخال صمام الحماية ضد هجمات المرور
filename = "tickerchart_live.csv"
if os.path.exists(filename):
    try:
        df_live = pd.read_csv(filename, sep=';', on_bad_lines='skip', encoding='windows-1256')
        df_live.columns = df_live.columns.str.strip()
        for idx, row in df_live.iterrows():
            sym = str(row.get('Symbol', row.get('رمز', ''))).strip()
            if sym in real_market_prices:
                real_market_prices[sym]["price"] = round(float(row.get('Last', row.get('آخر', real_market_prices[sym]["price"]))), 2)
    except Exception: pass

if 'current_tf' not in st.session_state: st.session_state.current_tf = "15 دقيقة"

market_data_list = []
stock_dfs = {}

for ticker, info in real_market_prices.items():
    c_close = info["price"]
    stock_dfs[ticker] = pd.DataFrame({'Open': [c_close]*20, 'High': [c_close*1.01]*20, 'Low': [c_close*0.99]*20, 'Close': [c_close]*20}, index=pd.date_range(end=datetime.now(), periods=20, freq='15min'))
    market_data_list.append({"رمز السهم": ticker, "اسم الشركة": info["name"], "السعر الحالي": c_close})

df_market = pd.DataFrame(market_data_list)
col_list, col_chart, col_calc = st.columns([1.4, 2.3, 1.3])

with col_list:
    st.markdown("<div class='trading-window'>", unsafe_allow_html=True)
    selected_option = st.selectbox("اختر الشركة للربط الفوري:", [f"{r['رمز السهم']} - {r['اسم الشركة']}" for _, r in df_market.iterrows()])
    selected_ticker = selected_option.split(" - ")[0]
    st.dataframe(df_market, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_chart:
    st.markdown("<div class='trading-window'>", unsafe_allow_html=True)
    df_selected = stock_dfs[selected_ticker]
    last_row = df_selected.iloc[-1]
    sl_val = round(last_row['Low'] * 0.99, 2)
    t_s, capital, tp1, s1, tp2, s2, tp3, s3 = calculate_advanced_targets(last_row['Close'], sl_val)
    
    fig = go.Figure(data=[go.Candlestick(x=df_selected.index, open=df_selected['Open'], high=df_selected['High'], low=df_selected['Low'], close=df_selected['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=True, height=450)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_calc:
    st.markdown("<div class='trading-window'>", unsafe_allow_html=True)
    if t_s > 0:
        st.markdown(f"### 🔢 إدارة محفظتك ({TOTAL_CAPITAL} ريال):\n* **الأسهم:** `{t_s}` سهم\n* **السيولة:** `{capital:.2f}` ريال\n* 🎯 **TP1:** `{tp1:.2f}`\n* 🎯 **TP2:** `{tp2:.2f}`\n* 🎯 **TP3:** `{tp3:.2f}`")
    st.markdown("</div>", unsafe_allow_html=True)

# 🛡️ قفل صمام التهدئة لمنع هجوم الـ Connection Reset السحابي
time.sleep(1)
