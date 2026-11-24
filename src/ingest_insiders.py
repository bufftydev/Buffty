import requests

headers = {"User-Agent": "Buffty buffty@example.com"}

companies = [("AAPL", "0000320193"), ("MSFT", "0000789019"), ("NVDA", "0001045810")]

for symbol, cik in companies:
    url = "https://data.sec.gov/submissions/CIK" + cik + ".json"
    data = requests.get(url, headers=headers).json()
    recent = data["filings"]["recent"]
    print("\n" + symbol + " - Recent Form 4 Insider Trades:")
    found = 0
    for i in range(len(recent["form"])):
        if recent["form"][i] == "4" and found < 3:
            date = recent["filingDate"][i]
            doc = recent["primaryDocument"][i]
            print("  " + date + " - Form 4 - " + doc)
            found = found + 1
    if found == 0:
        print("  No recent Form 4 found in list")
