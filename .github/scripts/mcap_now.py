"""Current market cap per ticker (Nasdaq quote summary), for the deal-scan upper-bound filter."""
import json, sys, time, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (AlphaGen Research desk@alphagenresearch.com)", "Accept": "application/json", "Accept-Encoding": "identity"}
out = {}
for tk in sys.argv[2].split():
    for cls in ("stocks",):
        try:
            j = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://api.nasdaq.com/api/quote/{tk}/summary?assetclass={cls}", headers=UA), timeout=20).read())
            sd = (j.get("data") or {}).get("summaryData") or {}
            out[tk] = {k: (v or {}).get("value") for k, v in sd.items() if k in ("MarketCap", "PreviousClose", "Exchange", "ShareVolume")}
            out[tk]["status"] = (j.get("status") or {}).get("rCode")
        except Exception as e:
            out[tk] = {"error": str(e)}
        time.sleep(0.3)
json.dump(out, open(sys.argv[1] + "/mcap_now.json", "w"), indent=1)
print(sum(1 for v in out.values() if v.get("MarketCap")), "of", len(out))
