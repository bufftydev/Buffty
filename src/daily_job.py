import subprocess
import sys

print("=== Buffty Daily Job ===")
print("1. Ingesting prices...")
subprocess.run([sys.executable, "src/ingest_prices.py"], check=True)
print("2. Ingesting filings...")
subprocess.run([sys.executable, "src/ingest_edgar.py"], check=True)
print("3. Analyzing all stocks...")
subprocess.run([sys.executable, "src/analyze_all.py"], check=True)
print("=== Daily Job Done ✅ ===")
