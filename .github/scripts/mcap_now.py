"""Latest SEC-reported shares outstanding and 2026 daily price history (split-adjusted, with split events)
for each issuer, so the desk can bound market cap at the time of each deal. Facts only."""
import json, sys, time, urllib.request, datetime as dt
UA = {"User-Agent": "AlphaGen Research desk@alphagenresearch.com", "Accept-Encoding": "identity"}
def get(u, t=25):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read())
out = {}
p1 = int(dt.datetime(2025, 12, 1).timestamp()); p2 = int(time.time()) + 86400
for pair in sys.argv[2].split():
    cik, tk = pair.split(":")
    o = {"cik": cik}
    try:
        f = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json")
        by = {}
        for u in f.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", []):
            k = (u["end"], u.get("accn")); by[k] = by.get(k, 0) + u["val"]
        if by:
            (e, a), v = max(by.items(), key=lambda kv: (kv[0][0], kv[1]))
            o["shares"] = v; o["shares_asof"] = e; o["accn"] = a
    except Exception as ex: o["shares_err"] = str(ex)[:80]
    time.sleep(0.15)
    try:
        r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}?period1={p1}&period2={p2}&interval=1d&events=split")["chart"]["result"][0]
        ts = r.get("timestamp") or []; cl = r["indicators"]["quote"][0].get("close") or []
        o["px"] = [[dt.datetime.utcfromtimestamp(a).date().isoformat(), round(c, 6)] for a, c in zip(ts, cl) if c is not None]
        o["splits"] = [[dt.datetime.utcfromtimestamp(int(k)).date().isoformat(), v["numerator"], v["denominator"]] for k, v in (r.get("events", {}).get("splits") or {}).items()]
        o["currency"] = r.get("meta", {}).get("currency")
    except Exception as ex: o["px_err"] = str(ex)[:80]
    time.sleep(0.25)
    out[tk] = o
json.dump(out, open(sys.argv[1] + "/mcap_now.json", "w"))
print(sum(1 for v in out.values() if v.get("shares") and v.get("px")), "complete of", len(out))
