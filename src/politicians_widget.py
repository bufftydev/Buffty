import streamlit as st
import requests
from bs4 import BeautifulSoup

def show_politicians(symbol):
    st.subheader(f"🏛 Politician Trades — {symbol} (Delayed 30-45 days)")
    st.caption("Source: Official House + Senate disclosures via Capitol Trades public pages")
    headers = {"User-Agent": "Mozilla/5.0 Buffty"}
    url = f"https://www.capitoltrades.com/trades?tickers={symbol}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("tbody tr")[:8]
        if not rows:
            st.info(f"No recent politician trades found. Check manually: {url}")
            return
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if not cols:
                continue
            # Capitol Trades columns: Politician | Issuer | Published | Traded | Filed After | Owner | Type | Size | Price
            name = cols[0] if len(cols) > 0 else "Unknown"
            issuer = cols[1] if len(cols) > 1 else symbol
            published = cols[2] if len(cols) > 2 else ""
            traded = cols[3] if len(cols) > 3 else published
            trade_type = cols[6] if len(cols) > 6 else ""
            size = cols[7] if len(cols) > 7 else ""
            # Position: Capitol Trades lists House/Senate in politician page, default to Congress if unknown
            # We keep subtitle as Position | Party pattern - party is in name on site, so show name detail as subtitle
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(f"Congress | {issuer}")
                st.markdown(f"**{symbol}** | {trade_type} | {size} | {traded}")
    except Exception as e:
        st.info(f"Could not load politician data: {e}")
