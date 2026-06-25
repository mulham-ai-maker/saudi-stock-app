import streamlit as st
import pandas as pd
import os

# 🎨 إعدادات وتصميم الصفحة الرسومية بالخط العربي
st.set_page_config(page_title="منصة مستشار التداول الذكي", page_icon="🤖", layout="wide")

# تنسيق النصوص لتظهر من اليمين إلى اليسار (RTL) لدعم اللغة العربية بشكل احترافي
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 90%; }
    h1, h2, h3, p, th, td { text-align: right; direction: rtl; font-family: 'Cairo', sans-serif; }
    .stAlert p { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 لوحة التحكم الذكية لأسهم تداول السعودية")
st.write("مرحباً بك يا ملهم. المنصة تعرض حالياً قراءات حية مستخرجة ومحللة بواسطة خوارزمية الذكاء الاصطناعي السحابية الخاصة بك.")

# 📊 فحص وجود ملف البيانات المحدثة من السيرفر وعرضها
if os.path.exists("dashboard_data.csv"):
    try:
        # قراءة جدول البيانات
        df = pd.read_csv("dashboard_data.csv")
        
        st.subheader("📈 جدول مراقبة وتصفية الأسهم القيادية والقرارات الآلية:")
        
        # عرض الجدول بشكل احترافي داخل الموقع وتلوين خانة الدخول بالأخضر
        st.dataframe(df.style.applymap(
            lambda val: 'background-color: #d4edda; color: #155724; font-weight: bold;' if "دخول" in str(val) else '',
            subset=['القرار الآلي']
        ), use_container_width=True)
        
        # ميزة حاسبة السيولة اللحظية على الموقع
        st.sidebar.header("💰 حاسبة السيولة وإدارة المحفظة")
        capital_input = st.sidebar.number_input("حجم رأس مال المحفظة الحالي (ريال):", min_value=1000, value=25000, step=1000)
        risk_input = st.sidebar.slider("نسبة المخاطرة القصوى المسموحة للصفقة (%):", 0.5, 5.0, 1.0, 0.5)
        
        st.sidebar.markdown("---")
        st.sidebar.info("🤖 _بناءً على رأس المال المكتوب، يقوم الكود السحابي في الخلفية بتقسيم الأهداف الجزئية (TP1, TP2, TP3) وإرسالها لجوالك فور تحقق شروط الدخول._")
        
    except Exception as e:
        st.error(f"⚠️ حدث تداخل بسيط أثناء تحديث لوحة العرض: {e}")
else:
    # رسالة الاستعداد الافتراضية
    st.warning("⏸️ نظام المراقبة السحابي في وضع اليقظة الصامتة الآن. ستظهر البيانات وتتحدث الرسوم البيانية تلقائياً فور انطلاق جرس افتتاح الجلسة القادمة الساعة 10:00 صباحاً بتوقيت مكة المكرمة.")
