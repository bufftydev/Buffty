import os
from dotenv import load_dotenv
from supabase import create_client
import requests
from bs4 import BeautifulSoup
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
SYMBOLS = ["AAPL","MSFT","NVDA","AMZN","GOOGL"]
headers = {"User-Agent": "Mozilla/5.0 Buffty"}
# Clear old
supabase.table("politicians").delete().neq("id", 0).execute()
for symbol in SYMBOLS:
    saved = 0
    for page in range(1, 21):
        if saved >= 8:
            break
        url = f"https://www.capitoltrades.com/trades?page={page}"
        try:
            r = requests.get(url, headers=headers, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            rows = soup.select("tbody tr")
            if not rows:
                break
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) < 8:
                    continue
                issuer = cols[1]
                if symbol not in issuer:
                    continue
                raw = cols[0]
                party = "Unknown"; position = "Congress"; name = raw
                for p in ["Republican","Democrat","Independent"]:
                    if p in raw:
                        party = p
                        parts = raw.split(p)
                        name = parts[0].strip()
                        rest = p.join(parts[1:])
                        if "Senate" in rest: position = "Senate"
                        elif "House" in rest: position = "House"
                        break
                supabase.table("politicians").insert({
                    "symbol": symbol, "name": name, "position": position, "party": party,
                    "trade_type": cols[6], "size": cols[7], "traded_date": cols[3]
                }).execute()
                saved += 1
                if saved >= 8:
                    break
        except Exception as e:
            print(symbol, "page", page, "error", e)
            break
    print(f"{symbol}: saved {saved}")
