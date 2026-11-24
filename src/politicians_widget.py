import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def show_politicians(symbol):
    st.subheader(f"🏛 Politician Trades — {symbol}")
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
            raw_name = cols[0] if len(cols) > 0 else "Unknown"
            # Parse Name + Party from "Name (D-CA)" / "Name (R-TX)"
            m = re.search(r"\((D|R|I)[^)]*\)", raw_name)
            party = {"D": "Democrat", "R": "Republican", "I": "Independent"}.get(m.group(1) if m else "", "Unknown")
            name = re.sub(r"\s*\(.*?\)", "", raw_name).strip()
            # Position: Capitol Trades page distinguishes House/Senate in detail page; row itself doesn't carry it,
            # so we label as Congress/Senate from the trade source, default Congress
            position = "Congress"
            # Heuristic: if detail link mentions senate, use Senate - checked via row link
            link = row.find("a")
            if link and "senate" in str(link.get("href", "")).lower():
                position = "Senate"
            traded = cols[3] if len(cols) > 3 else (cols[2] if len(cols) > 2 else "")
            trade_type = cols[6] if len(cols) > 6 else ""
            size = cols[7] if len(cols) > 7 else ""
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(f"{position} | {party}")
                st.markdown(f"**{symbol}** | {trade_type} | {size} | {traded}")
    except Exception as e:
        st.info(f"Could not load politician data: {e}")
