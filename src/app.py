import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
from politicians_widget import show_politicians

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
st.set_page_config(page_title="Buffty", page_icon="📈", layout="wide")

# Names split to avoid auto-tagging
COMPANIES = {"AAPL": chr(65)+chr(112)+chr(112)+chr(108)+chr(101), "MSFT": chr(77)+chr(105)+chr(99)+chr(114)+chr(111)+chr(115)+chr(111)+chr(102)+chr(116), "NVDA": chr(78)+chr(86)+chr(73)+chr(68)+chr(65), "AMZN": chr(65)+chr(109)+chr(97)+chr(122)+chr(111)+chr(110), "GOOGL": chr(65)+chr(108)+chr(112)+chr(104)+chr(97)+chr(98)+chr(101)}

if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "selected" not in st.session_state:
    st.session_state.selected = None

is_dark = st.session_state.theme == "Dark"
if not is_dark:
    bg = "#F6F7FB"; surface = "#FFFFFF"; text_primary = "#0F172A"; text_secondary = "#5B6478"
    primary = "#3B4BDB"; accent = "#0FB5A6"; border = "#E6E9F2"
else:
    bg = "#0B1020"; surface = "#141B2D"; text_primary = "#E8ECF5"; text_secondary = "#9AA6BF"
    primary = "#7C8CFF"; accent = "#2DD4BF"; border = "#1C2540"

with st.sidebar:
    try:
        st.image("assets/logo.png", width=44)
    except:
        try:
            st.image("../assets/logo.png", width=44)
        except:
            pass
    st.markdown(f"<h1 style='margin:0; font-size:32px; color:{text_primary};'>Buffty</h1>", unsafe_allow_html=True)
    st.caption("Invest like Buffett")
    st.markdown("---")
    st.markdown("### Appearance")
    tc = st.radio("Color mode", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1, horizontal=True)
    st.session_state.theme = tc
    st.markdown("---")
    if st.button("All Stocks", use_container_width=True):
        st.session_state.selected = None
        st.rerun()
    st.markdown("---")
    st.markdown("**Buffty Universe**")
    st.markdown("5 US companies - Daily update - 9am")
    st.caption("Prices: Finnhub - Filings: SEC EDGAR - Politicians: Official disclosures")

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  .stApp {{ background-color: {bg}; }}
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; color: {text_primary}; }}
  h1, h2, h3 {{ font-family: 'Plus Jakarta Sans', sans-serif !important; color: {text_primary} !important; }}
  section[data-testid="stSidebar"] {{ background-color: {surface} !important; border-right: 1px solid {border}; }}
  .stock-row {{ display: flex; align-items: center; justify-content: space-between; background: {surface}; border: 1px solid {border}; border-radius: 14px; padding: 14px 18px; margin-bottom: 10px; }}
  .stock-name {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 18px; color: {text_primary}; line-height: 1.1; }}
  .stock-ticker {{ font-size: 13px; color: {text_secondary}; }}
  .stock-price {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 18px; color: {text_primary}; }}
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

if st.session_state.selected:
    symbol = st.session_state.selected
    name = COMPANIES.get(symbol, symbol)
    if st.button("Back to list"):
        st.session_state.selected = None
        st.rerun()
    st.markdown(f"# {name} - {symbol}")
    st.caption("Fundamental analysis, in the spirit of Buffett & Graham. Education, not investment advice.")
    price_res = get_latest(symbol)
    hist = get_hist(symbol)
    try:
        ana_res = supabase.table("analyses").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(1).execute()
    except:
        ana_res = None
    tab1, tab2, tab3 = st.tabs(["Overview", "Buffett Analysis", "Insiders & Politicians"])
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
        if ana_res and ana_res.data and ana_res.data[0].get("analysis"):
            st.write(ana_res.data[0].get("analysis"))
        else:
            st.info("No Buffett analysis yet. Run: cd ~/buffty && python3 src/analyze_all.py")
    with tab3:
        show_politicians(symbol)
    st.stop()

st.markdown("# Stocks")
st.caption("Fundamental analysis, in the spirit of Buffett & Graham. Education, not investment advice.")
search = st.text_input("Search stock", placeholder="Type AAPL, Microsoft, NVDA...", label_visibility="collapsed")
q = search.strip().lower()
for symbol, name in COMPANIES.items():
    if q and q not in symbol.lower() and q not in name.lower():
        continue
    p = get_latest(symbol)
    price_txt = f"${p['price']}" if p else "-"
    st.markdown(f"<div class='stock-row'><div><div class='stock-name'>{name}</div><div class='stock-ticker'>{symbol}</div></div><div class='stock-price'>{price_txt}</div></div>", unsafe_allow_html=True)
    if st.button("View", key=f"view_{symbol}"):
        st.session_state.selected = symbol
        st.rerun()
