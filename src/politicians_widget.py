import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

def show_politicians(symbol):
    st.subheader(f"Politician Trades - {symbol}")
    st.caption("Source: Official House + Senate disclosures via Capitol Trades public pages")
    headers = {"User-Agent": "Mozilla/5.0 Buffty"}
    url = f"https://www.capitoltrades.com/trades?tickers={symbol}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("tbody tr")
        if not rows:
            st.info(f"No recent politician trades found. Check manually: {url}")
            return
        shown = 0
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 8:
                continue
            # cols: Politician | Issuer | Published | Traded | FiledAfter | Owner | Type | Size | Price
            raw_pol = cols[0]  # e.g. Harriet HagemanRepublicanHouseWY
            issuer = cols[1]   # e.g. Abbott LaboratoriesABT:US
            # Only keep rows for THIS ticker - Capitol Trades ignores the filter, so we filter here
            if symbol not in issuer and symbol.lower() not in issuer.lower():
                # Also allow company name match via symbol mapping in app - skip if issuer doesn't contain symbol
                # If we filtered everything out, we still want to show something, so count and continue
                continue
            # Parse Name / Party / Position from squashed string
            party = "Unknown"
            position = "Congress"
            name = raw_pol
            for p in ["Republican", "Democrat", "Independent"]:
                if p in raw_pol:
                    party = p
                    parts = raw_pol.split(p)
                    name = parts[0].strip()
                    rest = p.join(parts[1:])
                    if "Senate" in rest:
                        position = "Senate"
                    elif "House" in rest:
                        position = "House"
                    break
            traded = cols[3] if len(cols) > 3 else ""
            trade_type = cols[6] if len(cols) > 6 else ""
            size = cols[7] if len(cols) > 7 else ""
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.caption(f"{position} | {party}")
                st.markdown(f"**{symbol}** | {trade_type} | {size} | {traded}")
            shown += 1
            if shown >= 8:
                break
        if shown == 0:
            st.info(f"No {symbol} politician trades in the latest Capitol Trades list. Check manually: {url}")
    except Exception as e:
        st.info(f"Could not load politician data: {e}")
