#!/bin/bash
cd ~/buffty
# Stop any old Streamlit
pkill -f streamlit || true
sleep 1
# Start Streamlit headless (don't auto-open Safari) + fix Safari CORS/XSRF that causes blank page
python3 -m streamlit run src/app.py --server.headless true --server.enableCORS false --server.enableXsrfProtection false --server.port 8501 &
sleep 4
# Kill Safari if it opened Buffty, open in Chrome
pkill -f "Safari.*8501" || true
open -a "Google Chrome" http://127.0.0.1:8501
wait
