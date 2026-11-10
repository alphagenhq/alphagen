"""Scottsdale deal scan: every 2026 8-K/6-K press release naming a repeat placement agent,
with deal-level gross proceeds and the issuer's market cap at the time of the deal.
Runs on GitHub's runners (which can reach SEC EDGAR and price data). Facts only; no AI.
Output: deals.json (one row per document) for AlphaGen's research desk."""
import json, re, sys, time, html, urllib.request, urllib.parse, datetime as dt
from html.parser import HTMLParser

OUT = sys.argv[1]
START, END = "2026-01-01", (sys.argv[2] if len(sys.argv) > 2 else dt.date.today().isoformat())
UA = {"User-Agent": "AlphaGen Research desk@alphagenresearch.com", "Accept-Encoding": "identity"}
AGENTS = {"HCW": "H.C. Wainwright", "Maxim": "Maxim Group", "AGP": "A.G.P./Alliance Global Partners", "Univest": "Univest Securities"}
LOG = []

def get(url, timeout=40, tries=3):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except Exception as e:
            err = e; time.sleep(1.5 * (i + 1))
    raise err

class _T(HTMLParser):
    def __init__(s): super().__init__(); s.out = []; s.skip = 0
    def handle_starttag(s, t, a):
        if t in ("script", "style"): s.skip += 1
        if t in ("p", "br", "div", "tr", "li", "table"): s.out.append("\n")
        if t in ("td", "th"): s.out.append(" ")
    def handle_endtag(s, t):
        if t in ("script", "style") and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)

def text_of(raw):
    try: h = raw.decode("utf-8")
    except Exception: h = raw.decode("latin-1", "ignore")
    p = _T(); p.feed(h)
    t = html.unescape("".join(p.out))
    t = re.sub(r"[ \t\r\f\v\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()

def search(agent):
    hits, frm = [], 0
    while True:
        q = urllib.parse.urlencode({"q": f'"{agent}" "gross proceeds"', "forms": "8-K,6-K",
                                    "dateRange": "custom", "startdt": START, "enddt": END, "from": frm})
        j = json.loads(get("https://efts.sec.gov/LATEST/search-index?" + q))
        hh = j.get("hits", {}).get("hits", [])
        hits += hh
        tot = j.get("hits", {}).get("total", {}).get("value", 0)
        frm += len(hh)
        time.sleep(0.2)
        if not hh or frm >= tot or frm >= 2000: return hits, tot

AMT = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*(million|billion|thousand)?", re.I)
def money(s):
    m = AMT.match(s)
    if not m: return None
    v = float(m.group(1).replace(",", ""))
    u = (m.group(2) or "").lower()
    return v * {"million": 1e6, "billion": 1e9, "thousand": 1e3}.get(u, 1)

def gross(t):
    for m in re.finditer(r"gross proceeds", t, re.I):
        seg = t[max(0, m.start() - 160): m.end() + 160]
        after = t[m.end(): m.end() + 160]
        before = t[max(0, m.start() - 160): m.start()]
        for part in (after, before):
            mm = AMT.search(part)
            if mm:
                v = money(part[mm.start():])
                if v and v >= 50000: return v, seg.replace("\n", " ")
    return None, ""

def kind(t):
    low = t[:4000].lower()
    if re.search(r"induce|reduced exercise price|exercise of (certain )?(existing|outstanding) warrants|warrant exercise", low): return "inducement"
    if "registered direct" in low: return "registered direct"
    if re.search(r"private placement|pipe", low): return "private placement"
    if re.search(r"public offering|underwritten", low): return "public offering"
    return "other"

def closed(t):
    low = t[:1500].lower()
    return bool(re.search(r"announce[sd]? (the )?(closing|clos(e|ed))|has closed|completed (the|its)|closing of (its|the|a)", low))

PX = {}
def prices(tk):
    if tk in PX: return PX[tk]
    p1 = int(dt.datetime(2025, 12, 1).timestamp()); p2 = int(time.time()) + 86400
    try:
        j = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(tk)}?period1={p1}&period2={p2}&interval=1d&events=split", timeout=25))
        r = j["chart"]["result"][0]
        ts = r.get("timestamp") or []
        cl = r["indicators"]["quote"][0].get("close") or []
        days = [(dt.datetime.utcfromtimestamp(a).date().isoformat(), c) for a, c in zip(ts, cl) if c is not None]
        sp = [(dt.datetime.utcfromtimestamp(int(k)).date().isoformat(), v["numerator"] / v["denominator"]) for k, v in (r.get("events", {}).get("splits") or {}).items()]
        PX[tk] = (days, sp)
    except Exception as e:
        LOG.append(f"price {tk}: {e}"); PX[tk] = ([], [])
    time.sleep(0.25)
    return PX[tk]

def unadj(close, d, sp):
    f = 1.0
    for sd, ratio in sp:
        if sd > d: f *= ratio
    return close * f

def split_factor(d0, d1, sp):
    """shares at d1 = shares at d0 * factor, for splits between."""
    f = 1.0
    for sd, ratio in sp:
        if d0 < sd <= d1: f *= ratio
    return f

SH = {}
def shares(cik):
    if cik in SH: return SH[cik]
    rows = []
    try:
        j = json.loads(get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json"))
        fact = j.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
        by = {}
        for u in fact.get("units", {}).get("shares", []):
            d = by.setdefault(u["end"], {})
            d[u.get("accn")] = d.get(u.get("accn"), 0) + u["val"]
        rows = sorted((e, max(v.values())) for e, v in by.items())
    except Exception as e:
        LOG.append(f"shares {cik}: {e}")
    time.sleep(0.15)
    SH[cik] = rows
    return rows

def mcap_at(cik, tk, d):
    days, sp = prices(tk) if tk else ([], [])
    prev = [x for x in days if x[0] < d]
    if not prev: return None
    pd_, pc = prev[-1]
    px = unadj(pc, pd_, sp)
    rows = shares(cik)
    if not rows: return {"price": round(px, 4), "price_date": pd_}
    before = [r for r in rows if r[0] <= d]
    e, n = before[-1] if before else rows[0]
    n_adj = n * split_factor(e, d, sp) if e <= d else n / split_factor(d, e, sp)
    return {"price": round(px, 4), "price_date": pd_, "shares": int(n_adj), "shares_asof": e, "mcap": round(px * n_adj)}

def after(tk, d):
    days, sp = prices(tk) if tk else ([], [])
    if not days: return {}
    prev = [x for x in days if x[0] < d]; nxt = [x for x in days if x[0] >= d]
    o = {"last_date": days[-1][0], "last_close": round(days[-1][1], 4), "splits_2026": [s for s in sp if s[0] >= "2026-01-01"]}
    if prev and nxt:
        o["day0_date"] = nxt[0][0]; o["day0_pct"] = round((nxt[0][1] / prev[-1][1] - 1) * 100, 1)
        o["since_pct"] = round((days[-1][1] / prev[-1][1] - 1) * 100, 1)
    return o

def main():
    rows, seen = [], set()
    for code, agent in AGENTS.items():
        hits, tot = search(agent)
        LOG.append(f"{code}: {tot} hits, {len(hits)} fetched")
        for h in hits:
            s = h["_source"]; adsh, fn = h["_id"].split(":", 1)
            ft = (s.get("file_type") or "").upper()
            if not (ft.startswith("EX-99") or ft in ("8-K", "6-K")): continue
            key = (adsh, fn, code)
            if key in seen: continue
            seen.add(key)
            cik = s["ciks"][0]
            name = (s.get("display_names") or [""])[0]
            m = re.search(r"\(([A-Z0-9.\-, ]+)\)\s+\(CIK", name)
            tk = m.group(1).split(",")[0].strip() if m else ""
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{fn}"
            try: t = text_of(get(url))
            except Exception as e: LOG.append(f"doc {url}: {e}"); continue
            time.sleep(0.12)
            if agent.lower() not in t.lower(): continue
            g, ctx = gross(t)
            rows.append({"agent": code, "cik": cik, "issuer": re.sub(r"\s+\(.*", "", name).strip(), "ticker": tk,
                         "date": s.get("file_date"), "form": s.get("form"), "url": url, "kind": kind(t), "closed": closed(t),
                         "gross": g, "gross_ctx": ctx[:330], "headline": t[:260].replace("\n", " ")})
    for r in rows:
        r["at_deal"] = mcap_at(r["cik"], r["ticker"], r["date"]) if r["ticker"] else None
        r["after"] = after(r["ticker"], r["date"]) if r["ticker"] else {}
    json.dump({"generated": dt.datetime.utcnow().isoformat() + "Z", "range": [START, END], "log": LOG, "rows": rows},
              open(f"{OUT}/deals.json", "w"), indent=1)
    print("\n".join(LOG[-40:])); print(len(rows), "rows")

main()
