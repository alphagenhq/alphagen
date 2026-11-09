"""Curated Advisor Intelligence sample editions (Monday, Nov 9, 2026).
Rendered statically into the home and /institutional previews and fed as JSON to the
interactive sample on /institutional. Every figure here was checked against company
releases, exchange/index data, CME FedWatch or AAA before publishing."""
import html, json
E = html.escape

DATE = "Monday, Nov 9, 2026"

SAMPLE = {
  "date": DATE,
  "am": {
    "edition": "Pre-Market Daily",
    "time": "Before the open",
    "subject": "Nvidia's CEO under review, oil breaks lower, four big reports tonight",
    "oneline": "Stocks are set to rebound from last week's AI selloff as oil drops again, but Nvidia opens under a cloud after its board launched an investigation into CEO Jensen Huang.",
    "stats": [
      {"k": "Brent crude", "v": "≈$94", "c": "−4% early", "d": "dn"},
      {"k": "Dec. Fed hike odds", "v": "≈80%", "c": "rate futures", "d": ""},
      {"k": "Reported this morning", "v": "CEG · KKR", "c": "both beat", "d": "up"},
      {"k": "Reporting tonight", "v": "TTD · RKLB · HIMS · TTWO", "c": "after the close", "d": ""},
    ],
    "happened": [
      "<b>Nvidia's board opened an independent investigation</b> into CEO Jensen Huang's relationship with a woman U.S. intelligence reportedly believes worked for China's Ministry of State Security. Huang admitted an affair in a Sunday memo and says he will cooperate.",
      "<b>Oil is sliding again</b> after President Trump said fresh strikes on Iran are highly unlikely while talks progress. Brent fell 16% last week, its steepest weekly drop since the start of the pandemic.",
      "<b>AI demand looks intact.</b> Constellation Energy beat estimates, raised its 2026 outlook and signed a 20-year nuclear power deal with Google, and AMD was upgraded at Oppenheimer.",
    ],
    "means": "Last week's drop was driven by political fear about AI spending, not by weaker earnings. This morning's company news points the other way.",
    "qa": [
      {"q": "Should I sell Nvidia?", "a": "Not because of this headline.", "b": "The board's review concerns the CEO's personal relationship, not Nvidia's products, customers or orders. The business story hasn't changed. The useful check is whether any single stock has grown too large in the portfolio.", "n": "Nvidia is about 7% of the S&P 500, so every index-fund investor already owns it."},
      {"q": "Is the market going to keep falling after last week?", "a": "Last week was about politics, not profits.", "b": "Stocks fell on worries that the new Congress slows AI data-center spending, not on weaker results. This morning's earnings point the other way: Constellation beat, raised its outlook and signed a 20-year nuclear power deal with Google.", "n": "Constellation raised 2026 guidance to $12.50–$12.80 a share, from $11.50–$12.50."},
      {"q": "Why are gas prices coming down?", "a": "Oil is falling on hopes of a U.S.–Iran deal.", "b": "Brent dropped 16% last week and is lower again this morning. That leaves more room in household budgets and eases pressure on inflation.", "n": "Gas averages $4.01 a gallon, about 10% below its late-September peak (AAA)."},
      {"q": "Are interest rates going up again?", "a": "Most likely, yes.", "b": "Rate futures price about an 80% chance the Fed hikes in December, and Tuesday's inflation report is the key input. The upside: cash, CDs and short-term Treasuries keep paying more while the Fed stays firm.", "n": "≈80% odds of a quarter-point hike at the Dec. 8–9 meeting."},
    ],
    "table_title": "On the calendar",
    "table": [
      ["Today", "Fed's Goolsbee and Barkin speak", "Both weigh in ahead of Tuesday's CPI"],
      ["After the close", "Trade Desk, Rocket Lab, Hims & Hers, Take-Two", "Plus AST SpaceMobile and Occidental"],
      ["Tue 8:30 a.m.", "October CPI", "Last inflation report before the December Fed meeting"],
    ],
    "note_subject": "What we're watching this week",
    "note": "Hi [Client name],\n\nA quick note before markets open. Last week's pullback was driven by political worries about AI spending, not by weaker company results, and this morning's earnings news has been encouraging. Oil prices are falling on hopes of a U.S.–Iran deal, which is good news for household budgets and inflation.\n\nYou may see headlines about an investigation involving Nvidia's CEO. We're watching it, but it doesn't change our long-term approach. The key event this week is Tuesday's inflation report.\n\nAs always, call me with any questions.\n\n[Advisor name]",
  },
  "pm": {
    "edition": "At the Close",
    "time": "After the bell",
    "subject": "All three indexes up 2%+, and it didn't need Nvidia",
    "oneline": "Stocks clawed back from last week's AI selloff as oil fell 5%, with all three major indexes up more than 2% even as Nvidia dropped 4% on the investigation into its CEO.",
    "stats": [
      {"k": "S&P 500", "v": "7,549.94", "c": "+2.35%", "d": "up"},
      {"k": "Nasdaq", "v": "25,253.14", "c": "+2.74%", "d": "up"},
      {"k": "Dow", "v": "52,389.75", "c": "+2.15%", "d": "up"},
      {"k": "10-yr yield", "v": "4.86%", "c": "flat", "d": ""},
      {"k": "Brent crude", "v": "$92.97", "c": "−5.4%", "d": "dn"},
      {"k": "VIX", "v": "20.02", "c": "−21.9%", "d": "dn"},
    ],
    "happened": [
      "<b>Broadest rally since April.</b> All three major indexes rose at least 2% for the first time since April 5, the Nasdaq exited correction territory, and small caps led with the Russell 2000 up 3.17%.",
      "<b>Oil was the driver.</b> Brent settled down 5.4% after President Trump said fresh strikes on Iran are highly unlikely while talks progress, extending last week's 16% slide.",
      "<b>Nvidia sat it out.</b> It fell 4.3% and was the Dow's worst stock, while AMD (+13.3%), Caterpillar (+7.2%) and Micron (+6.3%) led the rebound.",
    ],
    "means": "The rally didn't need Nvidia. Money rotated within AI rather than leaving it, and lower oil takes pressure off inflation one day before the October CPI report.",
    "qa": [
      {"q": "Should I be worried about the market after last week?", "a": "No.", "b": "Last week's drop came from political fear about AI spending, not from weaker company earnings, and all three major indexes rose more than 2% today for the first time since April. Company profits are still the foundation, and they haven't changed.", "n": "S&P 500 +2.35%; all three major indexes up 2%+ for the first time since April 5."},
      {"q": "Should I sell Nvidia?", "a": "Not because of this headline.", "b": "The board's review concerns the CEO's personal relationship, not Nvidia's products or customers. The rest of the AI group rallied hard today, a sign investors still back the buildout. It's a good moment to check concentration, not to react.", "n": "Nvidia −4.3% while AMD rose 13.3% and Micron 6.3%."},
      {"q": "Why are gas prices dropping?", "a": "Oil is falling on hopes of a U.S.–Iran deal.", "b": "Brent fell 5.4% today after a 16% drop last week, its steepest since the start of the pandemic. That puts money back in household budgets and takes pressure off inflation.", "n": "Gas averages $4.01 a gallon, about 10% below its late-September peak (AAA)."},
      {"q": "Are interest rates going up again?", "a": "Most likely, yes.", "b": "Rate futures price about an 84% chance of a December hike, and tomorrow's inflation report will likely decide it. The upside: cash, CDs and short-term Treasuries keep paying more while the Fed holds firm.", "n": "84% odds of a quarter-point hike at the Dec. 8–9 meeting (CME FedWatch)."},
    ],
    "table_title": "After the bell",
    "table": [
      ["TTD", "+22%", "Revenue beat by 13%; Q4 outlook about 9% above estimates"],
      ["TTWO", "+4%", "Bookings missed, full-year outlook held; GTA VI launches Nov. 19"],
      ["HIMS", "−2%", "Missed on profit and cut its profit outlook, after a ~10% drop today"],
      ["RKLB", "−6.5%", "Record revenue and backlog, but a wider loss after a 25%+ run-up"],
    ],
    "note_subject": "Markets bounced back today",
    "note": "Hi [Client name],\n\nA quick update: all three major U.S. stock indexes rose more than 2% today for the first time since April, helped by a sharp drop in oil prices on hopes of a U.S.–Iran deal. Last week's decline was driven by political worries about AI spending rather than by company earnings, and today's rebound reflects that.\n\nNvidia was the exception, down about 4% on an investigation involving its CEO. We're watching it, but it doesn't change our long-term approach. The key event this week is Tuesday's inflation report.\n\nAs always, call me with any questions.\n\n[Advisor name]",
  },
}

def preview_html(ed="pm", label="Preview of a sample briefing"):
    s = SAMPLE[ed]
    q = s["qa"][1] if ed == "pm" else s["qa"][0]
    stats = s["stats"][:3]
    st = "".join(f'<div class="aip-st"><span>{E(x["k"])}</span><b>{E(x["v"])}</b><i class="{x["d"]}">{E(x["c"])}</i></div>' for x in stats)
    return f'''<div class="ai-preview ready" aria-label="{E(label)}">
        <div class="aip-head"><div class="aip-brand"><img src="/logo-192.png" alt="" width="28" height="28"><span class="w">Alpha<span>Gen</span></span></div><div class="aip-ed"><b>{E(s["edition"])}</b><span>{E(SAMPLE["date"])}</span></div></div>
        <div class="aip-one"><span class="aip-k">Today in one line</span><p>{E(s["oneline"])}</p></div>
        <div class="aip-stats">{st}</div>
        <div class="aip-qa"><span class="aip-k">Your client asks</span><b>“{E(q["q"])}”</b><p><strong>{E(q["a"])}</strong> {E(q["b"])}</p><small><span>Cite</span>{E(q["n"])}</small></div>
        <a class="aip-foot" href="/institutional#sample">Sample edition · {E(SAMPLE["date"])} · <b>See the full briefing →</b></a>
      </div>'''

def sample_json():
    return json.dumps(SAMPLE, ensure_ascii=False).replace("</", "<\\/")
