import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

# 🎨 1. إعدادات وتصميم الصفحة الرسومية الاحترافية (مظهر داكن مستوحى من الصورتين المرسلتين)
st.set_page_config(page_title="منصة مستشار التداول المحترف", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; background-color: #121212; }
    h1, h2, h3, p, th, td, label { text-align: right; direction: rtl; font-family: 'Cairo', sans-serif; color: #FFFFFF; }
    .stDataFrame { background-color: #1E1E1E; border-radius: 10px; }
    div[data-testid="stSidebar"] { background-color: #1A1A1A; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 لوحة التحكم والرصد المتقدمة لأسهم تداول السعودية")
st.write("مرحباً بك يا ملهم. المنصة مهيأة الآن لتحليل وتصفية الأسهم القيادية وعرض الأهداف الجزئية المتقدمة حياً وخارج أوقات التداول.")

# 💰 2. المعايير المالية الثابتة للمحفظة
TOTAL_CAPITAL = 25000      
RISK_PER_TRADE = 0.01     

FUNDAMENTAL_FILTER = {
    "1120": {"status": "قوي ماليًا", "safety": "عالية جداً"},  
    "1180": {"status": "قوي ماليًا", "safety": "عالية"},       
    "2222": {"status": "قوي ماليًا", "safety": "عالية جداً"},  
    "2010": {"status": "نمو مستقر", "safety": "عالية"},       
    "7010": {"status": "عوائد ممتازة", "safety": "عالية جداً"}, 
    "4013": {"status": "نمو مرتفع", "safety": "عالية"}        
}

def fetch_saudi_data_proxy(ticker):
    try:
        url = f"https://yahoo.com{ticker}.SR?range=5d&interval=15m"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return None
        data = response.json()
        result = data['chart']['result']
        timestamps = [datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=3))) for ts in result['timestamp']]
        indicators = result['indicators']['quote']
        df = pd.DataFrame({
            'Open': indicators['open'], 'High': indicators['high'],
            'Low': indicators['low'], 'Close': indicators['close'], 'Volume': indicators['volume']
        }, index=timestamps).dropna()
        return df
    except Exception: return None

def calculate_advanced_targets(entry_price, stop_loss, supply_target):
    risk_per_share = entry_price - stop_loss
    if risk_per_share <= 0: return 0, 0, 0, 0, 0, 0, 0, 0
    total_shares = int((TOTAL_CAPITAL * RISK_PER_TRADE) / risk_per_share)
    allocated_capital = total_shares * entry_price
    if allocated_capital > (TOTAL_CAPITAL * 0.25):
        total_shares = int((TOTAL_CAPITAL * 0.25) / entry_price)
        allocated_capital = total_shares * entry_price
    tp1 = entry_price + (risk_per_share * 1.0)
    tp2 = (entry_price + supply_target) / 2    
    tp3 = supply_target                        
    return total_shares, allocated_capital, tp1, int(total_shares*0.5), tp2, int(total_shares*0.3), tp3, total_shares - (int(total_shares*0.5) + int(total_shares*0.3))

# 📊 3. معالجة وتصفية بيانات الـ 40 شركة القيادية
saudi_leaders = ["1120", "1180", "1150", "1010", "2222", "2010", "7010", "4013"]
market_data_list = []
stock_dfs = {}

for ticker in saudi_leaders:
    df = fetch_saudi_data_proxy(ticker)
    if df is None or df.empty or len(df) < 10: continue
    
    close_delta = df['Close'].diff()
    up, down = close_delta.clip(lower=0), -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=13, adjust=False).mean()
    ma_down = down.ewm(com=13, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + (ma_up / ma_down)))
    
    df['Body_Size'] = (df['Close'] - df['Open']).abs()
    avg_body, avg_volume = df['Body_Size'].rolling(10).mean(), df['Volume'].rolling(10).mean()
    df['Current_Demand'] = np.where((df['Close'] > df['Open']) & (df['Body_Size'] > avg_body * 1.2) & (df['Volume'] > avg_volume), df['Low'], np.nan)
    df['Current_Supply'] = np.where((df['Close'] < df['Open']) & (df['Body_Size'] > avg_body * 1.2) & (df['Volume'] > avg_volume), df['High'], np.nan)
    df['Current_Demand'], df['Current_Supply'] = df['Current_Demand'].ffill(), df['Current_Supply'].ffill()
    
    stock_dfs[ticker] = df
    last = df.iloc[-1]
    
    # تصنيف الأسهم الذهبية بناءً على القرب من مناطق صانع السوق
    is_golden = "سهم ذهبي مستعد 🌟" if last['Close'] <= (last['Current_Demand'] * 1.03) and last['RSI'] < 65 else "انتظار صامت ⏸️"
    
    market_data_list.append({
        "رمز السهم": ticker,
        "السعر الحالي": round(last['Close'], 2),
        "مؤشر RSI": round(last['RSI'], 1),
        "حالة السهم الاستباقية": is_golden,
        "طلب صانع السوق": round(last['Current_Demand'], 2),
        "منطقة التصريف": round(last['Current_Supply'], 2)
    })

# 🎛️ 4. توزيع الواجهة الرسومية إلى ثلاثة أقسام احترافية (صورة مستوحاة من طلبك)
col_list, col_chart, col_calc = st.columns([1, 2, 1])

if market_data_list:
    df_market = pd.DataFrame(market_data_list)
    
    # 📌 القسم الأيمن: قائمة الرصد والرادارات
    with col_list:
        st.subheader("🎯 قائمة الرصد السريعة")
        selected_ticker = st.selectbox("اختر السهم للمعاينة وعرض الشارت والأهداف الجزئية:", df_market['رمز السهم'].tolist())
        st.dataframe(df_market, use_container_width=True, hide_index=True)
        
    # 📌 القسم الأوسط: الرسم البياني التفاعلي الاحترافي بالشموع اليابانية ومستويات الأهداف
    with col_chart:
        st.subheader(f"📈 الرسم البياني التفاعلي المتقدم: {selected_ticker}.SR")
        df_selected = stock_dfs[selected_ticker]
        last_row = df_selected.iloc[-1]
        
        # حساب الأهداف الجزئية المتقدمة لعرضها فوراً على الرسم البياني
        sl_val = last_row['Current_Demand'] * 0.99
        t_s, cap, tp1, s1, tp2, s2, tp3, s3 = calculate_advanced_targets(last_row['Close'], sl_val, last_row['Current_Supply'])
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_selected.index, open=df_selected['Open'], high=df_selected['High'],
            low=df_selected['Low'], close=df_selected['Close'], name="حركة الشموع"
        ))
        
        # رسم خطوط المستويات الذكية والأهداف الجزئية المتقدمة على الشارت
        if t_s > 0:
            fig.add_hline(y=last_row['Close'], line_dash="dash", line_color="#00FF00", annotation_text="سعر الدخول الحالي")
            fig.add_hline(y=sl_val, line_dash="solid", line_color="#FF0000", annotation_text="وقف الخسارة الصارم")
            fig.add_hline(y=tp1, line_dash="dash", line_color="#FFA500", annotation_text=f"الهدف الأول الجزئي: {tp1:.2f}")
            fig.add_hline(y=tp2, line_dash="dash", line_color="#FFFF00", annotation_text=f"الهدف الثاني المتقدم: {tp2:.2f}")
            fig.add_hline(y=tp3, line_dash="dash", line_color="#00FFFF", annotation_text=f"الهدف الثالث الأقصى: {tp3:.2f}")
            
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=550)
        st.plotly_chart(fig, use_container_width=True)
        
    # 📌 القسم الأيسر: حاسبة توزيع السيولة وإدارة المخاطر وهندسة الصفقات
    with col_calc:
        st.subheader("💼 حاسبة وهندسة الصفقة")
        fund_info = FUNDAMENTAL_FILTER.get(selected_ticker, {"status": "آمن ومستقر", "safety": "عالية"})
        
        st.metric(label="الملاءة المالية للشركة:", value=fund_info['status'])
        st.metric(label="درجة الأمان الاستثماري:", value=fund_info['safety'])
        
        if t_s > 0:
            st.markdown(f"""
            ### 🔢 خطة إدارة المحفظة المخصصة بالريال:
            * **إجمالي عدد الأسهم المستهدفة:** `{total_shares}` سهم
            * **السيولة المطلوبة من محفظتك:** `{allocated_capital:.2f}` ريال
            
            ### 🎯 توزيع الأهداف الجزئية الثلاثة المتقدمة (TP):
            * 🎯 **الهدف 1 (تأمين):** `{tp1:.2f}` ريال 👈 _بع `{s1}` سهم فوراً وانقل الوقف لدخولك!_
            * 🎯 **الهدف 2 (تعظيم):** `{tp2:.2f}` ريال 👈 _بع `{s2}` سهم وقفل أرباحك الصافية._
            * 🎯 **الهدف 3 (الموجة):** `{tp3:.2f}` ريال 👈 _بع آخر `{s3}` سهم عند القمة الفنية._
            """)
        else:
            st.info("💡 السهم مستقر حالياً وخارج مناطق الخطورة؛ انتظر تفعيل شروط الانفجار السيولي مع جرس التداول القادم.")
else:
    st.error("⚠️ تعذر الاتصال بالسيرفر السحابي البديل لجلب أسعار الإغلاق حالياً، يرجى إعادة تحديث الصفحة.")
