import os
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

for symbol in ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]:
    result = supabase.table("prices").select("*").eq("symbol", symbol).order("created_at", desc=True).limit(1).execute()
    latest = result.data[0] if result.data else {"price": "unknown", "change_pct": "unknown"}
    price = latest["price"]
    change = latest["change_pct"]

    prompt = f"""
    You are Buffty, a fundamental analyst in the style of Warren Buffett and Ben Graham.
    Analyze {symbol}:
    - Latest price: ${price}
    - Daily change: {change}%

    Write a short summary with:
    1. Business in plain English
    2. Moat
    3. Financial health
    4. Valuation sanity check
    5. Risks (2-3)
    6. Buffett verdict: Would Buffett like this business? Why / why not?

    Be honest, no hype. End with: "This is education, not investment advice."
    """

    chat = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    summary = chat.choices[0].message.content
    print("\n==== " + symbol + " ====\n")
    print(summary[:500] + "...")

    supabase.table("analyses").insert({"symbol": symbol, "summary": summary}).execute()

print("\nAll 5 saved to Supabase ✅")
