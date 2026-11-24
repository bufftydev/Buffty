import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def show_politicians(symbol):
    st.subheader(f"Politician Trades - {symbol}")
    st.caption("Source: Official House + Senate disclosures via Capitol Trades public pages")
    try:
        res = supabase.table("politicians").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(8).execute()
        rows = res.data or []
        if not rows:
            st.info(f"No {symbol} politician trades in the latest cached list. Capitol Trades only shows the newest 12 trades in its static list — check the full history here:")
            st.link_button(f"See all {symbol} trades on Capitol Trades", f"https://www.capitoltrades.com/trades?tickers={symbol}")
            return
        for r in rows:
            with st.container(border=True):
                st.markdown(f"**{r.get('name','Unknown')}**")
                st.caption(f"{r.get('position','Congress')} | {r.get('party','Unknown')}")
                st.markdown(f"**{symbol}** | {r.get('trade_type','')} | {r.get('size','')} | {r.get('traded_date','')}")
    except Exception as e:
        st.info(f"Could not load politician data: {e}")
        st.link_button(f"See {symbol} on Capitol Trades", f"https://www.capitoltrades.com/trades?tickers={symbol}")
