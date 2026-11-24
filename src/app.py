import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="Buffty — Invest like Buffett", page_icon="📈", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

with st.sidebar:
    try:
        st.image('assets/logo.png', width=140)
    except:
        try:
            st.image('../assets/logo.png', width=140)
        except:
            pass
    st.markdown("### 🎨 Appearance")
    theme_choice = st.radio("Color mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1, horizontal=True)
    st.session_state.theme = theme_choice
    st.markdown("---")
    st.markdown("### 🧭 Pick a company")
    symbol = st.selectbox("Stock", ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Buffty Universe**")
    st.markdown("5 US companies • Daily update • 9am")
    st.caption("Prices: Finnhub • Filings: SEC EDGAR • Politicians: Official disclosures")

is_dark = st.session_state.theme == "Dark"

if not is_dark:
    bg = "#F6F7FB"; surface = "#FFFFFF"; text_primary = "#0F172A"; text_secondary = "#5B6478"
    primary = "#3B4BDB"; accent = "#0FB5A6"; positive = "#12A150"; negative = "#E5484D"; warning = "#F5A524"
    header_bg = "#FFFFFF"; header_text = "#0F172A"; border = "#E6E9F2"
else:
    bg = "#0B1020"; surface = "#141B2D"; elevated = "#1C2540"; text_primary = "#E8ECF5"; text_secondary = "#9AA6BF"
    primary = "#7C8CFF"; accent = "#2DD4BF"; positive = "#34D399"; negative = "#FF6B6B"; warning = "#FBBF24"
    header_bg = "#141B2D"; header_text = "#E8ECF5"; border = "#1C2540"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  .stApp {{ background-color: {bg}; }}
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; color: {text_primary}; }}
  h1, h2, h3, h4, h5, h6 {{ font-family: 'Plus Jakarta Sans', sans-serif !important; color: {text_primary} !important; font-weight: 700; letter-spacing: -0.02em; }}
  p, li, span, div {{ color: {text_primary}; }}
  .buffty-header {{ background: {header_bg}; padding: 28px 32px; border-radius: 16px; margin-bottom: 24px; border: 1px solid {border}; }}
  .buffty-header h1 {{ color: {header_text} !important; margin: 0; font-size: 42px; }}
  .buffty-header p {{ color: {text_secondary} !important; margin: 8px 0 0 0; font-size: 16px; }}
  .buffty-badge {{ display: inline-block; background: {primary}; color: white !important; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-top: 12px; }}
  .buffty-badge-accent {{ display: inline-block; background: {accent}; color: white !important; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; margin-left: 8px; margin-top: 12px; }}
  [data-testid="stMetric"] {{ background: {surface}; padding: 18px; border-radius: 12px; border: 1px solid {border}; }}
  [data-testid="stMetric"] label {{ color: {text_secondary} !important; font-family: 'Inter', sans-serif !important; }}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {text_primary} !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
  .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
  .stTabs [data-baseweb="tab"] {{ background: {surface}; border-radius: 10px 10px 0 0; padding: 10px 18px; color: {text_secondary}; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
  .stTabs [aria-selected="true"] {{ background: {primary} !important; color: white !important; }}
  section[data-testid="stSidebar"] {{ background-color: {surface} !important; border-right: 1px solid {border}; }}
  section[data-testid="stSidebar"] * {{ color: {text_primary} !important; }}
  hr {{ border-color: {border} !important; }}
  a {{ color: {primary} !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="buffty-header">
  <h1>📈 Buffty</h1>
  <p>Fundamental analysis, in the spirit of Buffett & Graham. Education, not investment advice.</p>
  <span class="buffty-badge">{st.session_state.theme} Mode • {symbol}</span>
  <span class="buffty-badge-accent">Live • Daily 9am</span>
</div>
""", unsafe_allow_html=True)

price_res = supabase.table("prices").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(1).execute()
ana_res = supabase.table("analyses").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(1).execute()
hist = supabase.table("prices").select("*").eq("symbol", symbol).order("created_at", desc=False).limit(20).execute()

tab1, tab2, tab3 = st.tabs(["📊 Overview", "📝 Buffett Analysis", "🏛️ Insiders & Politicians"])

with tab1:
    if price_res.data:
        p = price_res.data[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest Price", f"${p['price']}")
        c2.metric("Daily Change", f"{p['change_pct']}%")
        c3.metric("Last Updated", str(p['created_at'])[:10])
    if hist.data:
        st.subheader("Price History")
        st.line_chart([float(x["price"]) for x in hist.data])
        st.caption("Last 20 price points from Supabase")

with tab2:
    if ana_res.data:
        st.markdown(ana_res.data[0]["summary"])
    else:
        st.info("No analysis yet. Run: python3 src/analyze_all.py")

with tab3:
    st.subheader(f"Politician Trades — {symbol}")
    st.caption("Source: Official House + Senate disclosures via Capitol Trades public pages. Delayed 30-45 days by law.")
    headers = {"User-Agent": "Mozilla/5.0 Buffty"}
    url = f"https://www.capitoltrades.com/trades?tickers={symbol}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("tbody tr")[:8]
        if not rows:
            st.info(f"No recent politician trades. Check: {url}")
        else:
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if cols:
                    st.write(" • " + " | ".join(cols))
    except Exception as e:
        st.info(f"Could not load: {e}")

st.markdown("---")
st.caption("Buffty • Headings: Plus Jakarta Sans • Body: Inter • Light: #F6F7FB / Dark: #0B1020")
