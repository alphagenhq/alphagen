#!/usr/bin/env python3
"""AlphaGen site generator.
Builds every page from shared templates plus the JSON data files, including static
pages for each note, chart, and covered stock, and branded share images (og/*.png).
Run from anywhere:  python3 _build/build.py
"""
import os, json, html, re, datetime, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "_build", "fonts")
E = html.escape
SITE = "https://alphagenresearch.com"
V = "6"  # asset version

def load(name):
    try:
        with open(os.path.join(ROOT, name)) as f:
            return json.load(f)
    except Exception:
        return {"items": []}

NOW = datetime.datetime.now(datetime.timezone.utc)
def is_live(item):
    t = item.get("time")
    if not t: return True
    try: return datetime.datetime.fromisoformat(t.replace("Z", "+00:00")) <= NOW
    except Exception: return True

def nice_date(iso):
    try:
        d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")) - datetime.timedelta(hours=4)
        return d.strftime("%b %-d, %Y")
    except Exception: return ""

def slug_ok(s): return bool(re.fullmatch(r"[A-Za-z0-9._-]{1,120}", s or ""))

X_ICON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.68l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64z"/></svg>'
LI_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'
X_URL = "https://x.com/alphageniq"
LI_URL = "https://www.linkedin.com/company/alphagen-research"
SUB_URL = "https://alphagen-newsletter.beehiiv.com/subscribe"

NAV = [
    ("wire", "/wire", "Wire", None),
    ("markets", None, "Markets", [("equities", "/equities", "Equities & movers", "Big movers with AlphaGen's thesis"),
                                  ("earnings", "/earnings", "Earnings scorecard", "Reported results from filings"),
                                  ("deals", "/deals", "Deals & private markets", "M&A, venture, PE, IPOs, live SEC filings"),
                                  ("stocks", "/stocks", "Stock coverage", "Every company we cover")]),
    ("rates-g", None, "Rates & Credit", [("rates", "/rates", "Rates & debt", "Yield curve, debt, Fed calendar"),
                                ("fed", "/fed", "Fed Watch", "Policy rate, balance sheet, liquidity"),
                                ("auctions", "/auctions", "Treasury auctions", "Results, demand, and the calendar"),
                                ("credit", "/credit", "Credit", "Spreads, lending, conditions")]),
    ("macro-g", None, "Macro", [("dashboard", "/dashboard", "Macro dashboard", "20 indicators with live signals"),
                                ("macro", "/macro", "Calendar & macro wire", "Releases and the macro tape"),
                                ("global", "/global", "Global markets", "Central banks, yields, FX"),
                                ("housing", "/housing", "Housing & real estate", "Mortgages, starts, prices")]),
    ("assets-g", None, "Assets", [("commodities", "/commodities", "Commodities & energy", "Oil, gas, metals, grains"),
                                ("crypto", "/crypto", "Crypto", "Bitcoin, ether, digital assets")]),
    ("charts", "/charts", "Charts", None),
    ("research", "/research", "Research", None),
]

TAPE = ",".join(["FOREXCOM:SPXUSD", "FOREXCOM:NSXUSD", "FOREXCOM:DJI", "AMEX:IWM", "NASDAQ:NVDA", "NASDAQ:AAPL",
                 "NASDAQ:MSFT", "NASDAQ:TLT", "AMEX:HYG", "AMEX:GLD", "AMEX:USO", "FX:EURUSD", "FX:USDJPY", "BITSTAMP:BTCUSD"])

def head(title, desc, path, og="/og/default.png", kind="website"):
    full = "AlphaGen Research" if title is None else f"{title} | AlphaGen Research"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#07121f">
<link rel="icon" type="image/png" href="/logo-192.png">
<link rel="apple-touch-icon" href="/logo-192.png">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="AlphaGen Research">
<meta property="og:title" content="{E(full if title is None else title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@alphageniq">
<meta name="twitter:image" content="{SITE}{og}">
<link rel="alternate" type="application/rss+xml" title="AlphaGen Research" href="/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500;62..125,600;62..125,700;62..125,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/ag.css?v={V}">
</head>
<body>
'''

def header(active):
    cur = ' aria-current="page"'
    parts = []
    for key, href, label, sub in NAV:
        if sub:
            on = any(k == active for k, *_ in sub)
            items = "".join(f'<a href="{h}"{cur if k == active else ""}>{n}<small>{d}</small></a>' for k, h, n, d in sub)
            parts.append(f'<div class="dd{" cur" if on else ""}"><button type="button">{label}</button><div class="dd-menu">{items}</div></div>')
        else:
            parts.append(f'<a class="txt" href="{href}"{cur if key == active else ""}>{label}</a>')
    return f'''<div class="statusbar"><div class="wrap"><span class="mkt" id="mkt"><i></i><b>NYSE</b></span><div class="crawl" id="crawl" aria-live="off"></div><span class="clock" id="clock"></span></div></div>
<header class="mast">
  <div class="wrap">
    <a class="logo" href="/"><img class="mark" src="/logo-192.png" alt="" width="34" height="34">Alpha<span>Gen</span></a>
    <nav class="nav" aria-label="Main">
      <div class="links">{"".join(parts)}</div>
      <a class="search-ico" href="/search" aria-label="Search AlphaGen"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></a>
      <a class="ico" href="{X_URL}" target="_blank" rel="noopener" aria-label="AlphaGen on X">{X_ICON}</a>
      <a class="ico" href="{LI_URL}" target="_blank" rel="noopener" aria-label="AlphaGen on LinkedIn">{LI_ICON}</a>
      <button class="btn sm" type="button" data-open-sub>Subscribe</button>
      <button class="menu-btn" type="button" aria-label="Menu" aria-expanded="false">☰</button>
    </nav>
  </div>
</header>
<div class="tape"><tv-ticker-tape symbols="{TAPE}" theme="dark" transparent show-hover></tv-ticker-tape></div>
'''

SLIP = f'''<section>
  <div class="wrap">
    <div class="slip">
      <div>
        <div class="eyebrow">The AlphaGen Newsletter</div>
        <h2 class="sec">Get the thesis before the open.</h2>
        <p>Free. Rates, liquidity, and earnings signals in one focused read.</p>
        <div class="subform"><a class="btn" data-sub-go href="{SUB_URL}" target="_blank" rel="noopener">Subscribe free →</a></div>
        <div class="fine">No spam. Unsubscribe anytime.</div>
      </div>
      <ul>
        <li>The AlphaGen thesis on debt, equities, and macro</li>
        <li>Funding-market and liquidity signals, explained</li>
        <li>Institutional-grade analysis in plain English</li>
      </ul>
    </div>
  </div>
</section>
'''

def footer(extra=""):
    def col(title, links): return f'<div><h4>{title}</h4><ul>' + "".join(f'<li><a href="{h}">{n}</a></li>' for h, n in links) + '</ul></div>'
    return f'''<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="logo" style="font-size:1.1rem"><img class="mark" src="/logo-192.png" alt="" width="30" height="30">Alpha<span>Gen</span></div>
        <p class="disc">Independent markets research on debt, equities, and macro, built from official data. For informational purposes only; not investment advice. See <a href="/disclosures" style="color:inherit">disclosures</a>.</p>
        <div class="social"><a href="{X_URL}" target="_blank" rel="noopener">{X_ICON}<span>X</span></a><a href="{LI_URL}" target="_blank" rel="noopener">{LI_ICON}<span>LinkedIn</span></a><a href="/rss.xml">RSS</a></div>
      </div>
      {col("Markets", [("/wire","The Wire"),("/equities","Equities & movers"),("/earnings","Earnings scorecard"),("/deals","Deals & private markets"),("/stocks","Stock coverage"),("/commodities","Commodities & energy"),("/crypto","Crypto")])}
      {col("Rates & macro", [("/rates","Rates & debt"),("/fed","Fed Watch"),("/auctions","Treasury auctions"),("/credit","Credit"),("/dashboard","Macro dashboard"),("/global","Global markets"),("/housing","Housing"),("/charts","Charts")])}
      {col("AlphaGen", [("/research","Research"),("/search","Search"),("/about","About"),("/methodology","Methodology"),("/standards","Editorial standards"),("/disclosures","Disclosures"),("/privacy","Privacy"),("/terms","Terms")])}
    </div>
    <div class="copy">© 2026 AlphaGen Research. Market data by TradingView and may be delayed. Economic data from FRED (Federal Reserve Bank of St. Louis), the U.S. Treasury, and the agencies cited.</div>
  </div>
</footer>
<div class="modal" id="sub-modal" role="dialog" aria-modal="true" aria-labelledby="sub-title" hidden>
  <div class="modal-card">
    <button class="x" type="button" data-close-sub aria-label="Close">×</button>
    <img class="mark" src="/logo-192.png" alt="" width="52" height="52">
    <div class="eyebrow">Free · The AlphaGen Newsletter</div>
    <h2 id="sub-title">Get the AlphaGen thesis before the open.</h2>
    <p>Our read on debt, equities, and macro, straight to your inbox.</p>
    <ul class="perks"><li>The AlphaGen thesis on what moves markets</li><li>Treasury, Fed, and earnings signals</li><li>Free. Unsubscribe anytime.</li></ul>
    <div class="subform"><a class="btn" style="flex:1 1 auto;padding:14px 18px;font-size:1rem" data-sub-go href="{SUB_URL}" target="_blank" rel="noopener">Subscribe →</a></div>
    <button class="later" type="button" data-close-sub>No thanks, maybe later</button>
  </div>
</div>
<script src="/assets/ag.js?v={V}"></script>
<script src="/assets/ag-data.js?v={V}"></script>
{extra}
</body>
</html>
'''

def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: f.write(content)

def page(rel, path, title, desc, active, body, js="", og="/og/default.png", kind="website", slip=True, ld=None):
    h = head(title, desc, path, og, kind)
    if ld: h = h.replace("</head>", '<script type="application/ld+json">' + json.dumps(ld).replace("</", "<\\/") + "</script>\n</head>")
    write(rel, h + header(active) + '<main id="top">\n' + body + '\n</main>\n' + (SLIP if slip else "") + footer(f"<script>\n{js}\n</script>" if js else ""))

# ---------- shared blocks ----------
def wire_card(view_id, limit, tags="", title="Live wire", height=None, ticker=""):
    style = f' style="max-height:{height}px"' if height else ""
    tk = f' data-ticker="{E(ticker)}"' if ticker else ""
    return f'''<div class="card wire"><div class="wire-head"><span class="live">{title}</span><span data-wire-updated>Updating</span></div><div class="wire-list" id="{view_id}" data-wire data-limit="{limit}" data-tags="{tags}"{tk}{style}></div></div>'''

def minis(symbols):
    return '<div class="minis">' + "".join(f'<div class="card"><tv-mini-chart symbol="{s}" theme="dark" transparent></tv-mini-chart></div>' for s in symbols) + '</div>'

def tvbox(id_, h, ph):
    return f'<div class="tv"><div class="tradingview-widget-container" id="{id_}"><div class="tradingview-widget-container__widget" style="min-height:{h}px" data-ph="{ph}"></div></div></div>'

def sec_head(eyebrow, title, right=""):
    return f'<div class="sec-head"><div><div class="eyebrow">{eyebrow}</div><h2 class="sec">{title}</h2></div>{right}</div>'

def phead(eyebrow, title, desc):
    return f'<div class="wrap phead"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{desc}</p></div>'

LEVELS = '''<div class="levels" id="levels" aria-label="Key Treasury levels">
  <div class="lvl"><div class="k">3M bill</div><div class="v num" id="lv-3m">4.26%</div><div class="d num" id="lv-3m-d">&nbsp;</div></div>
  <div class="lvl"><div class="k">2Y note</div><div class="v num" id="lv-2y">4.79%</div><div class="d num" id="lv-2y-d">&nbsp;</div></div>
  <div class="lvl"><div class="k">10Y note</div><div class="v num" id="lv-10y">5.21%</div><div class="d num" id="lv-10y-d">&nbsp;</div></div>
  <div class="lvl"><div class="k">30Y bond</div><div class="v num" id="lv-30y">5.56%</div><div class="d num" id="lv-30y-d">&nbsp;</div></div>
  <div class="lvl"><div class="k">2s10s spread</div><div class="v num" id="lv-2s10s">+42bp</div><div class="d num" id="lv-2s10s-d">&nbsp;</div></div>
  <div class="lvl"><div class="k">U.S. public debt</div><div class="v num" id="lv-debt">$40.30T</div><div class="d num" id="lv-debt-d">as of Oct 9</div></div>
</div>
<div class="levels-note" id="levels-note">U.S. Treasury par yield curve rates, close of Oct 13, 2026. Debt: Treasury, Debt to the Penny.</div>'''

DESK = '''<div class="desk">
  <div class="card curve">
    <div class="card-h"><span>U.S. Treasury yield curve</span><span id="curve-date">Oct 13, 2026</span></div>
    <div id="curve-chart" role="img" aria-label="U.S. Treasury par yield curve"></div>
    <div class="legend"><span><i></i><b id="lg-now">Oct 13, 2026</b></span><span><i class="prev"></i><span id="lg-prev">Oct 1, 2026</span></span></div>
    <div class="ytable-wrap"><table class="ytable" id="ytable"></table></div>
  </div>
  <div class="card debt">
    <div>
      <div class="eyebrow" style="color:var(--steel)">Total public debt outstanding</div>
      <div class="big num" id="debt-total">$40.30<small>trillion</small></div>
      <div class="sub" id="debt-date">As of Oct 9, 2026 · U.S. Treasury, Debt to the Penny</div>
    </div>
    <p class="ctx">With the 10-year above 5%, every refinancing locks in higher interest costs. That makes the debt a rates story as much as a fiscal one.</p>
    <div class="split">
      <div><span>Held by the public</span><b class="num" id="debt-public">$32.45T</b></div>
      <div><span>Intragovernmental</span><b class="num" id="debt-intra">$7.85T</b></div>
    </div>
  </div>
</div>'''

FOMC_CARD = '''<div class="card fed" data-fomc>
  <div class="date" data-fomc-date>Oct 27–28</div>
  <div><div class="card-h" style="margin:0 0 4px"><span>Next FOMC meeting</span></div><div style="font-family:var(--display);font-stretch:88%;font-weight:700;font-size:1.2rem">Federal Open Market Committee</div><div class="cd" data-fomc-cd>Decision Oct 28, 2026 at 2:00 p.m. ET</div></div>
</div>'''

OVERVIEW_JS = '''AG.tv("tv-overview","market-overview",{dateRange:"1D",showChart:true,width:"100%",height:540,showSymbolLogo:true,showFloatingTooltip:true,
  plotLineColorGrowing:"#4c8dff",plotLineColorFalling:"#ff6b6b",gridLineColor:"rgba(39,67,108,0.4)",scaleFontColor:"#93a7c4",
  belowLineFillColorGrowing:"rgba(76,141,255,0.14)",belowLineFillColorFalling:"rgba(255,107,107,0.10)",belowLineFillColorGrowingBottom:"rgba(76,141,255,0)",belowLineFillColorFallingBottom:"rgba(255,107,107,0)",symbolActiveColor:"rgba(76,141,255,0.12)",
  tabs:[
   {title:"Indices",symbols:[{s:"FOREXCOM:SPXUSD",d:"S&P 500"},{s:"FOREXCOM:NSXUSD",d:"Nasdaq 100"},{s:"FOREXCOM:DJI",d:"Dow 30"},{s:"AMEX:IWM",d:"Russell 2000 (IWM)"},{s:"AMEX:SPY",d:"SPDR S&P 500 (SPY)"},{s:"NASDAQ:QQQ",d:"Invesco QQQ"}]},
   {title:"Megacaps",symbols:[{s:"NASDAQ:NVDA",d:"Nvidia"},{s:"NASDAQ:MSFT",d:"Microsoft"},{s:"NASDAQ:AAPL",d:"Apple"},{s:"NASDAQ:AMZN",d:"Amazon"},{s:"NASDAQ:GOOGL",d:"Alphabet"},{s:"NASDAQ:META",d:"Meta"}]},
   {title:"Rates & Credit",symbols:[{s:"NASDAQ:SHV",d:"T-Bills (SHV)"},{s:"NASDAQ:SHY",d:"1–3Y Treasuries (SHY)"},{s:"NASDAQ:IEF",d:"7–10Y Treasuries (IEF)"},{s:"NASDAQ:TLT",d:"20Y+ Treasuries (TLT)"},{s:"NASDAQ:LQD",d:"IG Corporates (LQD)"},{s:"AMEX:HYG",d:"High Yield (HYG)"}]},
   {title:"Commodities",symbols:[{s:"AMEX:GLD",d:"Gold (GLD)"},{s:"AMEX:SLV",d:"Silver (SLV)"},{s:"AMEX:USO",d:"WTI Oil (USO)"},{s:"AMEX:UNG",d:"Natural Gas (UNG)"},{s:"AMEX:CPER",d:"Copper (CPER)"}]},
   {title:"FX & Crypto",symbols:[{s:"AMEX:UUP",d:"U.S. Dollar (UUP)"},{s:"FX:EURUSD",d:"EUR/USD"},{s:"FX:USDJPY",d:"USD/JPY"},{s:"FX:GBPUSD",d:"GBP/USD"},{s:"BITSTAMP:BTCUSD",d:"Bitcoin"},{s:"BITSTAMP:ETHUSD",d:"Ethereum"}]}
  ]});'''
CAL_JS = 'AG.tv("tv-calendar","events",{width:"100%",height:540,importanceFilter:"0,1",countryFilter:"us"});'
HEAT_JS = 'AG.tv("tv-heatmap","stock-heatmap",{exchanges:[],dataSource:"SPX500",grouping:"sector",blockSize:"market_cap_basic",blockColor:"change",hasTopBar:false,isDataSetEnabled:false,isZoomEnabled:true,hasSymbolTooltip:true,isMonoSize:false,width:"100%",height:560});'
HOT_JS = '''AG.tv("tv-hot","hotlists",{exchange:"US",dateRange:"1D",showChart:true,width:"100%",height:620,showSymbolLogo:true,showFloatingTooltip:true,
  plotLineColorGrowing:"#36c98b",plotLineColorFalling:"#ff6b6b",gridLineColor:"rgba(39,67,108,0.4)",scaleFontColor:"#93a7c4",
  belowLineFillColorGrowing:"rgba(54,201,139,0.14)",belowLineFillColorFalling:"rgba(255,107,107,0.10)",belowLineFillColorGrowingBottom:"rgba(54,201,139,0)",belowLineFillColorFallingBottom:"rgba(255,107,107,0)",symbolActiveColor:"rgba(76,141,255,0.12)"});'''

def wire_filters(id_, tags, search=False):
    btns = "".join(f'<button type="button" data-f="{t}" aria-pressed="false">{t.title() if t != "FX" else "FX"}</button>' for t in tags)
    s = '<label class="sr" for="wire-q">Search the Wire</label><input class="search" id="wire-q" type="search" placeholder="Search the Wire: CPI, NVDA, auction…">' if search else ""
    return f'<div class="toolbar" data-wire-filters="{id_}"><div class="filters" role="group" aria-label="Filter the Wire"><button type="button" data-f="all" aria-pressed="true">All</button>{btns}</div>{s}</div>'

def research_filters(id_):
    return f'''<div class="filters" role="group" aria-label="Filter research" data-research-filters="{id_}">
  <button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="briefs" aria-pressed="false">Briefs</button>
  <button type="button" data-f="debt" aria-pressed="false">Debt &amp; Rates</button><button type="button" data-f="equities" aria-pressed="false">Equities</button><button type="button" data-f="macro" aria-pressed="false">Macro</button></div>'''

# ---------- data ----------
wire = load("wire.json"); movers = load("movers.json"); notes = load("notes.json")
charts = load("charts.json"); earnings = load("earnings.json"); deals = load("deals.json")

SERIES_LABEL = {"morning-brief": "Morning Brief", "the-close": "The Close", "week-ahead": "The Week Ahead"}

# ---------- share images ----------
try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

def font(name, size, wght=None, wdth=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if wght is not None:
        try:
            axes = f.get_variation_axes(); vals = []
            for a in axes:
                nm = a.get("name", b"")
                nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                if "eight" in nm: vals.append(wght)
                elif "idth" in nm: vals.append(wdth if wdth is not None else 100)
                else: vals.append(a.get("default", a.get("minimum")))
            f.set_variation_by_axes(vals)
        except Exception: pass
    return f

def og_image(rel, eyebrow, title, footer_l):
    if not HAVE_PIL: return
    out = os.path.join(ROOT, rel)
    if os.path.exists(out) and rel != "og/default.png": return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), (7, 18, 31)); d = ImageDraw.Draw(im)
    for i in range(H):  # subtle vertical gradient
        c = int(18 + (i / H) * 8); d.line([(0, i), (W, i)], fill=(7, c, 31 + int(i / H * 12)))
    d.rectangle([0, 0, 10, H], fill=(76, 141, 255))
    try:
        logo = Image.open(os.path.join(ROOT, "logo-192.png")).convert("RGBA").resize((76, 76), Image.LANCZOS)
        im.paste(logo, (70, 56), logo)
    except Exception: pass
    brand = font("Archivo.ttf", 40, 800, 112)
    d.text((164, 70), "Alpha", font=brand, fill=(238, 243, 251))
    d.text((164 + d.textlength("Alpha", font=brand), 70), "Gen", font=brand, fill=(76, 141, 255))
    d.text((70, 182), eyebrow.upper(), font=font("PlexMono-Medium.ttf", 24), fill=(127, 176, 255))
    size = 70
    while size > 40:
        tf = font("Archivo.ttf", size, 800, 80)
        words, lines, cur = title.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=tf) <= W - 150: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) * size * 1.08 <= 300: break
        size -= 4
    y = 228
    for ln in lines[:5]:
        d.text((70, y), ln, font=tf, fill=(238, 243, 251)); y += int(size * 1.08)
    d.line([(70, H - 86), (W - 70, H - 86)], fill=(28, 51, 84), width=2)
    mono = font("PlexMono.ttf", 22)
    d.text((70, H - 66), footer_l, font=mono, fill=(147, 167, 196))
    d.text((W - 70 - d.textlength("alphagenresearch.com", font=mono), H - 66), "alphagenresearch.com", font=mono, fill=(147, 167, 196))
    im.save(out, "PNG", optimize=True)

og_image("og/default.png", "AlphaGen Research", "Market insights built to generate alpha.", "Debt · Equities · Macro")

# ---------- home ----------
home = f'''<div class="wrap">
  <div class="hero">
    <div>
      <div class="eyebrow">AlphaGen Research · New York</div>
      <h1>Market insights built to <em>generate alpha.</em></h1>
      <p class="lede">The AlphaGen Wire, mover theses, a live macro dashboard, Treasury auction tracking, and daily research across debt, equities, and macro. Built from official data.</p>
      <div class="cta-row"><button class="btn" type="button" data-open-sub>Get the daily thesis free →</button><a class="btn ghost" href="/wire">Read the Wire</a></div>
      <div class="pulse-row" data-fomc><span><b data-wire-count>0</b> Wire pieces today</span><span>Next FOMC <b data-fomc-date>Oct 27–28</b></span><span>Sources: <b>Fed · Treasury · BLS · SEC</b></span></div>
    </div>
    <a class="feature" id="feature" href="/research">
      <div class="img" id="feature-img"><div class="ph"><img src="/logo-192.png" alt=""></div></div>
      <div class="body">
        <div class="top"><span id="feature-kind">Latest AlphaGen thesis</span><span class="live">New</span></div>
        <div><span class="tag" id="feature-tag">Macro</span></div>
        <h2 id="feature-title">Loading the latest research…</h2>
        <p id="feature-desc"></p>
        <div class="top" style="text-transform:none;letter-spacing:0"><span id="feature-date"></span><span class="go">Read now →</span></div>
      </div>
    </a>
  </div>
  {LEVELS}
</div>
<section>
  <div class="wrap">
    {sec_head("Today's desk", "The daily AlphaGen lineup", '<a class="btn ghost" href="/research">All research →</a>')}
    <div class="desk-strip" data-desk></div>
  </div>
</section>
<section>
  <div class="wrap">
    {sec_head("Equities · Big movers", "What's moving, and why", '<a class="btn ghost" href="/equities">All movers →</a>')}
    <div class="spot" data-spot></div>
  </div>
</section>
<section id="wire">
  <div class="wrap split2">
    <div>{sec_head("AlphaGen Wire", "Market news, our take", '<a class="btn ghost" href="/wire">Full Wire →</a>')}{wire_card("home-wire", 14)}</div>
    <div id="research">{sec_head("AlphaGen Research", "Notes &amp; deep dives", '<a class="btn ghost" href="/research">All research →</a>')}
      <div class="notes" id="home-research" data-research="all" data-limit="6"></div>
      <div class="inline-sub"><b>Get every thesis in your inbox.</b><button class="btn" type="button" data-open-sub>Subscribe free</button></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap"><div class="cotd" data-cotd><div class="chart-load">Loading the Chart of the Day…</div></div><div style="margin-top:12px"><a class="btn ghost sm" href="/charts">Chart archive →</a></div></div>
</section>
<section>
  <div class="wrap">
    {sec_head("Macro dashboard", "The macro pulse", '<a class="btn ghost" href="/dashboard">Full dashboard →</a>')}
    <div class="pulse" data-pulse></div>
    <div data-dash="compact"></div>
  </div>
</section>
<section id="markets">
  <div class="wrap">
    {sec_head("Markets", "Live markets board", "<p>Indices, megacaps, rates and credit, commodities, FX, and crypto, next to this week's U.S. releases.</p>")}
    <div class="grid2">
      <div class="card"><div class="card-h"><span>Market overview</span></div>{tvbox("tv-overview",540,"LIVE QUOTES")}</div>
      <div class="card"><div class="card-h"><span>U.S. economic calendar</span><a href="/macro">Macro →</a></div>{tvbox("tv-calendar",540,"CPI · JOBS · FOMC · GDP")}</div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    {sec_head("Rates &amp; Debt", "The Treasury curve and the debt behind it", '<a class="btn ghost" href="/rates">Rates desk →</a>')}
    {DESK}
    <div class="card" style="margin-top:20px"><div class="card-h"><span>Latest Treasury auctions</span><a href="/auctions">Auction tracker →</a></div><div class="tbl-wrap" style="border:0"><table class="atbl" id="auc-mini"></table></div></div>
  </div>
</section>'''
ORG_LD = {"@context": "https://schema.org", "@type": "Organization", "name": "AlphaGen Research", "url": SITE, "logo": SITE + "/logo-192.png", "sameAs": [X_URL, LI_URL]}
HUBS = [("/equities","Equities","Movers & thesis"),("/deals","Deals","M&A, VC, PE, IPOs"),("/earnings","Earnings","Scorecard from filings"),("/rates","Rates","Curve & debt"),("/fed","Fed Watch","Policy & liquidity"),("/auctions","Auctions","Treasury demand"),("/credit","Credit","Spreads & lending"),("/dashboard","Macro","20-indicator dashboard"),("/global","Global","Central banks & FX"),("/housing","Housing","Mortgages & prices"),("/commodities","Commodities","Energy, metals, grains"),("/crypto","Crypto","Bitcoin & ether")]
home = home.replace('<section id="markets">', f'''<section>
  <div class="wrap">
    {sec_head("Deals &amp; private markets", "Deal flow", '<a class="btn ghost" href="/deals">All deals →</a>')}
    <div class="split2"><div><div data-deals data-view="cards" data-limit="6" id="home-deals"></div></div>
    <div class="card" style="padding:0;overflow:hidden"><div class="wire-head"><span class="live">Live SEC filings</span><span>EDGAR</span></div><div class="filings" data-filings data-limit="14"></div></div></div>
  </div>
</section>
<section>
  <div class="wrap">
    {sec_head("Coverage", "Every market, one desk")}
    <div class="hubs">{"".join(f'<a class="hub" href="{h}"><span class="eyebrow">{n}</span><b>{n}</b><span>{d}</span></a>' for h, n, d in HUBS)}</div>
  </div>
</section>
<section id="markets">''', 1)
page("index.html", "/", None, "AlphaGen Research: the AlphaGen Wire, big-mover theses, a live macro dashboard, Treasury auction tracking, and daily research on debt, equities, and macro.", "home", home, OVERVIEW_JS + "\n" + CAL_JS, ld=ORG_LD)

# ---------- wire ----------
page("wire.html", "/wire", "The Wire", "The AlphaGen Wire: market news with AlphaGen's take, built from official releases and filings, updated every few minutes.", "wire",
     phead("AlphaGen Wire", "Market news, our take.", "New pieces every few minutes through the trading day. Each one is built from an official release or filing, and every figure links to its source.") +
     f'''<section class="flush"><div class="wrap split2"><div>{wire_filters("full-wire", ["RATES","DEBT","FED","MACRO","EQUITIES","EARNINGS","COMMODITIES","FX"], True)}
<div class="card wire"><div class="wire-head"><span class="live">Live wire</span><span data-wire-updated>Updating</span></div><div class="wire-list full" id="full-wire" data-wire data-limit="300"></div></div></div>
<div style="display:grid;gap:20px;align-content:start;position:sticky;top:90px">
<div class="card"><div class="card-h"><span>How the Wire works</span></div><p style="margin:0 0 10px;color:var(--steel)">Every piece is built from a primary source: the Federal Reserve, U.S. Treasury, BLS, BEA, EIA, or a company's SEC filing. Each one links to the release it came from.</p><p style="margin:0;color:var(--steel)">Pieces publish every few minutes on weekdays from 6 a.m. to 9 p.m. ET, with weekend updates. <a href="/methodology" style="color:var(--signal-2)">Methodology →</a></p></div>
{FOMC_CARD}
<div class="card"><div class="card-h"><span>Pieces today</span></div><div style="font-family:var(--display);font-weight:800;font-stretch:76%;font-size:3rem;line-height:1" data-wire-count>0</div></div>
</div></div></section>''')

# ---------- equities ----------
page("equities.html", "/equities", "Equities & Movers", "Big movers with AlphaGen's thesis on every major move, live gainers and losers, the S&P 500 heatmap, and equities research.", "equities",
     phead("Equities", "Where the market is moving, and why.", "Live gainers, losers, and most active U.S. stocks, with AlphaGen's thesis on each major move. Every catalyst links to the company's own release or SEC filing.") +
     f'''<section class="flush"><div class="wrap"><div class="spot" data-spot></div></div></section>
<section><div class="wrap">{sec_head("Big movers", "Movers board", "<p>Updates live through the session. The theses beside it rotate as the day's biggest moves change.</p>")}
<div class="grid2"><div class="card"><div class="card-h"><span>U.S. gainers · losers · most active</span><span class="live">Live</span></div>{tvbox("tv-hot",620,"TOP GAINERS · LOSERS · MOST ACTIVE")}</div>
<div>{wire_card("eq-wire", 30, "EQUITIES,EARNINGS", "Equities wire", 690)}</div></div></div></section>
<section><div class="wrap">{sec_head("AlphaGen thesis", "Today's movers, explained", '<span class="eyebrow" style="color:var(--mute)" data-movers-updated></span>')}<div class="movers" data-movers data-limit="24"></div></div></section>
<section><div class="wrap">{sec_head("Breadth", "S&amp;P 500 heatmap", "<p>Sized by market cap and colored by today's move. Tap a sector to zoom in.</p>")}<div class="card">{tvbox("tv-heatmap",560,"S&amp;P 500 HEATMAP")}</div></div></section>
<section><div class="wrap">{sec_head("Research", "Equities research", '<a class="btn ghost" href="/earnings">Earnings scorecard →</a>')}<div class="notes cards" id="eq-research" data-research="all" data-topic="equities" data-limit="9"></div></div></section>''',
     HOT_JS + "\n" + HEAT_JS)

# ---------- earnings ----------
page("earnings.html", "/earnings", "Earnings Scorecard", "Reported quarterly results taken directly from company filings, with AlphaGen's take on each report.", "earnings",
     phead("Earnings scorecard", "Results, straight from the filings.", "Every figure on this page comes from the company's own earnings release or SEC filing, not from estimates. Year-over-year changes are calculated from the same release.") +
     f'''<section class="flush"><div class="wrap"><div data-earnings></div><p class="levels-note" style="margin-top:12px">Revenue in billions of U.S. dollars as reported (banks report net revenues). EPS is diluted, as reported. "–" means the figure was not published in a comparable form.</p></div></section>
<section><div class="wrap">{sec_head("Earnings wire", "Reports as they land")}{wire_card("earn-wire", 40, "EARNINGS", "Earnings wire")}</div></section>''')

# ---------- rates ----------
page("rates.html", "/rates", "Rates & Debt", "Live U.S. Treasury yield curve, total public debt, the next FOMC decision, auction results, and AlphaGen's rates wire.", "rates",
     phead("Rates &amp; Debt", "The rates desk.", "Official Treasury yields and debt data, the Fed calendar, auction results, and AlphaGen's read on funding markets. Refreshed automatically after every Treasury release.") +
     f'''<div class="wrap">{LEVELS}</div><section><div class="wrap">{DESK}</div></section>
<section><div class="wrap split2"><div>{sec_head("Rates wire", "Fed, Treasury, and credit")}{wire_card("rates-wire", 30, "RATES,DEBT,FED", "Rates wire")}</div>
<div>{sec_head("Federal Reserve", "Next decision")}{FOMC_CARD}<div style="height:20px"></div>
<div class="card"><div class="card-h"><span>Latest auctions</span><a href="/auctions">Tracker →</a></div><div class="tbl-wrap" style="border:0"><table class="atbl" id="auc-mini"></table></div></div><div style="height:20px"></div>
{minis(["NASDAQ:SHV","NASDAQ:IEF","NASDAQ:TLT","AMEX:HYG"])}</div></div></section>
<section><div class="wrap">{sec_head("Research", "Debt &amp; rates research")}<div class="notes cards" id="rates-research" data-research="all" data-topic="debt" data-limit="9"></div></div></section>''')

# ---------- auctions ----------
page("auctions.html", "/auctions", "Treasury Auction Tracker", "Every U.S. Treasury auction: high rates, bid-to-cover, indirect and dealer takedown, and the upcoming calendar, from official Treasury data.", "auctions",
     phead("Treasury auctions", "Auction tracker.", "Results for every bill, note, and bond auction, plus the upcoming calendar, pulled from official U.S. Treasury data. Demand at auction is one of the clearest real-time reads on appetite for U.S. debt.") +
     f'''<section class="flush"><div class="wrap">{sec_head("Coupon auctions", "Latest notes &amp; bonds", '<span class="eyebrow" style="color:var(--mute)" data-auc-asof></span>')}<div class="auc-keys" id="auc-key"><div class="card chart-load">Loading auction results…</div></div></div></section>
<section><div class="wrap">{sec_head("Results", "All recent auctions")}<div class="tbl-wrap"><table class="atbl" id="auc-results" data-limit="60"></table></div></div></section>
<section><div class="wrap grid2"><div class="card"><div class="card-h"><span>Upcoming auctions</span><span>Announced</span></div><div class="up-list" id="auc-upcoming"></div></div>
<div class="card"><div class="card-h"><span>How to read an auction</span></div><p style="margin:0 0 8px;color:var(--steel)"><b style="color:var(--paper)">High rate:</b> the highest accepted yield (bills shown on an investment-rate basis).</p><p style="margin:0 0 8px;color:var(--steel)"><b style="color:var(--paper)">Bid-to-cover:</b> dollars bid per dollar sold. Higher means stronger demand. "vs prior" compares with the last auction of the same security.</p><p style="margin:0 0 8px;color:var(--steel)"><b style="color:var(--paper)">Indirect:</b> share of competitive awards to indirect bidders, a proxy for foreign and institutional demand.</p><p style="margin:0;color:var(--steel)"><b style="color:var(--paper)">Dealers:</b> share left with primary dealers. A high share usually signals weaker end demand.</p></div></div></section>
<section><div class="wrap">{sec_head("Rates wire", "Auction and Treasury coverage")}{wire_card("auc-wire", 20, "RATES,DEBT", "Rates wire")}</div></section>''')

# ---------- dashboard ----------
page("dashboard.html", "/dashboard", "Macro Dashboard", "AlphaGen's live macro dashboard: inflation, labor, growth, policy, credit, and financial conditions, with directional signals, from official data.", "dashboard",
     phead("Macro dashboard", "The macro pulse.", "Twenty indicators institutions watch, updated automatically from official sources. Each signal compares the latest reading with roughly three months ago and is colored by whether that direction supports growth and stable prices.") +
     '''<section class="flush"><div class="wrap"><div class="pulse" data-pulse></div><div data-dash></div>
<p class="levels-note">Data: FRED, Federal Reserve Bank of St. Louis, sourcing BLS, BEA, the Federal Reserve Board, the Atlanta Fed, the Chicago Fed, ICE BofA, CBOE, and the EIA. Click any indicator for the official series. <a href="/methodology#dashboard" style="color:var(--signal-2)">How signals work →</a></p></div></section>''')

# ---------- macro ----------
page("macro.html", "/macro", "Macro", "U.S. economic calendar, AlphaGen's macro wire, commodities, the dollar, and macro research.", "macro",
     phead("Macro", "The macro tape.", "Economic releases, commodities, the dollar, and global central banks, with AlphaGen's take on what each print means for markets.") +
     f'''<section class="flush"><div class="wrap split2"><div class="card"><div class="card-h"><span>U.S. economic calendar</span><span class="live">Live</span></div>{tvbox("tv-calendar",640,"CPI · JOBS · FOMC · GDP")}</div>
<div>{wire_card("macro-wire", 30, "MACRO,COMMODITIES,FX,FED", "Macro wire", 640)}</div></div></section>
<section><div class="wrap">{sec_head("Cross-asset", "Commodities, dollar, and crypto", '<a class="btn ghost" href="/dashboard">Macro dashboard →</a>')}{minis(["AMEX:GLD","AMEX:USO","AMEX:UNG","AMEX:CPER","AMEX:UUP","FX:EURUSD","FX:USDJPY","BITSTAMP:BTCUSD"])}</div></section>
<section><div class="wrap">{sec_head("Research", "Macro research")}<div class="notes cards" id="macro-research" data-research="all" data-topic="macro" data-limit="9"></div></div></section>''',
     CAL_JS.replace("540", "640"))

# ---------- charts ----------
page("charts.html", "/charts", "Charts", "The AlphaGen Chart of the Day and chart archive, built from official data. Download any chart as a branded image.", "charts",
     phead("Charts", "Chart of the Day.", "One chart every trading day that explains what matters, built from official data, with the AlphaGen take. Download any chart as a branded image to share.") +
     f'''<section class="flush"><div class="wrap"><div class="cotd" data-cotd><div class="chart-load">Loading the Chart of the Day…</div></div></div></section>
<section><div class="wrap">{sec_head("Archive", "Recent charts")}<div class="chart-grid" data-chart-archive data-limit="36"></div></div></section>''')

for c in [c for c in charts.get("items", []) if is_live(c) and slug_ok(c.get("id"))]:
    og = f"/og/chart-{c['id']}.png"
    og_image(og[1:], "Chart of the Day · " + nice_date(c["time"]), c["title"], "AlphaGen Research")
    page(f"charts/{c['id']}.html", f"/charts/{c['id']}", c["title"], c.get("take", "")[:200], "charts",
         f'<div class="wrap phead"><a href="/charts" style="font-family:var(--mono);font-size:.72rem;color:var(--signal-2);text-decoration:none">← All charts</a></div><section class="flush"><div class="wrap"><div class="cotd" data-cotd="{E(c["id"])}"><div class="chart-load">Loading chart…</div></div></div></section>',
         og=og, kind="article")


# ---------- market hub generator ----------
def market_page(rel, path, title, h1, desc, eyebrow, active, dash_set, wire_tags, mini_syms, topic=None, top="", js="", dash_title="Live indicators"):
    body = phead(eyebrow, h1, desc) + top
    if dash_set:
        body += f'<section class="flush"><div class="wrap">{sec_head("Official data", dash_title, "<p>Updated automatically from FRED. Click any indicator for the source series.</p>")}<div data-dash data-dash-set="{dash_set}"></div></div></section>'
    body += f'<section><div class="wrap split2"><div>{sec_head("AlphaGen Wire", title + " wire")}{wire_card(rel.split(".")[0] + "-wire", 30, wire_tags, title + " wire")}</div><div>{sec_head("Markets", "Live pricing")}{minis(mini_syms)}</div></div></section>'
    if topic:
        body += f'<section><div class="wrap">{sec_head("Research", title + " research")}<div class="notes cards" data-research="all" data-topic="{topic}" data-limit="9"></div></div></section>'
    page(rel, path, title, desc, active, body, js)

# ---------- deals ----------
page("deals.html", "/deals", "Deals & Private Markets", "M&A, venture capital, private equity, and IPO deal flow from company announcements and SEC filings, with a live EDGAR filings tape and AlphaGen's take.", "deals",
     phead("Deals &amp; private markets", "Deal flow.", "M&amp;A, venture rounds, private equity, and IPOs, taken from company announcements and SEC filings, with AlphaGen's take on each. Plus a live tape of new private-placement, IPO, merger, tender, and activist filings straight from SEC EDGAR.") +
     f'''<div class="wrap"><div class="levels" data-deal-stats style="grid-template-columns:repeat(6,minmax(0,1fr))"></div></div>
<section><div class="wrap">{sec_head("Deal log", "Announced deals")}
<div class="toolbar" data-deal-filters="deal-log"><div class="filters"><button type="button" data-f="all" aria-pressed="true">All</button>{"".join(f'<button type="button" data-f="{x}" aria-pressed="false">{x}</button>' for x in ["M&A","VC","PE","IPO","Debt"])}</div></div>
<div data-deals id="deal-log" data-limit="80"></div><p class="levels-note" style="margin-top:10px">Values are as disclosed by the parties. "Undisclosed" means no value was announced. Totals count only deals logged by AlphaGen.</p></div></section>
<section><div class="wrap split2"><div class="card" style="padding:0;overflow:hidden"><div class="wire-head"><span class="live">Live SEC filings</span><span>Form D · S-1 · F-1 · DEFM14A · SC TO-T · SC 13D</span></div><div class="filings" data-filings data-limit="40"></div></div>
<div>{wire_card("deals-wire", 30, "DEALS,IPO", "Deals wire", 640)}</div></div></section>
<section><div class="wrap">{sec_head("Reading the filings", "What each SEC form means")}<div class="hubs">
<div class="hub"><span class="eyebrow">Form D</span><b>Private raise</b><span>Filed after a company or fund sells securities in a private offering, including most venture and private-fund raises.</span></div>
<div class="hub"><span class="eyebrow">S-1 / F-1</span><b>IPO filing</b><span>Registration statement for a public offering by a U.S. (S-1) or foreign (F-1) issuer.</span></div>
<div class="hub"><span class="eyebrow">DEFM14A</span><b>Merger proxy</b><span>Definitive proxy sent to shareholders to vote on a merger or acquisition.</span></div>
<div class="hub"><span class="eyebrow">SC TO-T</span><b>Tender offer</b><span>A third party's offer to buy a company's shares directly from shareholders.</span></div>
<div class="hub"><span class="eyebrow">SC 13D</span><b>Activist stake</b><span>Filed by an investor who acquires more than 5% of a company with intent to influence it.</span></div>
</div></div></section>''')

market_page("fed.html", "/fed", "Fed Watch", "The Fed watch.", "The federal funds target, effective rate, SOFR, the Fed's balance sheet, bank reserves, reverse repo, and the Treasury General Account, plus the next FOMC decision and AlphaGen's Fed coverage.", "Fed Watch", "fed", "fed", "FED,RATES",
            ["NASDAQ:SHV","NASDAQ:SHY","NASDAQ:IEF","NASDAQ:TLT"], "debt",
            top=f'<section class="flush"><div class="wrap grid2">{FOMC_CARD}<div class="card"><div class="card-h"><span>FOMC 2026–27 calendar</span><a href="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm" target="_blank" rel="noopener">Fed →</a></div><p style="margin:0;color:var(--steel);font-family:var(--mono);font-size:.8rem;line-height:1.9">2026: Oct 27–28 · Dec 8–9*<br>2027: Jan 26–27 · Mar 16–17* · Apr 27–28 · Jun 8–9* · Jul 27–28 · Sep 14–15* · Oct 26–27 · Dec 7–8*<br><span style="color:var(--mute)">* Summary of Economic Projections. 2027 dates are tentative per the Fed.</span></p></div></div></section>',
            dash_title="Policy rate &amp; liquidity")
market_page("credit.html", "/credit", "Credit", "The credit desk.", "Investment-grade and high-yield spreads by rating, bank lending standards, financial conditions, and AlphaGen's credit coverage.", "Credit", "credit", "credit", "RATES,DEBT,EARNINGS",
            ["NASDAQ:LQD","AMEX:HYG","AMEX:JNK","NASDAQ:VCIT","AMEX:BKLN","AMEX:EMB"], "debt", dash_title="Spreads &amp; lending")
market_page("global.html", "/global", "Global Markets", "Global markets.", "Major central-bank rates, European and Japanese yields, the dollar against major currencies, and global equity markets.", "Global", "global", "global", "GLOBAL,FX,MACRO",
            ["AMEX:EWJ","AMEX:EWG","AMEX:EWU","AMEX:FXI","AMEX:INDA","AMEX:EWZ","AMEX:EEM","AMEX:EFA"], "macro", dash_title="Rates &amp; currencies")
market_page("housing.html", "/housing", "Housing & Real Estate", "Housing &amp; real estate.", "Mortgage rates, housing starts and permits, home sales, supply, home prices, and real-estate equities.", "Housing", "housing", "housing", "HOUSING,MACRO",
            ["AMEX:VNQ","AMEX:XHB","AMEX:ITB","NYSE:DHI","NYSE:LEN","NASDAQ:Z"], "macro", dash_title="Mortgages, activity &amp; prices")
market_page("commodities.html", "/commodities", "Commodities & Energy", "Commodities &amp; energy.", "Crude oil, natural gas, gasoline, metals, and grains from the EIA and IMF, with AlphaGen's energy and commodities coverage.", "Commodities", "commodities", "energy", "COMMODITIES,ENERGY",
            ["AMEX:USO","AMEX:BNO","AMEX:UNG","AMEX:GLD","AMEX:SLV","AMEX:CPER","AMEX:DBA","AMEX:XLE"], "macro", dash_title="Energy, metals &amp; grains")
market_page("crypto.html", "/crypto", "Crypto", "Crypto.", "Bitcoin and ether pricing, crypto-linked equities and ETFs, and AlphaGen's digital-asset coverage from official filings.", "Crypto", "crypto", "crypto", "CRYPTO",
            ["BITSTAMP:BTCUSD","BITSTAMP:ETHUSD","COINBASE:SOLUSD","NASDAQ:COIN","NASDAQ:MSTR","AMEX:IBIT"], None, dash_title="Reference prices")

# ---------- search ----------
page("search.html", "/search", "Search", "Search the AlphaGen Wire, notes, briefs, deals, earnings, and charts.", "search",
     phead("Search", "Search AlphaGen.", "Every Wire piece, note, brief, deal, earnings report, and chart.") +
     '<section class="flush"><div class="wrap prose" style="max-width:900px"><label class="sr" for="search-q">Search</label><input class="search search-big" id="search-q" type="search" placeholder="Try NVDA, auction, CPI, merger…" autofocus><div class="eyebrow" id="search-count" style="color:var(--mute)"></div><div id="search-results"></div></div></section>', slip=False)

# ---------- research + notes ----------
page("research.html", "/research", "Research", "AlphaGen Notes, the Morning Brief, The Close, The Week Ahead, and the AlphaGen newsletter.", "research",
     phead("AlphaGen Research", "Research.", "AlphaGen Notes, daily briefs, and the AlphaGen newsletter in one place: the thesis on debt, equities, and macro.") +
     f'''<section class="flush"><div class="wrap"><div class="toolbar">{research_filters("all-research")}<button class="btn" type="button" data-open-sub>Subscribe free</button></div>
<div class="notes cards" id="all-research" data-research="all" data-limit="80"></div></div></section>''')
page("article.html", "/article", "Note", "An AlphaGen Research note.", "research", '<div class="wrap"><article class="article" id="article"><div class="empty"><b>Loading note…</b></div></article></div>')

def note_html(n):
    body = "".join(f"<p>{E(b)}</p>" if isinstance(b, str) else (f"<h2>{E(b['h'])}</h2>" if isinstance(b, dict) and b.get("h") else "") for b in n.get("body", []))
    kp = "".join(f"<li>{E(k)}</li>" for k in n.get("key_points", []))
    src = "".join(f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["name"])}</a></li>' for s in n.get("sources", []))
    label = SERIES_LABEL.get(n.get("series", ""), "AlphaGen Note")
    tks = "".join(f'<a class="tag tk" href="/stock/{E(t.split(":")[-1])}">{E(t.split(":")[-1])}</a> ' for t in n.get("tickers", []))
    url = f"{SITE}/notes/{n['id']}"
    share = f'<div class="share"><a class="btn ghost sm" href="https://www.linkedin.com/sharing/share-offsite/?url={E(url)}" target="_blank" rel="noopener">Share on LinkedIn</a><a class="btn ghost sm" href="https://x.com/intent/post?url={E(url)}&amp;text={E(n["title"])}" target="_blank" rel="noopener">Share on X</a></div>'
    return f'''<div class="wrap"><article class="article">
<a href="/research" style="font-family:var(--mono);font-size:.72rem;color:var(--signal-2);text-decoration:none">← All research</a>
<div style="margin-top:18px"><span class="tag">{E(n.get("tag","Macro"))}</span> <span class="tag tk">{label}</span> {tks}</div>
<h1>{E(n["title"])}</h1><p class="dek">{E(n.get("dek",""))}</p>
<div class="byline"><span>AlphaGen Research</span><span>{E(nice_date(n["time"]))}</span></div>
{f'<div class="kp"><span class="eyebrow">Key points</span><ul>{kp}</ul></div>' if kp else ""}
<div class="content">{body}</div>
{f'<div class="sources"><b>Sources</b><ul>{src}</ul></div>' if src else ""}
{share}
<p class="disc">For informational purposes only. Not investment advice. See <a href="/disclosures" style="color:inherit">disclosures</a>.</p>
</article></div>'''

live_notes = [n for n in notes.get("items", []) if is_live(n) and slug_ok(n.get("id"))]
for n in live_notes:
    og = f"/og/note-{n['id']}.png"
    og_image(og[1:], SERIES_LABEL.get(n.get("series", ""), "AlphaGen Note") + " · " + n.get("tag", "Macro"), n["title"], nice_date(n["time"]))
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": n["title"][:110], "description": n.get("dek", ""),
          "datePublished": n["time"], "dateModified": n.get("updated_at", n["time"]), "image": [SITE + og],
          "author": {"@type": "Organization", "name": "AlphaGen Research", "url": SITE},
          "publisher": {"@type": "Organization", "name": "AlphaGen Research", "logo": {"@type": "ImageObject", "url": SITE + "/logo-192.png"}},
          "mainEntityOfPage": f"{SITE}/notes/{n['id']}"}
    page(f"notes/{n['id']}.html", f"/notes/{n['id']}", n["title"], n.get("dek", ""), "research", note_html(n), og=og, kind="article", ld=ld)

# ---------- stock pages ----------
KNOWN = {"NVDA": ("NASDAQ:NVDA", "Nvidia"), "MSFT": ("NASDAQ:MSFT", "Microsoft"), "AAPL": ("NASDAQ:AAPL", "Apple"),
         "AMZN": ("NASDAQ:AMZN", "Amazon"), "GOOGL": ("NASDAQ:GOOGL", "Alphabet"), "META": ("NASDAQ:META", "Meta Platforms"),
         "AVGO": ("NASDAQ:AVGO", "Broadcom"), "TSLA": ("NASDAQ:TSLA", "Tesla"), "JPM": ("NYSE:JPM", "JPMorgan Chase"),
         "GS": ("NYSE:GS", "Goldman Sachs"), "BAC": ("NYSE:BAC", "Bank of America"), "MS": ("NYSE:MS", "Morgan Stanley"),
         "C": ("NYSE:C", "Citigroup"), "WFC": ("NYSE:WFC", "Wells Fargo"), "XOM": ("NYSE:XOM", "Exxon Mobil")}
stocks = dict(KNOWN)
for src in (movers.get("items", []), earnings.get("items", [])):
    for m in src:
        if m.get("ticker") and ":" in m["ticker"]:
            s = m["ticker"].split(":")[-1]
            stocks[s] = (m["ticker"], m.get("name") or stocks.get(s, ("", s))[1])
for w in wire.get("items", []):
    t = w.get("ticker")
    if t and ":" in t:
        s = t.split(":")[-1]
        if s not in stocks: stocks[s] = (t, s)
for n in notes.get("items", []) + deals.get("items", []):
    for t in n.get("tickers", []):
        if ":" in t:
            s = t.split(":")[-1]
            if s not in stocks: stocks[s] = (t, s)

for sym, (full, name) in sorted(stocks.items()):
    if not re.fullmatch(r"[A-Z0-9.\-]{1,10}", sym): continue
    js = f'''AG.tv("tv-sym","symbol-overview",{{symbols:[["{E(name)}","{full}|1D"]],chartOnly:false,width:"100%",height:440,showVolume:false,hideDateRanges:false,scalePosition:"right",scaleMode:"Normal",fontColor:"#93a7c4",gridLineColor:"rgba(39,67,108,0.35)",lineColor:"#4c8dff",topColor:"rgba(76,141,255,0.25)",bottomColor:"rgba(76,141,255,0)",dateRanges:["1d|1","1m|30","3m|60","12m|1D","60m|1W","all|1M"]}});
AG.tv("tv-fin","financials",{{symbol:"{full}",width:"100%",height:620,displayMode:"regular"}});
AG.tv("tv-prof","symbol-profile",{{symbol:"{full}",width:"100%",height:420}});'''
    body = f'''<div class="wrap phead"><div class="stock-head"><div><a href="/stocks" style="font-family:var(--mono);font-size:.72rem;color:var(--signal-2);text-decoration:none">← Stock coverage</a><h1 style="margin-top:.35em">{E(name)}</h1><span class="tk-big">{E(full)}</span></div><button class="btn" type="button" data-open-sub>Get AlphaGen research free</button></div></div>
<section class="flush"><div class="wrap"><div class="card">{tvbox("tv-sym",440,"LIVE CHART")}</div></div></section>
<section><div class="wrap">{sec_head("AlphaGen thesis", "Mover coverage")}<div class="movers" data-movers data-ticker="{sym}" data-limit="6"></div></div></section>
<section><div class="wrap split2"><div>{sec_head("Wire", "AlphaGen Wire coverage")}{wire_card("stk-wire", 30, "", "Coverage", None, sym)}</div>
<div>{sec_head("Earnings", "Reported results")}<div data-earnings data-ticker="{full}"></div><div style="height:20px"></div>{sec_head("Research", "Notes")}<div class="notes" data-research="notes" data-ticker="{sym}" data-limit="6"></div></div></div></section>
<section><div class="wrap grid2"><div class="card"><div class="card-h"><span>Financials</span></div>{tvbox("tv-fin",620,"FINANCIALS")}</div><div class="card"><div class="card-h"><span>Company profile</span></div>{tvbox("tv-prof",420,"PROFILE")}</div></div></section>'''
    page(f"stock/{sym}.html", f"/stock/{sym}", f"{name} ({sym})", f"AlphaGen coverage of {name} ({sym}): live chart, mover theses, Wire coverage, reported earnings, and research.", "stocks", body, js)

tiles = "".join(f'<a class="card" href="/stock/{E(s)}" style="text-decoration:none;display:grid;gap:4px"><span class="tag tk" style="justify-self:start">{E(s)}</span><b style="font-family:var(--display);font-stretch:88%;font-size:1.1rem">{E(n)}</b><span style="font-family:var(--mono);font-size:.68rem;color:var(--mute)">{E(f)}</span></a>' for s, (f, n) in sorted(stocks.items(), key=lambda kv: kv[1][1]))
page("stocks.html", "/stocks", "Stock Coverage", "Every company AlphaGen covers, with live charts, mover theses, Wire coverage, earnings, and research.", "stocks",
     phead("Stock coverage", "Companies we cover.", "Every company that appears in the AlphaGen Wire, mover theses, earnings scorecard, or research gets its own coverage page. The list grows automatically.") +
     f'<section class="flush"><div class="wrap"><div class="minis" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,220px),1fr))">{tiles}</div></div></section>')

# ---------- credibility pages ----------
def prose_page(rel, path, title, h1, desc, eyebrow, html_body, active="about"):
    page(rel, path, title, desc, active, f'<div class="wrap phead"><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1></div><section class="flush"><div class="wrap prose">{html_body}</div></section>', slip=(rel == "about.html"))

prose_page("about.html", "/about", "About", "Independent research, built on official data.", "About AlphaGen Research: independent markets research on debt, equities, and macro, built from official data.", "About AlphaGen", '''
<p><strong>AlphaGen Research is an independent markets research publication covering debt, equities, and macro.</strong> We publish for investors who want the signal behind the headline: what a data release, an auction, or an earnings report actually means for markets.</p>
<div class="facts"><div><b>Primary sources</b><span>Fed · Treasury · BLS · SEC</span></div><div><b>Every few minutes</b><span>The AlphaGen Wire, weekdays</span></div><div><b>Daily</b><span>Morning Brief · Chart · The Close</span></div><div><b>20 indicators</b><span>Live macro dashboard</span></div></div>
<h2>What we publish</h2>
<ul><li><strong>The AlphaGen Wire:</strong> short takes on economic data, Fed and Treasury releases, and company filings, each linked to its source.</li>
<li><strong>Movers:</strong> AlphaGen's thesis on the day's biggest stock moves, tied to the company's own disclosure.</li>
<li><strong>Daily briefs:</strong> the Morning Brief before the open, The Close after the bell, and The Week Ahead on Sundays.</li>
<li><strong>Chart of the Day:</strong> one chart, built from official data, that explains what matters.</li>
<li><strong>AlphaGen Notes and the AlphaGen newsletter:</strong> deeper research on the themes driving rates, credit, and equities.</li>
<li><strong>Data desks:</strong> the macro dashboard, Treasury auction tracker, yield curve, and earnings scorecard.</li></ul>
<h2>How we work</h2>
<p>Every figure we publish comes from an official source: a statistical agency, a central bank, the U.S. Treasury, or a company's own filing. We link to that source so readers can check it. Read our <a href="/methodology">methodology</a> and <a href="/standards">editorial standards</a>.</p>
<h2>Contact</h2>
<p>Reach the AlphaGen desk on <a href="https://x.com/alphageniq" target="_blank" rel="noopener">X</a> or <a href="https://www.linkedin.com/company/alphagen-research" target="_blank" rel="noopener">LinkedIn</a>.</p>''')

prose_page("methodology.html", "/methodology", "Methodology", "How AlphaGen is built.", "How AlphaGen Research sources data, produces the Wire, computes dashboard signals, and measures Treasury auctions.", "Methodology", '''
<h2>Sources</h2>
<p>AlphaGen uses primary sources only for every figure it publishes: the Bureau of Labor Statistics, the Bureau of Economic Analysis, the Census Bureau, the Federal Reserve Board and regional Reserve Banks, the U.S. Department of the Treasury (including TreasuryDirect and Fiscal Data), the Energy Information Administration, the CFTC, official foreign central banks, and company filings with the SEC and company investor-relations releases. News coverage may alert us to a development, but we never cite a news outlet as the source of a figure.</p>
<h2>How the Wire and research are produced</h2>
<p>AlphaGen uses AI-assisted research tools, operating under fixed editorial rules, to monitor official releases throughout the day and draft Wire pieces, mover theses, briefs, and notes. Those rules require every number to be taken directly from the primary source it links to, prohibit stock-price and percentage-move claims in written content, prohibit buy, sell, or hold recommendations and price targets, and require that anything that cannot be verified is left out. Wire pieces are scheduled to publish a few minutes apart.</p>
<h2 id="movers">Movers</h2>
<p>Mover theses cover large, liquid U.S. companies with significant moves during the session. A stock is included only if its move can be tied to a verifiable company-specific disclosure (an earnings release, 8-K, guidance update, transaction announcement, or regulatory decision) or to official data clearly tied to its sector. Live price action is shown by the chart beside each thesis, not in the text.</p>
<h2 id="dashboard">Macro dashboard signals</h2>
<p>Each indicator is pulled from FRED (Federal Reserve Bank of St. Louis), which republishes the underlying official series. The headline value is the latest observation, transformed where noted (for example, year-over-year percent change for price indexes, or monthly change for payrolls). The signal compares the latest value with the value roughly three months earlier: three observations for monthly data, thirteen for weekly data, and about sixty-three trading days for daily data. Signals are colored green when the direction is generally supportive of growth and stable prices (for example, falling credit spreads or falling inflation) and red when it is not. Indicators without a clear "good" direction, such as the policy rate, are shown in neutral blue. Signals are descriptive, not forecasts.</p>
<h2 id="auctions">Treasury auctions</h2>
<p>Auction data comes from the U.S. Treasury's Fiscal Data API. The high rate is the highest accepted yield (bills on an investment-rate basis; floating-rate notes show the high discount margin). Bid-to-cover is total bids divided by the amount accepted. Indirect and primary-dealer shares are each group's accepted amount as a share of total competitive awards. "vs prior" compares bid-to-cover with the most recent auction of the same security type and term.</p>
<h2>Yields and debt</h2>
<p>Yield curve data uses the Treasury's Daily Par Yield Curve Rates, published after each trading day. Total public debt uses the Treasury's Debt to the Penny dataset. Both refresh automatically.</p>
<h2>Market data</h2>
<p>Live quotes, charts, heatmaps, and mover lists are provided by TradingView and may be delayed. AlphaGen does not verify third-party market data.</p>''')

prose_page("standards.html", "/standards", "Editorial Standards", "Editorial standards.", "AlphaGen Research's editorial standards: sourcing, accuracy, corrections, and what we will not publish.", "Editorial standards", '''
<h2>Accuracy first</h2>
<p>Every figure must come from a primary source and link to it. If a number cannot be verified at the source, it is not published. Arithmetic, such as year-over-year changes and spreads, is calculated from the source figures, not estimated.</p>
<h2>Analysis, not advice</h2>
<p>AlphaGen publishes analysis of public information. We do not make buy, sell, or hold recommendations, set price targets, or tell readers what to do with their money. Where we share a view, we frame it as analysis of what the data suggests, not as a prediction.</p>
<h2>Attribution</h2>
<p>We credit the agency, central bank, or company that produced the information. We do not reproduce or rewrite other publications' reporting.</p>
<h2>Corrections</h2>
<p>If we get something wrong, we correct it promptly. To flag an error, contact the desk on <a href="https://x.com/alphageniq" target="_blank" rel="noopener">X</a> or <a href="https://www.linkedin.com/company/alphagen-research" target="_blank" rel="noopener">LinkedIn</a> with a link to the item and the source.</p>
<h2>Use of AI</h2>
<p>AlphaGen uses AI-assisted tools to monitor releases and draft content under the rules above. See our <a href="/methodology">methodology</a> for details.</p>''')

prose_page("disclosures.html", "/disclosures", "Disclosures", "Disclosures.", "Important disclosures for AlphaGen Research content.", "Disclosures", '''
<p><strong>For informational purposes only.</strong> All content published by AlphaGen Research, including the AlphaGen Wire, mover theses, briefs, notes, charts, dashboards, and the AlphaGen newsletter, is general market commentary provided for informational and educational purposes. It is not investment, legal, tax, or accounting advice, and it is not an offer or solicitation to buy or sell any security or financial instrument.</p>
<p><strong>No personalized advice.</strong> AlphaGen content does not take into account any reader's investment objectives, financial situation, or needs. Readers should do their own research and consult a qualified professional before making investment decisions.</p>
<p><strong>No guarantee.</strong> AlphaGen uses sources it believes to be reliable, including official government and company sources, but does not guarantee the accuracy, completeness, or timeliness of any information. Data may be revised by its publisher after AlphaGen reports it. Past performance does not guarantee future results, and all investments involve risk, including loss of principal.</p>
<p><strong>Positions.</strong> AlphaGen, its contributors, and affiliates may hold positions in securities or instruments discussed on this site and may trade them at any time.</p>
<p><strong>Forward-looking statements.</strong> Any views about future market conditions reflect judgment at the time of publication and may change without notice.</p>
<p><strong>Third-party data.</strong> Market quotes, charts, and lists are provided by TradingView and may be delayed. Economic data is sourced from FRED (Federal Reserve Bank of St. Louis) and the underlying agencies, and from the U.S. Treasury. These providers are not affiliated with AlphaGen and do not endorse it.</p>
<p><strong>AI-assisted content.</strong> AlphaGen uses AI-assisted tools to monitor public releases and draft content under fixed editorial rules. See the <a href="/methodology">methodology</a>.</p>''')


# ---------- 404 (falls back to the live note reader for notes not yet built) ----------
page("404.html", "/404", "Page not found", "This page could not be found.", "", '<div class="wrap phead"><div class="eyebrow">404</div><h1>That page moved or doesn\'t exist.</h1><p>Try the <a href="/wire" style="color:var(--signal-2)">Wire</a>, <a href="/research" style="color:var(--signal-2)">Research</a>, or the <a href="/" style="color:var(--signal-2)">home page</a>.</p></div>',
     js='(function(){var m=location.pathname.match(/^\\/notes\\/([A-Za-z0-9._-]+)$/);if(m)location.replace("/article?id="+encodeURIComponent(m[1]));})();', slip=False)


prose_page("privacy.html", "/privacy", "Privacy Policy", "Privacy policy.", "How AlphaGen Research handles information when you visit alphagenresearch.com.", "Privacy", """
<p><strong>Last updated: October 14, 2026.</strong> This policy explains what information is involved when you visit alphagenresearch.com.</p>
<h2>What we collect</h2>
<p>AlphaGen does not ask you to create an account and does not collect your name or email on this site. Newsletter sign-ups are handled by our newsletter provider, beehiiv, on its own pages and under its own privacy policy.</p>
<p>The site stores two small preferences in your browser's local storage so the newsletter pop-up doesn't keep reappearing: whether you closed it and whether you clicked to subscribe. This information stays on your device.</p>
<h2>Service providers</h2>
<p>Like most websites, pages are delivered through a hosting provider (Netlify), which processes standard request information such as IP address and browser type to serve and secure the site. Fonts load from Google Fonts. Market quotes and charts are embedded from TradingView, which may set its own cookies or collect usage data under its own policies. Data shown on the site is retrieved from public sources such as the U.S. Treasury, FRED, and SEC EDGAR.</p>
<h2>Analytics</h2>
<p>If we add analytics, we will use a privacy-focused, cookie-free service and update this policy.</p>
<h2>Links</h2>
<p>The site links to official sources and third-party sites. Their privacy practices are their own.</p>
<h2>Contact</h2>
<p>Questions about this policy can be sent to the desk on <a href="https://x.com/alphageniq" target="_blank" rel="noopener">X</a> or <a href="https://www.linkedin.com/company/alphagen-research" target="_blank" rel="noopener">LinkedIn</a>.</p>""")

prose_page("terms.html", "/terms", "Terms of Use", "Terms of use.", "Terms governing use of alphagenresearch.com and AlphaGen Research content.", "Terms", """
<p><strong>Last updated: October 14, 2026.</strong> By using alphagenresearch.com, you agree to these terms.</p>
<h2>Informational use only</h2>
<p>All content is general market commentary for informational purposes. It is not investment, legal, or tax advice, and it is not an offer or solicitation to buy or sell any security. See our <a href="/disclosures">disclosures</a>.</p>
<h2>Accuracy and availability</h2>
<p>We work to keep content accurate and sourced to official publications, but we do not guarantee that content is complete, current, or error-free, and data may be revised by its publisher. The site and its data feeds are provided "as is" and may be interrupted or delayed.</p>
<h2>Intellectual property</h2>
<p>AlphaGen's written content, charts, design, and branding belong to AlphaGen Research. You may share links and short excerpts with attribution to AlphaGen Research and a link to the original page. Charts downloaded from the site may be shared with their AlphaGen branding intact. Underlying public data belongs to its publishers. Third-party widgets and data remain the property of their providers.</p>
<h2>Acceptable use</h2>
<p>Don't scrape the site at a volume that disrupts it, attempt to interfere with its operation, or present AlphaGen content as your own.</p>
<h2>Limitation of liability</h2>
<p>To the fullest extent permitted by law, AlphaGen Research is not liable for any losses or damages arising from use of the site or reliance on its content.</p>
<h2>Changes</h2>
<p>We may update these terms. Continued use of the site means you accept the current version.</p>""")

# ---------- RSS + sitemap ----------
items = sorted([n for n in live_notes], key=lambda n: n["time"], reverse=True)[:40]
def rfc(iso):
    d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")); return d.strftime("%a, %d %b %Y %H:%M:%S +0000")
rss = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>AlphaGen Research</title><link>' + SITE + '</link><description>AlphaGen Notes and briefs on debt, equities, and macro.</description>' + \
      "".join(f'<item><title>{E(n["title"])}</title><link>{SITE}/notes/{n["id"]}</link><guid>{SITE}/notes/{n["id"]}</guid><pubDate>{rfc(n["time"])}</pubDate><description>{E(n.get("dek",""))}</description></item>' for n in items) + "</channel></rss>\n"
write("rss.xml", rss)
urls = ["/", "/wire", "/equities", "/earnings", "/deals", "/stocks", "/rates", "/fed", "/auctions", "/credit", "/dashboard", "/macro", "/global", "/housing", "/commodities", "/crypto", "/charts", "/research", "/search", "/about", "/methodology", "/standards", "/disclosures", "/privacy", "/terms"] + \
       [f"/notes/{n['id']}" for n in live_notes] + [f"/stock/{s}" for s in stocks] + [f"/charts/{c['id']}" for c in charts.get("items", []) if is_live(c) and slug_ok(c.get("id"))]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print(f"built: {len(live_notes)} notes, {len(stocks)} stocks, {len([c for c in charts.get('items', []) if is_live(c)])} charts, PIL={HAVE_PIL}")
