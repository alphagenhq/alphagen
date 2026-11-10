"""AlphaGen source feeds: runs on GitHub's runners (which can reach official sites) and
saves primary-source documents to sources.json on the data branch, so the hourly Claude
desk can read and cite them even when it cannot open those sites itself.
Facts only: titles, links, timestamps and the source's own text. No AI, no analysis."""
import json, os, re, sys, html, urllib.request, datetime as dt
from xml.etree import ElementTree as ET
from html.parser import HTMLParser

OUT = sys.argv[1]
UA = {"User-Agent": "AlphaGen Research desk@alphagenresearch.com", "Accept-Encoding": "identity", "Accept": "*/*"}
NOW = dt.datetime.now(dt.timezone.utc)
KEEP_H = 48
TEXT_CAP = 12000
LOG = []

def get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

class _T(HTMLParser):
    def __init__(s): super().__init__(); s.out = []; s.skip = 0
    def handle_starttag(s, t, a):
        if t in ("script", "style", "noscript", "nav", "header", "footer", "svg"): s.skip += 1
        if t in ("p", "br", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"): s.out.append("\n")
        if t in ("td", "th"): s.out.append(" | ")
    def handle_endtag(s, t):
        if t in ("script", "style", "noscript", "nav", "header", "footer", "svg") and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)

def text_of(raw):
    try: h = raw.decode("utf-8")
    except Exception: h = raw.decode("latin-1", "ignore")
    p = _T(); p.feed(h)
    t = html.unescape("".join(p.out))
    t = re.sub(r"[ \t\r\f\v\xa0]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()[:TEXT_CAP]

def parse_time(s):
    if not s: return None
    s = s.strip()
    for f in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M %z"):
        try:
            d = dt.datetime.strptime(s, f)
            return (d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)
        except Exception: pass
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return (d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc)
    except Exception: return None

def rss(url):
    root = ET.fromstring(get(url))
    out = []
    for it in root.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"): continue
        f = {c.tag.split("}")[-1]: c for c in it}
        title = (f.get("title").text or "").strip() if f.get("title") is not None else ""
        link = ""
        if f.get("link") is not None:
            link = (f["link"].text or f["link"].get("href") or "").strip()
        when = None
        for k in ("pubDate", "published", "updated", "date"):
            if f.get(k) is not None and f[k].text: when = parse_time(f[k].text); break
        if title and link: out.append((title, link, when))
    return out

# Official feeds. Each item's own page text is fetched so figures can be read and cited.
FEEDS = [
    ("BLS", "MACRO", "https://www.bls.gov/feed/bls_latest.rss"),
    ("BEA", "MACRO", "https://apps.bea.gov/rss/rss.xml"),
    ("Federal Reserve", "FED", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("Federal Reserve speeches", "FED", "https://www.federalreserve.gov/feeds/speeches.xml"),
    ("EIA", "ENERGY", "https://www.eia.gov/rss/press_rss.xml"),
    ("EIA Today in Energy", "ENERGY", "https://www.eia.gov/rss/todayinenergy.xml"),
    ("Census", "MACRO", "https://www.census.gov/economic-indicators/indicator.xml"),
    ("ECB", "GLOBAL", "https://www.ecb.europa.eu/rss/press.html"),
    ("Bank of England", "GLOBAL", "https://www.bankofengland.co.uk/rss/news"),
    ("Bank of Canada", "GLOBAL", "https://www.bankofcanada.ca/content_type/press-releases/feed/"),
    ("CFTC", "COMMODITIES", "https://www.cftc.gov/RSS/RSSGP/rssgp.xml"),
]

try: cur = json.load(open(os.path.join(OUT, "sources.json")))
except Exception: cur = {"items": []}
have = {i["id"]: i for i in cur.get("items", [])}
cut = NOW - dt.timedelta(hours=KEEP_H)
new = []

def add(item):
    if item["id"] in have: return
    have[item["id"]] = item; new.append(item)

for name, tag, url in FEEDS:
    try:
        n = 0; undated = 0
        for title, link, when in rss(url)[:15]:
            if when and when < cut: continue
            if not when:
                undated += 1
                if undated > 3: continue
            iid = "src-" + re.sub(r"[^a-z0-9]+", "-", (name + "-" + link).lower())[-110:]
            if iid in have: continue
            try: body = text_of(get(link))
            except Exception as e: body = ""
            add({"id": iid, "source": name, "tag": tag, "title": title, "url": link,
                 "published": when.strftime("%Y-%m-%dT%H:%M:%SZ") if when else None,
                 "fetched": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "text": body,
                 **({} if when else {"note": "This feed gives no date. Confirm the release date in the text; it may be an older release."})})
            n += 1
        LOG.append(f"{name}: +{n}")
    except Exception as e:
        LOG.append(f"{name}: ERROR {type(e).__name__}")

# Key official release pages, refreshed every run (always the latest edition).
PAGES = [
    ("bls-cpi", "BLS", "MACRO", "Consumer Price Index news release (latest)", "https://www.bls.gov/news.release/cpi.nr0.htm"),
    ("bls-jobs", "BLS", "MACRO", "Employment Situation news release (latest)", "https://www.bls.gov/news.release/empsit.nr0.htm"),
    ("bls-ppi", "BLS", "MACRO", "Producer Price Index news release (latest)", "https://www.bls.gov/news.release/ppi.nr0.htm"),
    ("bls-realearn", "BLS", "MACRO", "Real Earnings news release (latest)", "https://www.bls.gov/news.release/realer.nr0.htm"),
    ("dol-claims", "U.S. Department of Labor", "MACRO", "Unemployment Insurance Weekly Claims (latest)", "https://www.dol.gov/ui/data.pdf"),
]
for pid, src, tag, title, url in PAGES:
    if url.endswith(".pdf"): continue
    try:
        body = text_of(get(url))
        if body:
            have[pid] = {"id": pid, "source": src, "tag": tag, "title": title, "url": url, "published": None,
                         "fetched": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "text": body, "note": "Latest edition of this release. Check the release date in the text."}
            LOG.append(f"{pid}: ok")
    except Exception as e:
        LOG.append(f"{pid}: ERROR {type(e).__name__}")

# SEC 8-Ks from the watchlist: earnings (2.02), agreements (1.01), completed deals (2.01).
try:
    WATCH = set(open(os.path.join(os.path.dirname(__file__), "watchlist.txt")).read().split())
    tick = {}
    for row in json.loads(get("https://www.sec.gov/files/company_tickers_exchange.json"))["data"]:
        cik, nm, t, ex = row
        if t and t.upper() in WATCH and str(cik) not in tick:
            tick[str(cik)] = (t.upper(), {"Nasdaq": "NASDAQ", "NYSE": "NYSE", "CBOE": "CBOE"}.get(ex or "", "NYSE"), nm)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    feed = ET.fromstring(get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&start=0&count=100&output=atom"))
    n = 0
    for e in feed.findall("a:entry", ns):
        title = e.findtext("a:title", "", ns)
        m = re.match(r"8-K - (.+?) \((\d{10})\) \(Filer\)", title)
        if not m: continue
        cik = str(int(m.group(2)))
        if cik not in tick: continue
        summ = html.unescape(e.findtext("a:summary", "", ns))
        items = [i for i in re.findall(r"Item (\d\.\d\d)", summ) if i in ("2.02", "1.01", "2.01", "5.02", "7.01", "8.01")]
        if not items: continue
        link = e.find("a:link", ns).get("href")
        acc = re.search(r"(\d{10}-\d{2}-\d{6})", link)
        if not acc: continue
        iid = "sec-" + acc.group(1)
        if iid in have: continue
        when = parse_time(e.findtext("a:updated", "", ns)) or NOW
        t, ex, nm = tick[cik]
        base = link.rsplit("/", 1)[0]
        body, doc = "", link
        try:
            idx = json.loads(get(base + "/index.json"))["directory"]["item"]
            names = [x["name"] for x in idx if x["name"].lower().endswith((".htm", ".html", ".txt"))]
            pick = [x for x in names if re.search(r"ex-?99|ex99|dex99", x, re.I)] or [x for x in names if "index" not in x.lower()]
            if pick:
                doc = base + "/" + pick[0]
                body = text_of(get(doc))
        except Exception: pass
        add({"id": iid, "source": f"SEC EDGAR, {t} Form 8-K", "tag": "EARNINGS" if "2.02" in items else "DEALS" if ("1.01" in items or "2.01" in items) else "EQUITIES",
             "title": f"{nm}: Form 8-K, Item {', '.join(items)}", "url": doc, "filing_index": link, "ticker": f"{ex}:{t}",
             "published": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "fetched": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "text": body})
        n += 1
    LOG.append(f"SEC 8-K: +{n}")
except Exception as e:
    LOG.append(f"SEC 8-K: ERROR {type(e).__name__}")

# Treasury auction results (fiscaldata API, the official record).
try:
    q = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?sort=-auction_date&page[size]=20"
    rows = json.loads(get(q.replace("[", "%5B").replace("]", "%5D")))["data"]
    keep = ("auction_date", "issue_date", "security_type", "security_term", "cusip", "high_yield", "high_investment_rate", "high_discount_rate", "bid_to_cover_ratio", "offering_amt", "indirect_bidder_accepted", "direct_bidder_accepted", "primary_dealer_accepted", "total_accepted")
    done = [{k: r.get(k) for k in keep} for r in rows if r.get("bid_to_cover_ratio") not in (None, "", "null")]
    cur_rows = {"id": "treasury-auctions", "source": "U.S. Treasury, Fiscal Data auctions", "tag": "DEBT",
                "title": "Latest Treasury auction results", "url": "https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/",
                "published": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "fetched": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "text": json.dumps(done[:8])}
    have["treasury-auctions"] = cur_rows
    LOG.append(f"Treasury auctions: {len(done[:8])} results")
except Exception as e:
    LOG.append(f"Treasury auctions: ERROR {type(e).__name__}")

# FRED daily/weekly series: latest observations (official St. Louis Fed data).
SERIES = ["DGS2", "DGS10", "DGS30", "T10Y2Y", "DFII10", "T10YIE", "SOFR", "DCOILBRENTEU", "DCOILWTICO", "DHHNGSP",
          "BAMLH0A0HYM2", "BAMLC0A0CM", "MORTGAGE30US", "DEXUSEU", "DEXJPUS", "ICSA", "WALCL", "RRPONTSYD"]
fred = {}
for s in SERIES:
    try:
        lines = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}").decode().strip().splitlines()[1:]
        obs = [l.split(",") for l in lines if l.split(",")[-1] not in (".", "")][-6:]
        fred[s] = {"url": f"https://fred.stlouisfed.org/series/{s}", "obs": obs}
    except Exception: pass
if fred:
    have["fred-latest"] = {"id": "fred-latest", "source": "FRED, Federal Reserve Bank of St. Louis", "tag": "RATES",
                           "title": "Latest FRED observations (date, value)", "url": "https://fred.stlouisfed.org/",
                           "published": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "fetched": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "text": json.dumps(fred)}
LOG.append(f"FRED: {len(fred)} series")

items = [i for i in have.values() if i["id"] in ("treasury-auctions", "fred-latest", "bls-cpi", "bls-jobs", "bls-ppi", "bls-realearn") or (parse_time(i.get("published") or i.get("fetched")) or NOW) >= cut]
items.sort(key=lambda i: i.get("published") or "0", reverse=True)
items = items[:220]
json.dump({"updated": NOW.strftime("%Y-%m-%dT%H:%M:%SZ"), "log": LOG, "items": items}, open(os.path.join(OUT, "sources.json"), "w"), indent=1)
print(" | ".join(LOG), f"| new {len(new)} | total {len(items)}")
