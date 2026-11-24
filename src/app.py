import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from politicians_widget import show_politicians

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="Buffty", page_icon="📈", layout="wide")

COMPANIES = {
    "AAPL": "【entity-Apple¦canonical_name=Apple】",
    "MSFT": "【entity-Microsoft¦canonical_name=Microsoft】",
    "NVDA": "【entity-NVIDIA¦canonical_name=NVIDIA】",
    "AMZN": "【entity-Amazon¦canonical_name=Amazon】",
    "GOOGL": "Alphabet",
}

if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "selected" not in st.session_state:
    st.session_state.selected = None
if "search" not in st.session_state:
    st.session_state.search = ""

is_dark = st.session_state.theme == "Dark"
if not is_dark:
    bg = "#F6F7FB"; surface = "#FFFFFF"; text_primary = "#0F172A"; text_secondary = "#5B6478"
    primary = "#3B4BDB"; accent = "#0FB5A6"; positive = "#12A150"; negative = "#E5484D"; warning = "#F5A524"
    header_bg = "#FFFFFF"; header_text = "#0F172A"; border = "#E6E9F2"
else:
    bg = "#0B1020"; surface = "#141B2D"; elevated = "#1C2540"; text_primary = "#E8ECF5"; text_secondary = "#9AA6BF"
    primary = "#7C8CFF"; accent = "#2DD4BF"; positive = "#34D399"; negative = "#FF6B6B"; warning = "#FBBF24"
    header_bg = "#141B2D"; header_text = "#E8ECF5"; border = "#1C2540"

# --- SIDEBAR: Buffty lives ONLY here ---
with st.sidebar:
    # Logo + full Buffty word, colors adapt to theme
    try:
        st.image("assets/logo.png", width=44)
    except:
        try:
            st.image("../assets/logo.png", width=44)
        except:
            pass
    st.markdown(f"<h1 style='margin:0; font-family:Plus Jakarta Sans; color:{text_primary}; font-size:32px;'>Buffty</h1>", unsafe_allow_html=True)
    st.caption("Invest like Buffett")
    st.markdown("---")
    st.markdown("### 🎨 Appearance")
    theme_choice = st.radio("Color mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1, horizontal=True)
    st.session_state.theme = theme_choice
    st.markdown("---")
    if st.button("🏠 All Stocks", use_container_width=True):
        st.session_state.selected = None
        st.rerun()
    st.markdown("---")
    st.markdown("**Buffty Universe**")
    st.markdown("5 US companies • Daily update • 9am")
    st.caption("Prices: Finnhub • Filings: SEC EDGAR • Politicians: Official disclosures")

# Global style - NO Buffty header in main
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  .stApp {{ background-color: {bg}; }}
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; color: {text_primary}; }}
  h1, h2, h3, h4, h5, h6 {{ font-family: 'Plus Jakarta Sans', sans-serif !important; color: {text_primary} !important; font-weight: 700; letter-spacing: -0.02em; }}
  p, li, span, div {{ color: {text_primary}; }}
  [data-testid="stMetric"] {{ background: {surface}; padding: 18px; border-radius: 12px; border: 1px solid {border}; }}
  [data-testid="stMetric"] label {{ color: {text_secondary} !important; }}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {{ color: {text_primary} !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }}
  section[data-testid="stSidebar"] {{ background-color: {surface} !important; border-right: 1px solid {border}; }}
  section[data-testid="stSidebar"] * {{ color: {text_primary} !important; }}
  hr {{ border-color: {border} !important; }}
  a {{ color: {primary} !important; }}
</style>
""", unsafe_allow_html=True)

def get_latest(symbol):
    try:
        r = supabase.table("prices").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(1).execute()
        return r.data[0] if r.data else None
    except:
        return None

def get_hist(symbol):
    try:
        r = supabase.table("prices").select("*").eq("symbol", symbol).order("created_at", desc=False).limit(20).execute()
        return r.data or []
    except:
        return []

# ===== STOCK PAGE =====
if st.session_state.selected:
    symbol = st.session_state.selected
    name = COMPANIES.get(symbol, symbol)
    if st.button("← Back to list"):
        st.session_state.selected = None
        st.rerun()
    # Title = Company Name + Ticker, NO Buffty here
    st.markdown(f"# {name} — {symbol}")
    st.caption(f"{name} • {symbol} • Fundamental analysis, in the spirit of Buffett & Graham. Education, not investment advice.")
    price_res = get_latest(symbol)
    hist = get_hist(symbol)
    try:
        ana_res = supabase.table("analyses").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(1).execute()
    except:
        ana_res = None
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📝 Buffett Analysis", "🏛 Insiders & Politicians"])
    with tab1:
        if price_res:
            c1, c2 = st.columns(2)
            c1.metric("Latest Price", f"${price_res.get('price')}")
            if price_res.get('change') is not None:
                c2.metric("Change", f"{price_res.get('change')}%")
            if hist:
                st.line_chart([float(x["price"]) for x in hist])
                st.caption("Last 20 price points from Supabase")
        else:
            st.info("No price data yet. Run ingest_prices.py")
    with tab2:
        if ana_res and ana_res.data:
            st.write(ana_res.data[0].get("analysis", "No analysis yet."))
        else:
            st.info("No Buffett analysis yet. Run analyze_all.py")
    with tab3:
        show_politicians(symbol)
    st.stop()

# ===== MAIN PAGE: LIST =====
st.markdown("# Stocks")
st.caption("Fundamental analysis, in the spirit of Buffett & Graham. Education, not investment advice.")
search = st.text_input("Search stock", placeholder="Type AAPL, Microsoft, NVDA...", value=st.session_state.search, label_visibility="collapsed")
st.session_state.search = search
q = search.strip().lower()
for symbol, name in COMPANIES.items():
    if q and q not in symbol.lower() and q not in name.lower():
        continue
    p = get_latest(symbol)
    price_txt = f"${p['price']}" if p else "—"
    change_txt = f"{p.get('change', '')}%" if p and p.get('change') is not None else ""
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.markdown(f"**{name}**")
            st.caption(symbol)
        with c2:
            st.markdown(f"**{price_txt}**")
            if change_txt:
                st.caption(change_txt)
        with c3:
            if st.button("View →", key=f"view_{symbol}", use_container_width=True):
                st.session_state.selected = symbol
                st.rerun()
