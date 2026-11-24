import os
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Get latest AAPL price from Supabase
result = supabase.table("prices").select("*").eq("symbol", "AAPL").order("created_at", desc=True).limit(1).execute()
latest = result.data[0] if result.data else {"price": "unknown", "change_pct": "unknown"}
price = latest["price"]
change = latest["change_pct"]

prompt = f"""
You are Buffty, a fundamental analyst in the style of Warren Buffett and Ben Graham.
Analyze AAPL with this data:
- Latest price: ${price}
- Daily change: {change}%
- Latest insider activity: Form 4 filed 2026-11-19

Write a 1-page summary with:
1. Business in plain English (what does 【entity-Apple¦canonical_name=Apple】 sell, where does money come from)
2. Moat (why is it hard to compete with)
3. Financial health (use general knowledge: margins, cash, debt)
4. Valuation sanity check (is it expensive vs history, use P/E logic, do not invent exact live P/E if unsure, say "check")
5. Risks (2-3)
6. Buffett verdict: Would Buffett like this business? Why / why not?

Be honest, no hype. End with: "This is education, not investment advice."
"""

chat = groq_client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

print(chat.choices[0].message.content)
