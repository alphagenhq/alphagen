"""AlphaGen live filings: polls SEC EDGAR's real-time 8-K feed and writes live.json.
Facts only (company, filing type, item, time, link). No AI, no analysis."""
import json, os, re, sys, urllib.request, datetime as dt, html
from zoneinfo import ZoneInfo
FIX = {"Jpmorgan": "JPMorgan", "At&T": "AT&T", "Ibm": "IBM", "Amd": "AMD", "Rtx": "RTX", "Ge": "GE", "Hp": "HP", "Ups": "UPS", "Cvs": "CVS", "Csx": "CSX", "Pnc": "PNC", "Us": "U.S.", "Nvidia": "NVIDIA", "Paypal": "PayPal", "Mcdonald's": "McDonald's", "Exxonmobil": "ExxonMobil", "Blackrock": "BlackRock", "Spacex": "SpaceX", "Dupont": "DuPont", "Mcdonalds": "McDonald's"}
def nice(name):
    name = re.sub(r"\s*/[A-Z]{2}/?$", "", name).strip().rstrip(".")
    name = re.sub(r",?\s+(INC|CORP|CORPORATION|CO|LTD|PLC|LLC|N\.V|S\.A|HOLDINGS INC|COMPANY)\.?$", "", name, flags=re.I).strip()
    name = re.sub(r"\s*&$", "", name).strip()
    return " ".join(w.lower() if w.lower() in ("of","and","the") and i else FIX.get(w.title(), w if "&" in w or re.search(r"\d", w) else w.title()) for i, w in enumerate(name.split()))
from xml.etree import ElementTree as ET
UA = {"User-Agent": "AlphaGen Research desk@alphagenresearch.com", "Accept-Encoding": "identity"}
OUT = sys.argv[1]
WATCH = set(open(os.path.join(os.path.dirname(__file__), "watchlist.txt")).read().split())
ITEMS = {
  "2.02": ("EARNINGS", "{n} releases financial results", "{n} filed its results announcement with the SEC (Form 8-K, Item 2.02)."),
  "1.01": ("DEALS", "{n} discloses a material agreement", "{n} reported entering a material definitive agreement in an SEC filing (Form 8-K, Item 1.01)."),
  "2.01": ("DEALS", "{n} completes an acquisition or sale of assets", "{n} reported completing an acquisition or disposition of assets in an SEC filing (Form 8-K, Item 2.01)."),
  "5.02": ("EQUITIES", "{n} reports an executive or board change", "{n} reported a change among its officers or directors in an SEC filing (Form 8-K, Item 5.02)."),
  "8.01": None,
}
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
tick = {}
for row in json.loads(get("https://www.sec.gov/files/company_tickers_exchange.json"))["data"]:
    cik, name, t, ex = row
    if t and t.upper() in WATCH and str(cik) not in tick:
        exch = {"Nasdaq": "NASDAQ", "NYSE": "NYSE", "CBOE": "CBOE"}.get(ex or "", "NYSE")
        tick[str(cik)] = (t.upper(), exch)
ns = {"a": "http://www.w3.org/2005/Atom"}
feed = ET.fromstring(get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&start=0&count=100&output=atom"))
try: cur = json.load(open(os.path.join(OUT, "live.json")))
except Exception: cur = {"items": []}
have = {i["id"] for i in cur["items"]}
new = []
for e in feed.findall("a:entry", ns):
    title = e.findtext("a:title", "", ns)
    m = re.match(r"8-K(?:/A)? - (.+?) \((\d{10})\) \(Filer\)", title)
    if not m or title.startswith("8-K/A"): continue
    name, cik = m.group(1), str(int(m.group(2)))
    if cik not in tick: continue
    t, ex = tick[cik]
    summ = html.unescape(e.findtext("a:summary", "", ns))
    link = e.find("a:link", ns).get("href")
    acc = re.search(r"AccNo:</b>\s*([\d-]+)", summ) or re.search(r"(\d{10}-\d{2}-\d{6})", link)
    when = e.findtext("a:updated", "", ns)
    try: ts = dt.datetime.fromisoformat(when).astimezone(dt.timezone.utc)
    except Exception: continue
    pretty = nice(name)
    for item in re.findall(r"Item (\d\.\d\d)", summ):
        spec = ITEMS.get(item)
        if not spec: continue
        iid = f"live-{acc.group(1) if acc else cik}-{item}"
        if iid in have: continue
        tag, h, take = spec
        et = ts.astimezone(ZoneInfo("America/New_York")).strftime("%-I:%M %p ET, %b %-d")
        new.append({"id": iid, "time": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "tag": tag, "live": True,
                    "headline": h.format(n=pretty), "take": take.format(n=pretty) + f" Filed {et}. AlphaGen's breakdown follows on the Wire.",
                    "source_name": f"SEC EDGAR, {t} Form 8-K", "source_url": link, "ticker": f"{ex}:{t}"})
        have.add(iid)
if new:
    items = sorted(new + cur["items"], key=lambda i: i["time"], reverse=True)[:300]
    json.dump({"updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items}, open(os.path.join(OUT, "live.json"), "w"), indent=1)
print(f"watchlist ciks {len(tick)}, new {len(new)}")
