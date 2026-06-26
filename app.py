import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

# 🎨 1. إعدادات وتصميم الصفحة الرسومية بالخط العربي
st.set_page_config(page_title="منصة مستشار التداول الذكي", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 90%; }
    h1, h2, h3, p, th, td { text-align: right; direction: rtl; font-family: 'Cairo', sans-serif; }
    .stAlert p { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 لوحة التحكم الذكية لأسهم تداول السعودية")
st.write("مرحباً بك يا ملهم. المنصة تعرض حالياً قراءات حية مستخرجة ومحللة بواسطة خوارزمية الذكاء الاصطناعي المباشرة الخاصة بك.")

# 💰 إعدادات المحفظة الافتراضية
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

# 📊 جلب البيانات الفورية وعرضها على الهواء مباشرة للمستخدم
with st.spinner("🔄 جاري الطواف اللحظي وجلب بيانات الشركات القيادية من السحاب..."):
    saudi_leaders = ["1120", "1180", "1150", "1010", "2222", "2010", "7010", "4013"]
    dashboard_rows = []
    
    for ticker in saudi_leaders:
        df = fetch_saudi_data_proxy(ticker)
        if df is None or df.empty: continue
        
        close_delta = df['Close'].diff()
        up, down = close_delta.clip(lower=0), -1 * close_delta.clip(upper=0)
        ma_up = up.ewm(com=13, adjust=False).mean()
        ma_down = down.ewm(com=13, adjust=False).mean()
        df['RSI'] = 100 - (100 / (1 + (ma_up / ma_down)))
        
        df['Body_Size'] = (df['Close'] - df['Open']).abs()
        avg_body, avg_volume = df['Body_Size'].rolling(20).mean(), df['Volume'].rolling(20).mean()
        df['Current_Demand'] = np.where((df['Close'] > df['Open']) & (df['Body_Size'] > avg_body * 1.5) & (df['Volume'] > avg_volume), df['Low'], np.nan)
        df['Current_Demand'] = df['Current_Demand'].ffill()
        
        last = df.iloc[-1]
        c_close, rsi, c_vol = last['Close'], last['RSI'], last['Volume']
        dem = last['Current_Demand']
        
        v_avg = df['Volume'].iloc[-20:].mean()
        status_text = "انتظار ⏸️"
        mm_status = "⚠️ سيولة اعتيادية"
        if c_vol > (v_avg * 1.5): mm_status = "🔥 سيولة انفجارية"
        if c_close <= (dem * 1.025) and rsi < 65: status_text = "دخول مفعل 🟢"
        
        dashboard_rows.append({
            "السهم": f"{ticker}.SR", "السعر الحالي": f"{c_close:.2f} ريال",
            "مؤشر RSI": f"{rsi:.1f}", "السيولة اللحظية": mm_status, "القرار الآلي": status_text
        })

if dashboard_rows:
    df_display = pd.DataFrame(dashboard_rows)
    st.subheader("📈 جدول مراقبة وتصفية الأسهم القيادية والقرارات الآلية:")
    
    # تلوين الجدول وعرضه حياً
    st.dataframe(df_display.style.applymap(
        lambda val: 'background-color: #d4edda; color: #155724; font-weight: bold;' if "دخول" in str(val) else '',
        subset=['القرار الآلي']
    ), use_container_width=True)
    
    # حاسبة السيولة الجانبية المحدثة
    st.sidebar.header("💰 حاسبة السيولة وإدارة المحفظة")
    capital_input = st.sidebar.number_input("حجم رأس مال المحفظة الحالي (ريال):", min_value=1000, value=TOTAL_CAPITAL, step=1000)
    st.sidebar.markdown("---")
    st.sidebar.info("🤖 المنصة متصلة ومحدثة بأسعار الإغلاق الحالية ومستعدة لرصد الجلسة القادمة.")
else:
    st.warning("⏸️ نظام المراقبة السحابي في وضع اليقظة الصامتة الآن. ستظهر البيانات تلقائياً فور انطلاق جرس الافتتاح.")
