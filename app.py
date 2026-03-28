import streamlit as st
import yfinance as yf
import google.generativeai as genai
import plotly.graph_objects as go

# এপিআই কি সেটআপ
GEMINI_API_KEY = "AIzaSyAyKJTrVLFj3SNSMHeDC9FNFmrc_qW_QaM"
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if target in models: return target
        return models[0]
    except: return "models/gemini-1.5-flash"

model = genai.GenerativeModel(get_working_model())

# অ্যাপ কনফিগারেশন
st.set_page_config(page_title="READYMADE STOCKS", layout="wide", page_icon="📈")

# লোগো এবং নাম (HII RAJESH)
header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    try:
        st.image("logo.jpg", width=70) 
    except:
        st.write("📈")

with header_col2:
    st.markdown("<h1 style='color: #00ffcc; margin-top: -10px; font-weight: bold;'>HII RAJESH</h1>", unsafe_allow_html=True)

stock_symbol = st.text_input("", placeholder="স্টকের নাম দিন (যেমন: RELIANCE.NS, YESBANK.NS...)")

if stock_symbol:
    try:
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period="1mo", interval="1d")
        info = stock.info
        
        if not hist.empty:
            st.subheader(f"📊 {stock_symbol} Candlestick Chart")
            fig = go.Figure(data=[go.Candlestick(x=hist.index,
                            open=hist['Open'], high=hist['High'],
                            low=hist['Low'], close=hist['Close'],
                            increasing_line_color='#00ff00', 
                            decreasing_line_color='#ff0000')])
            fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, dragmode=False)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

            tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD", "📈 AI STRATEGY", "📰 NEWS & AI ANALYSIS"])

            with tab1:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                diff = curr - prev
                st.write("### 🏛️ Financial Highlights")
                f1, f2, f3 = st.columns(3)
                f1.metric("Market Cap", f"{info.get('marketCap', 'N/A'):,}")
                f2.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
                f3.metric("52W High/Low", f"{info.get('fiftyTwoWeekHigh', 'N/A')} / {info.get('fiftyTwoWeekLow', 'N/A')}")
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**CURRENT PRICE**")
                    st.info(f"₹ {curr:.2f} ({'+' if diff>0 else ''}{diff:.2f})")
                with col2:
                    st.write("**SENTIMENT**")
                    buy_v = 75 if diff > 0 else 38
                    st.success(f"BUY: {buy_v}%")
                    st.error(f"SELL: {100-buy_v}%")
                if st.button("RUN AI ANALYSIS"):
                    with st.spinner("এআই বিশ্লেষণ করছে..."):
                        res = model.generate_content(f"{stock_symbol} সাপোর্ট ও রেসিস্ট্যান্স বাংলায় জানাও।")
                        st.write(res.text)
            
            with tab2:
                if st.button("Generate Strategy"):
                    with st.spinner("AI Strategy বানাচ্ছে..."):
                        res = model.generate_content(f"{stock_symbol} ট্রেডিং স্ট্র্যাটেজি বাংলায় দাও।")
                        st.write(res.text)

            with tab3:
                news_list = stock.news
                if news_list:
                    headlines = [n.get('title') for n in news_list[:5]]
                    for h in headlines: st.info(f"📍 {h}")
                    if st.button("AI NEWS ANALYSIS"):
                        res = model.generate_content(f"খবরগুলোর প্রভাব {stock_symbol} এ বাংলায় বলো: {' '.join(headlines)}")
                        st.write(res.text)
                else: st.warning("খবর পাওয়া যায়নি।")
    except: st.error("সঠিক নাম দিন।")
