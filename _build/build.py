#!/usr/bin/env python3
"""Builds the AlphaGen static pages from shared templates. Run: python3 _build/build.py"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

X_ICON = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.68l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64z"/></svg>'
LI_ICON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>'
X_URL = "https://x.com/alphageniq"
LI_URL = "https://www.linkedin.com/company/alphagen-research"
SUB_URL = "https://alphagen-newsletter.beehiiv.com/subscribe"

NAV = [("/", "Home", "home"), ("/wire", "Wire", "wire"), ("/equities", "Equities", "equities"),
       ("/rates", "Rates & Debt", "rates"), ("/macro", "Macro", "macro"), ("/research", "Research", "research")]

TAPE = ",".join(["FOREXCOM:SPXUSD", "FOREXCOM:NSXUSD", "FOREXCOM:DJI", "AMEX:IWM", "NASDAQ:NVDA", "NASDAQ:AAPL",
                 "NASDAQ:MSFT", "NASDAQ:TLT", "AMEX:HYG", "AMEX:GLD", "AMEX:USO", "FX:EURUSD", "FX:USDJPY", "BITSTAMP:BTCUSD"])

def head(title, desc, path):
    full = "AlphaGen Research" if title is None else f"{title} | AlphaGen Research"
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#07121f">
<link rel="icon" type="image/png" href="/logo-192.png">
<link rel="apple-touch-icon" href="/logo-192.png">
<link rel="canonical" href="https://alphagenresearch.com{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="AlphaGen Research">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://alphagenresearch.com{path}">
<meta property="og:image" content="https://alphagenresearch.com/logo-192.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:site" content="@alphageniq">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500;62..125,600;62..125,700;62..125,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/ag.css?v=3">
</head>
<body>
'''

def header(active):
    cur = ' aria-current="page"'
    links = "".join(f'<a class="txt" href="{h}"{cur if k == active else ""}>{n}</a>' for h, n, k in NAV)
    return f'''<div class="statusbar"><div class="wrap"><span class="mkt" id="mkt"><i></i><b>NYSE</b></span><span class="clock" id="clock"></span></div></div>
<header class="mast">
  <div class="wrap">
    <a class="logo" href="/"><img class="mark" src="/logo-192.png" alt="" width="34" height="34">Alpha<span>Gen</span></a>
    <nav class="nav" aria-label="Main">
      <div class="links">{links}</div>
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

def footer(extra_js=""):
    nav1 = "".join(f'<li><a href="{h}">{n}</a></li>' for h, n, k in NAV[:3])
    nav2 = "".join(f'<li><a href="{h}">{n}</a></li>' for h, n, k in NAV[3:])
    return f'''<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="logo" style="font-size:1.1rem"><img class="mark" src="/logo-192.png" alt="" width="30" height="30">Alpha<span>Gen</span></div>
        <p class="disc">Independent markets research on debt, equities, and macro. AlphaGen content is for informational and educational purposes only and is not investment advice or a recommendation to buy or sell any security.</p>
        <div class="social"><a href="{X_URL}" target="_blank" rel="noopener">{X_ICON}<span>X</span></a><a href="{LI_URL}" target="_blank" rel="noopener">{LI_ICON}<span>LinkedIn</span></a></div>
      </div>
      <div><h4>Markets</h4><ul>{nav1}</ul></div>
      <div><h4>Coverage</h4><ul>{nav2}</ul></div>
      <div><h4>Data</h4><ul><li>Quotes &amp; charts: TradingView</li><li>Yields &amp; debt: U.S. Treasury</li><li>Wire sources: official releases &amp; filings</li></ul></div>
    </div>
    <div class="copy">© 2026 AlphaGen Research. Market data may be delayed.</div>
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
<script src="/assets/ag.js?v=3"></script>
{extra_js}
</body>
</html>
'''

def wire_card(view_id, limit, tags="", title="Live wire", height=None):
    style = f' style="max-height:{height}px"' if height else ""
    return f'''<div class="card wire">
  <div class="wire-head"><span class="live">{title}</span><span data-wire-updated>Updating</span></div>
  <div class="wire-list" id="{view_id}" data-wire data-limit="{limit}" data-tags="{tags}"{style}></div>
</div>'''

def minis(symbols):
    return '<div class="minis">' + "".join(f'<div class="card"><tv-mini-chart symbol="{s}" theme="dark" transparent></tv-mini-chart></div>' for s in symbols) + '</div>'

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

def tvbox(id_, h, ph):
    return f'<div class="tv"><div class="tradingview-widget-container" id="{id_}"><div class="tradingview-widget-container__widget" style="min-height:{h}px" data-ph="{ph}"></div></div></div>'

def page(name, path, title, desc, active, body, js=""):
    html = head(title, desc, path) + header(active) + '<main id="top">\n' + body + '\n</main>\n' + SLIP + footer(f"<script>\n{js}\n</script>" if js else "")
    with open(os.path.join(ROOT, name), "w") as f:
        f.write(html)

WIRE_FILTERS = '''<div class="toolbar" data-wire-filters="{id}">
  <div class="filters" role="group" aria-label="Filter the Wire">
    <button type="button" data-f="all" aria-pressed="true">All</button>{btns}
  </div>{search}
</div>'''
def wire_filters(id_, tags, search=False):
    btns = "".join(f'<button type="button" data-f="{t}" aria-pressed="false">{t.title() if t != "FX" else "FX"}</button>' for t in tags)
    s = '<label class="sr" for="wire-q">Search the Wire</label><input class="search" id="wire-q" type="search" placeholder="Search the Wire: CPI, NVDA, auction…">' if search else ""
    return WIRE_FILTERS.format(id=id_, btns=btns, search=s)

RESEARCH_FILTERS = '''<div class="filters" role="group" aria-label="Filter research" data-research-filters="{id}">
  <button type="button" data-f="all" aria-pressed="true">All</button>
  <button type="button" data-f="debt" aria-pressed="false">Debt &amp; Rates</button>
  <button type="button" data-f="equities" aria-pressed="false">Equities</button>
  <button type="button" data-f="macro" aria-pressed="false">Macro</button>
</div>'''

# ---------------- HOME ----------------
home = f'''<div class="wrap">
  <div class="hero">
    <div>
      <div class="eyebrow">AlphaGen Research · New York</div>
      <h1>Market insights built to <em>generate alpha.</em></h1>
      <p class="lede">The AlphaGen Wire, mover theses, and daily research across debt, equities, and macro. Built from official data and written for serious investors.</p>
      <div class="cta-row"><button class="btn" type="button" data-open-sub>Get the daily thesis free →</button><a class="btn ghost" href="/wire">Read the Wire</a></div>
      <div class="pulse-row" data-fomc><span><b data-wire-count>0</b> Wire pieces today</span><span>Next FOMC <b data-fomc-date>Oct 27–28</b></span><span>Sources: <b>Fed · Treasury · BLS · SEC</b></span></div>
    </div>
    <a class="feature" id="feature" href="/research">
      <div class="img" id="feature-img"><div class="ph"><img src="/logo-192.png" alt=""></div></div>
      <div class="body">
        <div class="top"><span id="feature-kind">Latest AlphaGen thesis</span><span class="live">New</span></div>
        <div><span class="tag" id="feature-tag">Macro</span></div>
        <h2 id="feature-title">Another 2008?</h2>
        <p id="feature-desc">AlphaGen Macroview | Oct 8/9th, 2026</p>
        <div class="top" style="text-transform:none;letter-spacing:0"><span id="feature-date">Oct 9, 2026</span><span class="go">Read now →</span></div>
      </div>
    </a>
  </div>
  {LEVELS}
</div>

<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Equities · Big movers</div><h2 class="sec">What's moving, and why</h2></div><a class="btn ghost" href="/equities">All movers →</a></div>
    <div class="spot" data-spot></div>
  </div>
</section>

<section id="wire">
  <div class="wrap split2">
    <div>
      <div class="sec-head"><div><div class="eyebrow">AlphaGen Wire</div><h2 class="sec">Market news, our take</h2></div><a class="btn ghost" href="/wire">Full Wire →</a></div>
      {wire_card("home-wire", 14)}
    </div>
    <div id="research">
      <div class="sec-head"><div><div class="eyebrow">AlphaGen Research</div><h2 class="sec">Notes &amp; deep dives</h2></div><a class="btn ghost" href="/research">All research →</a></div>
      <div class="notes" id="home-research" data-research="all" data-limit="6"></div>
      <div class="inline-sub"><b>Get every thesis in your inbox.</b><button class="btn" type="button" data-open-sub>Subscribe free</button></div>
    </div>
  </div>
</section>

<section id="markets">
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Markets</div><h2 class="sec">Live markets board</h2></div><p>Indices, megacaps, rates and credit, commodities, FX, and crypto, next to this week's U.S. releases.</p></div>
    <div class="grid2">
      <div class="card"><div class="card-h"><span>Market overview</span></div>{tvbox("tv-overview",540,"LIVE QUOTES")}</div>
      <div class="card"><div class="card-h"><span>U.S. economic calendar</span><a href="/macro">Macro →</a></div>{tvbox("tv-calendar",540,"CPI · JOBS · FOMC · GDP")}</div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Rates &amp; Debt</div><h2 class="sec">The Treasury curve and the debt behind it</h2></div><a class="btn ghost" href="/rates">Rates desk →</a></div>
    {DESK}
  </div>
</section>'''
page("index.html", "/", None, "AlphaGen Research: the AlphaGen Wire, big-mover theses, Treasury curve and debt data, and daily research on debt, equities, and macro.", "home", home, OVERVIEW_JS + "\n" + CAL_JS)

# ---------------- EQUITIES ----------------
eq = f'''<div class="wrap phead">
  <div class="eyebrow">Equities</div>
  <h1>Where the market is moving, and why.</h1>
  <p>Live gainers, losers, and most active U.S. stocks, with AlphaGen's thesis on each major move. Every catalyst links to the company's own release or SEC filing.</p>
</div>
<section class="flush">
  <div class="wrap">
    <div class="spot" data-spot></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Big movers</div><h2 class="sec">Movers board</h2></div><p>Updates live through the session. The theses beside it rotate as the day's biggest moves change.</p></div>
    <div class="grid2">
      <div class="card"><div class="card-h"><span>U.S. gainers · losers · most active</span><span class="live">Live</span></div>{tvbox("tv-hot",620,"TOP GAINERS · LOSERS · MOST ACTIVE")}</div>
      <div>{wire_card("eq-wire", 30, "EQUITIES,EARNINGS", "Equities wire", 690)}</div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">AlphaGen thesis</div><h2 class="sec">Today's movers, explained</h2></div><span class="eyebrow" style="color:var(--mute)" data-movers-updated></span></div>
    <div class="movers" data-movers data-limit="24"></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Breadth</div><h2 class="sec">S&amp;P 500 heatmap</h2></div><p>Sized by market cap and colored by today's move. Tap a sector to zoom in.</p></div>
    <div class="card">{tvbox("tv-heatmap",560,"S&amp;P 500 HEATMAP")}</div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Megacaps</div><h2 class="sec">The names that move the index</h2></div></div>
    {minis(["NASDAQ:NVDA","NASDAQ:MSFT","NASDAQ:AAPL","NASDAQ:AMZN","NASDAQ:GOOGL","NASDAQ:META","NASDAQ:AVGO","NASDAQ:TSLA"])}
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Research</div><h2 class="sec">Equities research</h2></div><a class="btn ghost" href="/research">All research →</a></div>
    <div class="notes cards" id="eq-research" data-research="all" data-topic="equities" data-limit="9"></div>
  </div>
</section>'''
page("equities.html", "/equities", "Equities", "Big movers with AlphaGen's thesis on every major move, live gainers and losers, the S&P 500 heatmap, and equities research.", "equities", eq, HOT_JS + "\n" + HEAT_JS)

# ---------------- RATES ----------------
rates = f'''<div class="wrap phead">
  <div class="eyebrow">Rates &amp; Debt</div>
  <h1>The rates desk.</h1>
  <p>Official Treasury yields and debt data, the Fed calendar, and AlphaGen's read on funding markets. Refreshed automatically after every Treasury release.</p>
</div>
<div class="wrap">{LEVELS}</div>
<section>
  <div class="wrap">{DESK}</div>
</section>
<section>
  <div class="wrap split2">
    <div>
      <div class="sec-head"><div><div class="eyebrow">Rates wire</div><h2 class="sec">Fed, Treasury, and credit</h2></div></div>
      {wire_card("rates-wire", 30, "RATES,DEBT,FED", "Rates wire")}
    </div>
    <div>
      <div class="sec-head"><div><div class="eyebrow">Federal Reserve</div><h2 class="sec">Next decision</h2></div></div>
      {FOMC_CARD}
      <div style="height:20px"></div>
      <div class="sec-head" style="margin-bottom:14px"><div><div class="eyebrow">Market pricing</div><h2 class="sec" style="font-size:1.5rem">Duration &amp; credit</h2></div></div>
      {minis(["NASDAQ:SHV","NASDAQ:IEF","NASDAQ:TLT","AMEX:HYG"])}
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Research</div><h2 class="sec">Debt &amp; rates research</h2></div></div>
    <div class="notes cards" id="rates-research" data-research="all" data-topic="debt" data-limit="9"></div>
  </div>
</section>'''
page("rates.html", "/rates", "Rates & Debt", "Live U.S. Treasury yield curve, total public debt, the next FOMC decision, and AlphaGen's rates wire and research.", "rates", rates)

# ---------------- MACRO ----------------
macro = f'''<div class="wrap phead">
  <div class="eyebrow">Macro</div>
  <h1>The macro tape.</h1>
  <p>Economic releases, commodities, the dollar, and global central banks, with AlphaGen's take on what each print means for markets.</p>
</div>
<section class="flush">
  <div class="wrap split2">
    <div class="card"><div class="card-h"><span>U.S. economic calendar</span><span class="live">Live</span></div>{tvbox("tv-calendar",640,"CPI · JOBS · FOMC · GDP")}</div>
    <div>{wire_card("macro-wire", 30, "MACRO,COMMODITIES,FX,FED", "Macro wire", 640)}</div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Cross-asset</div><h2 class="sec">Commodities, dollar, and crypto</h2></div></div>
    {minis(["AMEX:GLD","AMEX:USO","AMEX:UNG","AMEX:CPER","AMEX:UUP","FX:EURUSD","FX:USDJPY","BITSTAMP:BTCUSD"])}
  </div>
</section>
<section>
  <div class="wrap">
    <div class="sec-head"><div><div class="eyebrow">Research</div><h2 class="sec">Macro research</h2></div></div>
    <div class="notes cards" id="macro-research" data-research="all" data-topic="macro" data-limit="9"></div>
  </div>
</section>'''
page("macro.html", "/macro", "Macro", "U.S. economic calendar, AlphaGen's macro wire, commodities, the dollar, and macro research.", "macro", macro, CAL_JS.replace("540", "640"))

# ---------------- WIRE ----------------
wire = f'''<div class="wrap phead">
  <div class="eyebrow">AlphaGen Wire</div>
  <h1>Market news, our take.</h1>
  <p>New pieces every few minutes through the trading day. Each one is built from an official release or filing, and every figure links to its source.</p>
</div>
<section class="flush">
  <div class="wrap split2">
    <div>
      {wire_filters("full-wire", ["RATES","DEBT","FED","MACRO","EQUITIES","EARNINGS","COMMODITIES","FX"], search=True)}
      <div class="card wire"><div class="wire-head"><span class="live">Live wire</span><span data-wire-updated>Updating</span></div><div class="wire-list full" id="full-wire" data-wire data-limit="150"></div></div>
    </div>
    <div style="display:grid;gap:20px;position:sticky;top:90px">
      <div class="card"><div class="card-h"><span>How the Wire works</span></div><p style="margin:0 0 10px;color:var(--steel)">The AlphaGen Wire is built only from primary sources: the Federal Reserve, U.S. Treasury, BLS, BEA, and company filings with the SEC. Every piece links to the release it came from.</p><p style="margin:0;color:var(--steel)">Pieces publish every few minutes on weekdays from 6 a.m. to 9 p.m. ET, with weekend updates.</p></div>
      {FOMC_CARD}
      <div class="card"><div class="card-h"><span>Pieces today</span></div><div style="font-family:var(--display);font-weight:800;font-stretch:76%;font-size:3rem;line-height:1" data-wire-count>0</div></div>
    </div>
  </div>
</section>'''
page("wire.html", "/wire", "The Wire", "The AlphaGen Wire: market news with AlphaGen's take, built from official releases and filings, updated every few minutes.", "wire", wire)

# ---------------- RESEARCH ----------------
research = f'''<div class="wrap phead">
  <div class="eyebrow">AlphaGen Research</div>
  <h1>Research.</h1>
  <p>AlphaGen Notes and the AlphaGen newsletter in one place: the thesis on debt, equities, and macro.</p>
</div>
<section class="flush">
  <div class="wrap">
    <div class="toolbar">{RESEARCH_FILTERS.format(id="all-research")}<button class="btn" type="button" data-open-sub>Subscribe free</button></div>
    <div class="notes cards" id="all-research" data-research="all" data-limit="60"></div>
  </div>
</section>'''
page("research.html", "/research", "Research", "AlphaGen Notes and newsletter research on debt, equities, and macro.", "research", research)

# ---------------- ARTICLE ----------------
article = '''<div class="wrap"><article class="article" id="article"><div class="empty"><b>Loading note…</b></div></article></div>'''
page("article.html", "/article", "Note", "An AlphaGen Research note.", "research", article)
print("built")
