import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 Buffty"}

for symbol in ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
    print("\n==== " + symbol + " - Politician Trades (Capitol Trades, public) ====")
    url = f"https://www.capitoltrades.com/trades?tickers={symbol}"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"  Could not load page - status {r.status_code}")
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        # Capitol Trades table rows
        rows = soup.select("tbody tr")[:5]
        if not rows:
            print("  No rows found - site may block scraping, try opening in browser")
            print(f"  Open this in browser to verify: {url}")
            continue
        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if cols:
                print("  " + " | ".join(cols))
    except Exception as e:
        print(f"  Error: {e}")
