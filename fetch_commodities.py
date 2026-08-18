import urllib.request
import json
import base64
import gzip
from datetime import datetime, timezone
import csv

# 1. Define the 13 commodities
COMMODITIES = [
    {"ticker": "CO1:COM",      "name": "Brent Crude Oil"},
    {"ticker": "SBR:COM",      "name": "Synthetic Rubber"},
    {"ticker": "JN1:COM",      "name": "Natural Rubber"},
    {"ticker": "PYL:COM",      "name": "Polypropylene"},
    {"ticker": "POL:COM",      "name": "Polyethylene"},
    {"ticker": "KSP:COM",      "name": "Kraft Pulp"},
    {"ticker": "CT1:COM",      "name": "Cotton"},
    {"ticker": "LN1:COM",      "name": "Nickel"},
    {"ticker": "LMAHDS03:COM", "name": "Aluminium"},
    {"ticker": "HG1:COM",      "name": "Copper"},
    {"ticker": "NG1:COM",      "name": "Natural Gas"},
    {"ticker": "GBRELEPRI:COM","name": "Electricity"},
    {"ticker": "SPSCFI:COM",   "name": "Freight"}
]

KEY_BYTES = "tradingeconomics-charts-core-api-key".encode("utf-8")
KEY_LEN = len(KEY_BYTES)

results = []

for item in COMMODITIES:
    url = f"https://d3ii0wo49og5mi.cloudfront.net/markets/{item['ticker']}?span=3d&ohlc=1&interval=1d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://tradingeconomics.com/",
        "Origin": "https://tradingeconomics.com",
        "x-api-key": "20260324:loboantunes"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            base64_data = resp.read()
            cipher_bytes = base64.b64decode(base64_data)
            
            # XOR Decryption
            decrypted = bytes([cipher_bytes[i] ^ KEY_BYTES[i % KEY_LEN] for i in range(len(cipher_bytes))])
            
            # GZip Decompression
            decompressed = gzip.decompress(decrypted)
            data_json = json.loads(decompressed.decode("utf-8"))
            
            series_data = data_json["series"][0]["data"]
            if series_data:
                # Sort by timestamp desc
                series_data.sort(key=lambda x: x[0], reverse=True)
                latest = series_data[0]
                dt = datetime.fromtimestamp(latest[0], tz=timezone.utc).strftime("%Y-%m-%d")
                price = float(latest[4]) # Open price
                
                results.append({
                    "Commodity": item["name"],
                    "Date": dt,
                    "Price": price
                })
                print(f"[SUCCESS] {item['name']}: {dt} = {price}")
    except Exception as e:
        print(f"[ERROR] {item['name']}: {e}")

# Write output CSV
with open("Commodities_Daily.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Commodity", "Date", "Price"])
    writer.writeheader()
    writer.writerows(results)

print(f"Successfully updated Commodities_Daily.csv with {len(results)} rows.")
