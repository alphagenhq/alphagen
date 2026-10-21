"""Cache FRED series as CSV in fred/ so the site never depends on a live FRED call."""
import json, os, time, urllib.request
BASE = ["BAMLC0A0CM","BAMLC0A4CBBB","BAMLH0A0HYM2","BAMLH0A1HYBB","BAMLH0A3HYC","CBBTCUSD","CBETHUSD","CPIAUCSL","CPILFESL","CSUSHPINSA","DCOILBRENTEU","DCOILWTICO","DEXCHUS","DEXJPUS","DEXUSEU","DEXUSUK","DFEDTARL","DFEDTARU","DFF","DFII10","DGS10","DGS2","DGS30","DGS3MO","DHHNGSP","DRTSCILM","DTWEXBGS","ECBDFR","EXHOSLUSM495S","GASREGW","GDPNOW","HOUST","ICSA","INDPRO","IRLTLT01DEM156N","IRLTLT01GBM156N","IRLTLT01JPM156N","MORTGAGE30US","MSACSR","NFCI","PALUMUSDM","PAYEMS","PCEPILFE","PCOPPUSDM","PERMIT","PMAIZMTUSDM","PWHEAMTUSDM","RRPONTSYD","RSAFS","SOFR","T10Y2Y","T10YIE","T5YIE","UNRATE","VIXCLS","WALCL","WRESBAL","WTREGEN"]
ids = set(BASE)
try:
    for c in json.load(open("charts.json")).get("items", [])[:60]:
        for s in c.get("series", []):
            if s.get("id"): ids.add(s["id"])
except Exception as e:
    print("charts.json skipped:", e)
os.makedirs("fred", exist_ok=True)
ok = bad = 0
for sid in sorted(ids):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=2000-01-01"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AlphaGen Research desk@alphagenresearch.com"})
            body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
            if body.lstrip().startswith("<") or "," not in body: raise ValueError("not csv")
            open(f"fred/{sid}.csv", "w").write(body); ok += 1; break
        except Exception as e:
            if attempt == 2: print("FAIL", sid, e); bad += 1
            else: time.sleep(5)
    time.sleep(0.5)
print(f"cached {ok}, failed {bad}")
