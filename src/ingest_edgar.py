import requests

headers = {"User-Agent": "Buffty buffty@example.com"}

companies = [("AAPL", "0000320193"), ("MSFT", "0000789019"), ("NVDA", "0001045810")]

for symbol, cik in companies:
    url = "https://data.sec.gov/submissions/CIK" + cik + ".json"
    data = requests.get(url, headers=headers).json()
    recent = data["filings"]["recent"]
    print("\n" + symbol + " - Latest filings:")
    for i in range(3):
        date = recent["filingDate"][i]
        form = recent["form"][i]
        doc = recent["primaryDocument"][i]
        print("  " + date + " - " + form + " - " + doc)
