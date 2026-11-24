import streamlit as st
import requests
from bs4 import BeautifulSoup

def show_politicians(symbol):
    st.subheader(f"🏛️ Politician Trades — {symbol} (Delayed 30-45 days)")
    st.caption("Source: Official House + Senate disclosures via Capitol Trades public pages")
    headers = {"User-Agent": "Mozilla/5.0 Buffty"}
    url = f"https://www.capitoltrades.com/trades?tickers={symbol}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("tbody tr")[:5]
        if not rows:
            st.info(f"No recent politician trades found. Check manually: {url}")
            return
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if cols:
                st.write(" • " + " | ".join(cols))
    except Exception as e:
        st.info(f"Could not load politician data: {e}")
