import os
from dotenv import load_dotenv
import finnhub
from supabase import create_client

load_dotenv()

finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

for symbol in ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
    quote = finnhub_client.quote(symbol)
    price = quote['c']
    change = quote['d']
    print(f"{symbol}: ${price}  change: {change}%")

    supabase.table("prices").insert({
        "symbol": symbol,
        "price": price,
        "change_pct": change
    }).execute()

print("Saved to Supabase ✅")
