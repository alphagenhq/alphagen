/* AlphaGen site runtime */
(function(){
"use strict";
const AG = window.AG = {};
const NEWSLETTER = "https://alphagen-newsletter.beehiiv.com";
const RSS_DIRECT = "https://rss.beehiiv.com/feeds/dFFy8T23eL.xml";
const TV_WC = "https://www.tradingview-widget.com/w/en/";

/* ---------- utils ---------- */
const $ = (s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const store={get(k){try{return localStorage.getItem(k)}catch(e){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const strip=h=>{const x=document.createElement("div");x.innerHTML=h||"";return (x.textContent||"").trim().replace(/\s+/g," ")};
const fmtDate=d=>new Date(d).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"});
const fmtDay=s=>{const [y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"})};
const ago=iso=>{const d=new Date(iso),m=Math.round((Date.now()-d)/60000);if(isNaN(m))return"";if(m<1)return"Just now";if(m<60)return m+"m ago";if(m<1440)return Math.round(m/60)+"h ago";return d.toLocaleDateString("en-US",{month:"short",day:"numeric"})};
const live=items=>(items||[]).filter(i=>!i.time||new Date(i.time)<=Date.now()).sort((a,b)=>new Date(b.time)-new Date(a.time));
function getJSON(p){return fetch(p+(p.includes("?")?"&":"?")+"t="+Date.now(),{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.json()})}
function fetchText(urls){return urls.reduce((p,u)=>p.catch(()=>fetch(u,{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.text()}).then(t=>{if(!t||/^\s*<!doctype html/i.test(t))throw 0;return t})),Promise.reject())}
Object.assign(AG,{$, $$, esc, ago, fmtDate, fmtDay, getJSON, live});

/* ---------- TradingView ---------- */
AG.tv=function(id,name,cfg){
  const el=document.getElementById(id); if(!el) return;
  const s=document.createElement("script");
  s.src="https://s3.tradingview.com/external-embedding/embed-widget-"+name+".js"; s.async=true; s.type="text/javascript";
  s.textContent=JSON.stringify(Object.assign({colorTheme:"dark",isTransparent:true,locale:"en"},cfg));
  el.appendChild(s);
};
const wcLoaded={};
AG.wc=function(name){if(wcLoaded[name])return;wcLoaded[name]=1;const s=document.createElement("script");s.type="module";s.src=TV_WC+name+".js";document.head.appendChild(s)};
AG.mini=function(symbol){const el=document.createElement("tv-mini-chart");el.setAttribute("symbol",symbol);el.setAttribute("theme","dark");el.setAttribute("transparent","");AG.wc("tv-mini-chart");return el};
if($("tv-ticker-tape")) AG.wc("tv-ticker-tape");
if($("tv-mini-chart")) AG.wc("tv-mini-chart");

/* ---------- nav ---------- */
const menu=$(".menu-btn"); if(menu){menu.addEventListener("click",()=>{const n=$(".nav");const o=n.classList.toggle("open");menu.setAttribute("aria-expanded",o)})}

/* ---------- market status (NYSE) ---------- */
const HOLIDAYS=new Set(["2026-11-26","2026-12-25","2027-01-01","2027-01-18","2027-02-15","2027-03-26","2027-05-31","2027-06-18","2027-07-05","2027-09-06","2027-11-25","2027-12-24"]);
const EARLY=new Set(["2026-11-27","2026-12-24","2027-11-26"]);
function nyParts(d){const p={};new Intl.DateTimeFormat("en-US",{timeZone:"America/New_York",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",weekday:"short",hour12:false}).formatToParts(d).forEach(x=>p[x.type]=x.value);const h=+p.hour%24;return {date:`${p.year}-${p.month}-${p.day}`,wd:p.weekday,mins:h*60+ +p.minute,secs:+p.second}}
const isTradingDay=p=>!["Sat","Sun"].includes(p.wd)&&!HOLIDAYS.has(p.date);
function nextOpen(now){for(let i=0;i<10;i++){const d=new Date(now.getTime()+i*86400000);const p=nyParts(d);if(i===0&&p.mins>=570)continue;if(isTradingDay(p))return {p,i}}return null}
const dur=m=>{m=Math.max(0,Math.round(m));const h=Math.floor(m/60),mm=m%60;return (h?h+"h ":"")+mm+"m"};
function marketStatus(){
  const now=new Date(), p=nyParts(now), close=EARLY.has(p.date)?780:960, td=isTradingDay(p);
  if(td&&p.mins>=570&&p.mins<close) return {cls:"open",label:"NYSE open",sub:"Closes in "+dur(close-p.mins-p.secs/60)};
  if(td&&p.mins>=240&&p.mins<570) return {cls:"pre",label:"Pre-market",sub:"Opens in "+dur(570-p.mins-p.secs/60)};
  if(td&&p.mins>=close&&p.mins<1200) return {cls:"post",label:"After hours",sub:"Closed at "+(close===780?"1:00":"4:00")+" p.m. ET"};
  const n=nextOpen(now); const when=n?(n.i===0?"today":n.i===1?"tomorrow":new Date(n.p.date+"T12:00:00").toLocaleDateString("en-US",{weekday:"long"})):"";
  return {cls:"closed",label:"Market closed",sub:n?"Opens "+when+" 9:30 a.m. ET":""};
}
function tick(){
  const el=$("#mkt"); if(el){const s=marketStatus();el.className="mkt "+s.cls;el.innerHTML="<i></i><b>"+s.label+"</b> · "+s.sub}
  const c=$("#clock"); if(c) c.textContent=new Date().toLocaleTimeString("en-US",{timeZone:"America/New_York",hour:"numeric",minute:"2-digit",second:"2-digit"})+" ET";
}
tick(); setInterval(tick,1000);
AG.marketStatus=marketStatus;

/* ---------- FOMC ---------- */
const FOMC=[["2026-10-27","2026-10-28"],["2026-12-08","2026-12-09"],["2027-01-26","2027-01-27"],["2027-03-16","2027-03-17"],["2027-04-27","2027-04-28"],["2027-06-08","2027-06-09"],["2027-07-27","2027-07-28"],["2027-09-14","2027-09-15"],["2027-10-26","2027-10-27"],["2027-12-07","2027-12-08"]];
AG.nextFomc=function(){const today=nyParts(new Date()).date;const m=FOMC.find(([a,b])=>b>=today);if(!m)return null;const [y,mo,d]=m[1].split("-").map(Number);const days=Math.ceil((new Date(y,mo-1,d,14)-Date.now())/86400000);return {start:m[0],end:m[1],days}};
$$("[data-fomc]").forEach(el=>{const f=AG.nextFomc();if(!f)return;const mon=new Date(f.start+"T12:00:00").toLocaleDateString("en-US",{month:"short"});const lab=mon+" "+(+f.start.slice(8))+"–"+(+f.end.slice(8));el.querySelectorAll("[data-fomc-date]").forEach(e=>e.textContent=lab);el.querySelectorAll("[data-fomc-cd]").forEach(cd=>cd.textContent=f.days<=0?"Decision today, 2:00 p.m. ET":f.days===1?"Decision tomorrow, 2:00 p.m. ET":"Decision in "+f.days+" days, "+fmtDay(f.end)+" at 2:00 p.m. ET")});

/* ---------- subscribe popup ---------- */
(function(){
  const modal=$("#sub-modal"); if(!modal) return; let last=null;
  const open=()=>{last=document.activeElement;modal.hidden=false;document.body.classList.add("locked");setTimeout(()=>{const g=modal.querySelector("[data-sub-go]");g&&g.focus()},50)};
  const close=()=>{modal.hidden=true;document.body.classList.remove("locked");store.set("ag_sub_seen",String(Date.now()));if(last&&last.focus)last.focus()};
  $$("[data-open-sub]").forEach(b=>b.addEventListener("click",open));
  $$("[data-close-sub]").forEach(b=>b.addEventListener("click",close));
  modal.addEventListener("click",e=>{if(e.target===modal)close()});
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!modal.hidden)close()});
  $$("[data-sub-go]").forEach(a=>a.addEventListener("click",()=>{store.set("ag_subscribed","1");if(!modal.hidden)close()}));
  const seen=+store.get("ag_sub_seen")||0;
  if(!store.get("ag_subscribed")&&Date.now()-seen>3*864e5) setTimeout(()=>{if(modal.hidden)open()},1400);
})();

/* ---------- Wire ---------- */
let WIRE=null, wireSeen=new Set(), wireFirst=true;
const wireViews=$$("[data-wire]").map(el=>({el,limit:+el.dataset.limit||40,tags:(el.dataset.tags||"").split(",").filter(Boolean),filter:"all",q:""}));
function renderWire(v){
  let items=live(WIRE&&WIRE.items);
  if(v.tags.length) items=items.filter(i=>v.tags.includes((i.tag||"").toUpperCase()));
  if(v.filter!=="all") items=items.filter(i=>(i.tag||"").toUpperCase()===v.filter);
  if(v.q){const q=v.q.toLowerCase();items=items.filter(i=>(i.headline+" "+i.take+" "+(i.ticker||"")).toLowerCase().includes(q))}
  items=items.slice(0,v.limit);
  if(!items.length){v.el.innerHTML='<div class="empty"><b>'+(WIRE?"Nothing here yet.":"Loading the AlphaGen Wire…")+'</b>New pieces post every few minutes through the trading day.</div>';return}
  v.el.innerHTML="";
  items.forEach(it=>{
    const fresh=(Date.now()-new Date(it.time))<60*60000;
    const a=document.createElement("article"); a.className="wire-item"+(!wireFirst&&!wireSeen.has(it.id)?" enter":"");
    a.innerHTML='<div class="wire-meta"><span class="tag">'+esc(it.tag||"Markets")+'</span>'+(it.ticker?'<span class="tag tk">'+esc(it.ticker.split(":").pop())+'</span>':"")+'<span class="'+(fresh?"new":"")+'">'+(fresh?"● ":"")+esc(ago(it.time))+'</span></div><h3>'+esc(it.headline)+'</h3><p>'+esc(it.take)+'</p>'+(it.source_url?'<a class="src" href="'+esc(it.source_url)+'" target="_blank" rel="noopener">Source: '+esc(it.source_name||"Official source")+' →</a>':"");
    v.el.appendChild(a);
  });
}
function drawWire(){wireViews.forEach(renderWire);const items=live(WIRE&&WIRE.items);items.forEach(i=>wireSeen.add(i.id));wireFirst=false;
  $$("[data-wire-updated]").forEach(e=>{if(items[0])e.textContent="Latest "+ago(items[0].time)});
  $$("[data-wire-count]").forEach(e=>{const today=nyParts(new Date()).date;e.textContent=items.filter(i=>nyParts(new Date(i.time)).date===today).length});
}
function loadWire(){return getJSON("/wire.json").then(d=>{WIRE=d;drawWire()}).catch(()=>{if(!WIRE){WIRE={items:[]};drawWire()}})}
if(wireViews.length||$("[data-wire-count]")){loadWire();setInterval(loadWire,60000);setInterval(drawWire,30000)}
$$("[data-wire-filters]").forEach(bar=>{
  const v=wireViews.find(w=>w.el.id===bar.dataset.wireFilters); if(!v) return;
  bar.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{v.filter=b.dataset.f;bar.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",x===b?"true":"false"));renderWire(v)}));
  const s=bar.querySelector("input"); if(s) s.addEventListener("input",()=>{v.q=s.value.trim();renderWire(v)});
});

/* ---------- Movers ---------- */
let MOVERS=null, spotI=0, spotTimer=null;
function moverCard(m){
  const c=document.createElement("article"); c.className="mover";
  const mc=document.createElement("div"); mc.className="mc"; mc.appendChild(AG.mini(m.ticker)); c.appendChild(mc);
  const b=document.createElement("div"); b.className="mb";
  b.innerHTML='<div class="row"><span class="tag tk">'+esc(m.ticker.split(":").pop())+'</span><span>'+esc(m.name||"")+'</span><span>· '+esc(ago(m.time))+'</span></div><h3>'+esc(m.headline)+'</h3><p>'+esc(m.thesis)+'</p>'+(m.source_url?'<a class="src" href="'+esc(m.source_url)+'" target="_blank" rel="noopener">Catalyst source: '+esc(m.source_name||"Filing")+' →</a>':"");
  c.appendChild(b); return c;
}
function renderSpot(el){
  const items=live(MOVERS&&MOVERS.items); if(!items.length){el.innerHTML='<div class="empty" style="padding:28px"><b>Movers update through the session.</b>AlphaGen theses on the day\'s biggest moves appear here once the market is moving.</div>';return}
  spotI=spotI%items.length; const m=items[spotI];
  el.innerHTML='<div class="chart"></div><div class="body"><div class="row" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap"><span class="eyebrow">Mover spotlight</span><span class="tag tk">'+esc(m.ticker.split(":").pop())+'</span><span style="font-family:var(--mono);font-size:.7rem;color:var(--mute)">'+esc(m.name||"")+'</span></div><h3>'+esc(m.headline)+'</h3>'+(m.catalyst?'<div class="cat"><b>CATALYST</b>'+esc(m.catalyst)+'</div>':"")+'<p>'+esc(m.thesis)+'</p><div class="foot"><span>'+(m.source_url?'<a href="'+esc(m.source_url)+'" target="_blank" rel="noopener" style="color:var(--signal-2);text-decoration:none">Source: '+esc(m.source_name||"Filing")+' →</a>':"")+'</span><div class="dots"></div></div></div>';
  el.querySelector(".chart").appendChild(AG.mini(m.ticker));
  const dots=el.querySelector(".dots");
  items.forEach((_,i)=>{const d=document.createElement("button");d.type="button";d.setAttribute("aria-label","Show mover "+(i+1));d.setAttribute("aria-current",i===spotI?"true":"false");d.addEventListener("click",()=>{spotI=i;renderSpot(el);restart(el)});dots.appendChild(d)});
}
function restart(el){clearInterval(spotTimer);spotTimer=setInterval(()=>{spotI++;renderSpot(el)},9000)}
function drawMovers(){
  $$("[data-spot]").forEach(el=>{renderSpot(el);restart(el)});
  $$("[data-movers]").forEach(el=>{
    const items=live(MOVERS&&MOVERS.items).slice(0,+el.dataset.limit||24); el.innerHTML="";
    if(!items.length){el.innerHTML='<div class="empty" style="grid-column:1/-1"><b>No mover theses yet this session.</b>They post as the day\'s biggest moves get a verified catalyst.</div>';return}
    items.forEach(m=>el.appendChild(moverCard(m)));
  });
  $$("[data-movers-updated]").forEach(e=>{if(MOVERS&&MOVERS.updated)e.textContent="Updated "+ago(MOVERS.updated)});
}
function loadMovers(){return getJSON("/movers.json").then(d=>{const sig=JSON.stringify(d.items.map(i=>i.id||i.ticker));if(!MOVERS||sig!==JSON.stringify(MOVERS.items.map(i=>i.id||i.ticker))){MOVERS=d;drawMovers()}else MOVERS=d}).catch(()=>{if(!MOVERS){MOVERS={items:[]};drawMovers()}})}
if($("[data-spot]")||$("[data-movers]")){loadMovers();setInterval(loadMovers,120000)}

/* ---------- Research: newsletter + AlphaGen Notes ---------- */
const FALLBACK_POSTS=[
  {title:"Another 2008?",desc:"AlphaGen Macroview | Oct 8/9th, 2026",link:NEWSLETTER+"/p/another-2008",date:"2026-10-09T12:30:00Z",img:""},
  {title:"The next decade of markets may be defined by one key thing: power.",desc:"AlphaGen Market Insights",link:NEWSLETTER+"/p/the-next-decade-of-markets-may-be-defined-by-one-key-thing-power",date:"2026-10-08T14:31:00Z",img:"https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/23b0a45b-c3f1-43cf-9f0e-b77200e1be0f/IMG_2477__1_.png?t=1791407249"},
  {title:"The AI Trade is Entering a Capital-Infrastructure Phase",desc:"AlphaGen Daily Watchlist",link:NEWSLETTER+"/p/the-ai-trade-is-entering-a-capital-infrastructure-phase",date:"2026-10-08T02:30:00Z",img:"https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/407ed160-e598-4180-85a7-b2c105c7d75a/IMG_2466.png?t=1791388221"},
  {title:"Short-term Treasury markets are sending a signal worth watching.",desc:"T-Bills Are Demanding More Yield",link:NEWSLETTER+"/p/short-term-treasury-markets-are-sending-a-signal-worth-watching",date:"2026-10-07T14:15:00Z",img:"https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/27551973-da80-4da2-a8b3-c392b047562c/IMG_2454__1_.png?t=1791338995"},
  {title:"Market Signals We Are Watching",desc:"October 6th Signals",link:NEWSLETTER+"/p/market-signals-we-are-watching",date:"2026-10-07T01:55:00Z",img:"https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/4c1c91a9-1834-46fe-8f46-7069994ab014/IMG_2434__1_.png?t=1791337647"}
];
const KEYS={debt:/debt|treasur|t-bill|bills?\b|yield|bond|rates?\b|fed\b|fomc|sofr|ois|curve|credit|fiscal|deficit|money.market|2008/i,equities:/equit|stock|earning|eps|s&p|nasdaq|\bai\b|capex|sector|valuation|m&a|ipo|watchlist/i};
const topicOf=t=>KEYS.debt.test(t)?"debt":KEYS.equities.test(t)?"equities":"macro";
const LABEL={debt:"Debt & Rates",equities:"Equities",macro:"Macro"};
const TAG2TOPIC={RATES:"debt",DEBT:"debt",FED:"debt",EQUITIES:"equities",EARNINGS:"equities",MACRO:"macro",COMMODITIES:"macro",FX:"macro"};
let POSTS=FALLBACK_POSTS.map(p=>({kind:"newsletter",title:p.title,desc:p.desc,link:p.link,date:p.date,img:p.img,topic:topicOf(p.title+" "+p.desc)}));
let NOTES=[];
function parseRSS(xml){
  const doc=new DOMParser().parseFromString(xml,"text/xml");
  return [...doc.getElementsByTagName("item")].map(it=>{
    const g=n=>{const e=it.getElementsByTagName(n)[0];return e?e.textContent.trim():""};
    const enc=it.getElementsByTagNameNS("*","encoded")[0]; const html=enc?enc.textContent:"";
    const m=html.match(/<img[^>]+src=["']([^"']+)["']/i);
    const p={kind:"newsletter",title:g("title"),link:g("link"),date:g("pubDate"),desc:strip(g("description")).slice(0,240),img:m?m[1].replace(/&amp;/g,"&"):""};
    p.topic=topicOf(p.title+" "+p.desc); return p;
  }).filter(p=>p.title&&p.link);
}
const researchViews=$$("[data-research]").map(el=>({el,limit:+el.dataset.limit||8,src:el.dataset.research||"all",filter:el.dataset.topic||"all"}));
function allResearch(src){
  let a=[]; if(src!=="notes") a=a.concat(POSTS); if(src!=="newsletter") a=a.concat(NOTES);
  return a.sort((x,y)=>new Date(y.date)-new Date(x.date));
}
function renderResearch(v){
  let items=allResearch(v.src); if(v.filter!=="all") items=items.filter(p=>p.topic===v.filter);
  items=items.slice(0,v.limit); v.el.innerHTML="";
  if(!items.length){v.el.innerHTML='<div class="empty"><b>Nothing in this category yet.</b>New AlphaGen research appears here as soon as it\'s published.</div>';return}
  items.forEach(p=>{
    const a=document.createElement("a"); a.className="note"; a.href=p.link; if(p.kind==="newsletter"){a.target="_blank";a.rel="noopener"}
    const th=p.img?'<img src="'+esc(p.img)+'" alt="" loading="lazy" onerror="this.src=\'/logo-192.png\';this.className=\'lg\'">':(p.kind==="note"?'<span class="glyph">AG</span>':'<img class="lg" src="/logo-192.png" alt="">');
    a.innerHTML='<div class="th">'+th+'</div><div><div class="meta"><span><span class="tag">'+esc(LABEL[p.topic])+'</span> <span class="tag tk">'+(p.kind==="note"?"AlphaGen Note":"Newsletter")+'</span></span><span>'+esc(fmtDate(p.date))+'</span></div><h3>'+esc(p.title)+'</h3><p>'+esc(p.desc||"")+'</p></div>';
    v.el.appendChild(a);
  });
}
function renderFeature(){
  const el=$("#feature"); if(!el) return; const p=allResearch("all")[0]; if(!p) return;
  el.href=p.link; if(p.kind==="newsletter"){el.target="_blank";el.rel="noopener"}else{el.removeAttribute("target")}
  $("#feature-title").textContent=p.title; $("#feature-desc").textContent=p.desc||""; $("#feature-tag").textContent=LABEL[p.topic]; $("#feature-date").textContent=fmtDate(p.date);
  $("#feature-kind").textContent=p.kind==="note"?"Latest AlphaGen Note":"Latest AlphaGen thesis";
  const box=$("#feature-img");
  if(p.img){box.innerHTML="";const im=new Image();im.alt="";im.src=p.img;im.onerror=()=>{box.innerHTML='<div class="ph"><img src="/logo-192.png" alt=""></div>'};box.appendChild(im)}
  else box.innerHTML='<div class="ph"><img src="/logo-192.png" alt=""></div>';
}
function drawResearch(){researchViews.forEach(renderResearch);renderFeature()}
$$("[data-research-filters]").forEach(bar=>{const v=researchViews.find(r=>r.el.id===bar.dataset.researchFilters);if(!v)return;bar.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{v.filter=b.dataset.f;bar.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",x===b?"true":"false"));renderResearch(v)}))});
function loadFeed(){
  return fetchText(["/feed.xml",RSS_DIRECT]).then(t=>{const items=parseRSS(t);if(items.length){POSTS=items;drawResearch()}}).catch(()=>{});
}
function loadNotes(){
  return getJSON("/notes.json").then(d=>{NOTES=live(d.items).map(n=>({kind:"note",id:n.id,title:n.title,desc:n.dek,link:"/article?id="+encodeURIComponent(n.id),date:n.time,img:"",topic:TAG2TOPIC[(n.tag||"").toUpperCase()]||"macro",raw:n}));drawResearch()}).catch(()=>{});
}
if(researchViews.length||$("#feature")){drawResearch();loadFeed();loadNotes();setInterval(loadFeed,5*60000);setInterval(loadNotes,2*60000)}

/* ---------- Article reader ---------- */
(function(){
  const el=$("#article"); if(!el) return;
  const id=new URLSearchParams(location.search).get("id");
  getJSON("/notes.json").then(d=>{
    const items=live(d.items); const n=items.find(x=>x.id===id)||(!id&&items[0]);
    if(!n){el.innerHTML='<div class="empty"><b>We couldn\'t find that note.</b><a href="/research" style="color:var(--signal-2)">Browse all AlphaGen research →</a></div>';return}
    document.title=n.title+" | AlphaGen Research";
    const body=(n.body||[]).map(b=>typeof b==="string"?"<p>"+esc(b)+"</p>":b.h?"<h2>"+esc(b.h)+"</h2>":"").join("");
    const kp=(n.key_points||[]).length?'<div class="kp"><span class="eyebrow">Key points</span><ul>'+n.key_points.map(k=>"<li>"+esc(k)+"</li>").join("")+"</ul></div>":"";
    const src=(n.sources||[]).length?'<div class="sources"><b>Sources</b><ul>'+n.sources.map(s=>'<li><a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(s.name)+"</a></li>").join("")+"</ul></div>":"";
    el.innerHTML='<a href="/research" style="font-family:var(--mono);font-size:.72rem;color:var(--signal-2);text-decoration:none">← All research</a><div style="margin-top:18px"><span class="tag">'+esc(n.tag||"Macro")+'</span> <span class="tag tk">AlphaGen Note</span></div><h1>'+esc(n.title)+'</h1><p class="dek">'+esc(n.dek||"")+'</p><div class="byline"><span>AlphaGen Research</span><span>'+esc(new Date(n.time).toLocaleString("en-US",{month:"short",day:"numeric",year:"numeric",hour:"numeric",minute:"2-digit",timeZone:"America/New_York"}))+' ET</span></div>'+kp+'<div class="content">'+body+'</div>'+src+'<p class="disc">For informational purposes only. Not investment advice.</p>';
  }).catch(()=>{el.innerHTML='<div class="empty"><b>This note is loading slowly.</b>Refresh in a moment.</div>'});
})();

/* ---------- Treasury curve, key levels, debt ---------- */
const TENORS=[["BC_1MONTH","1M"],["BC_3MONTH","3M"],["BC_6MONTH","6M"],["BC_1YEAR","1Y"],["BC_2YEAR","2Y"],["BC_3YEAR","3Y"],["BC_5YEAR","5Y"],["BC_7YEAR","7Y"],["BC_10YEAR","10Y"],["BC_20YEAR","20Y"],["BC_30YEAR","30Y"]];
const FALLBACK_CURVE=[
  {date:"2026-10-01",v:{BC_1MONTH:4.06,BC_3MONTH:4.17,BC_6MONTH:4.27,BC_1YEAR:4.44,BC_2YEAR:4.78,BC_3YEAR:4.91,BC_5YEAR:5.01,BC_7YEAR:5.12,BC_10YEAR:5.24,BC_20YEAR:5.64,BC_30YEAR:5.61}},
  {date:"2026-10-13",v:{BC_1MONTH:4.10,BC_3MONTH:4.26,BC_6MONTH:4.34,BC_1YEAR:4.48,BC_2YEAR:4.79,BC_3YEAR:4.90,BC_5YEAR:5.00,BC_7YEAR:5.11,BC_10YEAR:5.21,BC_20YEAR:5.60,BC_30YEAR:5.56}}
];
const ym=d=>d.getFullYear()+String(d.getMonth()+1).padStart(2,"0");
function parseCurve(xml){const doc=new DOMParser().parseFromString(xml,"application/xml");return [...doc.getElementsByTagNameNS("*","properties")].map(p=>{const o={};[...p.children].forEach(c=>o[c.localName]=c.textContent);if(!o.NEW_DATE)return null;const v={};TENORS.forEach(([k])=>{const n=parseFloat(o[k]);if(!isNaN(n))v[k]=n});return {date:o.NEW_DATE.slice(0,10),v}}).filter(Boolean)}
const bp=x=>(x>0?"+":"")+Math.round(x)+"bp";
const set=(id,t)=>{const e=document.getElementById(id);if(e)e.textContent=t};
function setChg(id,now,prev){const el=document.getElementById(id);if(!el)return;if(prev==null||now==null){el.innerHTML="&nbsp;";return}const d=(now-prev)*100;el.textContent=(Math.round(d)===0?"unch":bp(d))+" d/d";el.className="d num "+(d>0?"up":d<0?"down":"")}
function renderCurve(rows,daily){
  rows=rows.slice().sort((a,b)=>a.date<b.date?-1:1);
  const now=rows[rows.length-1], prior=daily!==false&&rows.length>1?rows[rows.length-2]:null;
  const t=new Date(now.date);t.setDate(t.getDate()-30);const tgt=t.toISOString().slice(0,10);
  let past=rows[0];rows.forEach(r=>{if(r.date<=tgt)past=r});if(past===now&&rows.length>1)past=rows[rows.length-2];
  const V=(r,k)=>r&&r.v[k]!=null?r.v[k]:null;
  [["lv-3m","BC_3MONTH"],["lv-2y","BC_2YEAR"],["lv-10y","BC_10YEAR"],["lv-30y","BC_30YEAR"]].forEach(([id,k])=>{const x=V(now,k);if(x!=null){set(id,x.toFixed(2)+"%");setChg(id+"-d",x,V(prior,k))}});
  const s=(V(now,"BC_10YEAR")-V(now,"BC_2YEAR"))*100; set("lv-2s10s",bp(s));
  if(prior){const ps=(V(prior,"BC_10YEAR")-V(prior,"BC_2YEAR"))*100,d=s-ps,el=document.getElementById("lv-2s10s-d");if(el){el.textContent=(Math.round(d)===0?"unch":bp(d))+" d/d";el.className="d num "+(d>0?"up":d<0?"down":"")}}
  set("levels-note","U.S. Treasury par yield curve rates, close of "+fmtDay(now.date)+". Debt: Treasury, Debt to the Penny.");
  set("curve-date",fmtDay(now.date)); set("lg-now",fmtDay(now.date)); set("lg-prev",fmtDay(past.date));
  const chart=document.getElementById("curve-chart"); if(!chart) return;
  const ks=TENORS.filter(([k])=>V(now,k)!=null), vals=ks.flatMap(([k])=>[V(now,k),V(past,k)]).filter(x=>x!=null);
  let lo=Math.floor((Math.min(...vals)-.05)*4)/4, hi=Math.ceil((Math.max(...vals)+.05)*4)/4; if(hi-lo<.5)hi=lo+.5;
  const W=720,H=300,L=46,R=16,T=18,B=34,x=i=>L+i*(W-L-R)/(ks.length-1),y=v=>T+(hi-v)*(H-T-B)/(hi-lo);
  let g="";for(let t=lo;t<=hi+1e-9;t+=.25){g+=`<line x1="${L}" x2="${W-R}" y1="${y(t)}" y2="${y(t)}" stroke="#1c3354"/><text x="${L-8}" y="${y(t)+4}" text-anchor="end" font-family="IBM Plex Mono,monospace" font-size="11" fill="#6b82a3">${t.toFixed(2)}</text>`}
  ks.forEach(([k,l],i)=>{g+=`<text x="${x(i)}" y="${H-10}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="11" fill="#6b82a3">${l}</text>`});
  const path=r=>ks.map(([k],i)=>V(r,k)==null?null:`${x(i)},${y(V(r,k))}`).filter(Boolean).join(" ");
  const dots=ks.map(([k],i)=>`<circle cx="${x(i)}" cy="${y(V(now,k))}" r="3.2" fill="#4c8dff" stroke="#07121f" stroke-width="1.5"/>`).join("");
  const ti=ks.findIndex(([k])=>k==="BC_10YEAR");
  const lab=ti>=0?`<text x="${x(ti)}" y="${y(V(now,"BC_10YEAR"))-12}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="11.5" fill="#eef3fb">10Y ${V(now,"BC_10YEAR").toFixed(2)}%</text>`:"";
  chart.innerHTML=`<svg viewBox="0 0 ${W} ${H}"><defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4c8dff" stop-opacity=".22"/><stop offset="1" stop-color="#4c8dff" stop-opacity="0"/></linearGradient></defs>${g}<polygon points="${L},${H-B} ${path(now)} ${W-R},${H-B}" fill="url(#cg)"/><polyline points="${path(past)}" fill="none" stroke="#6b82a3" stroke-width="1.6" stroke-dasharray="5 4"/><polyline points="${path(now)}" fill="none" stroke="#4c8dff" stroke-width="2.4" stroke-linejoin="round"/>${dots}${lab}</svg>`;
  const tb=document.getElementById("ytable"); if(!tb) return;
  const sh=r=>fmtDay(r.date).replace(/, \d{4}$/,"");
  tb.innerHTML="<tr><th>Tenor</th>"+ks.map(([,l])=>`<th>${l}</th>`).join("")+"</tr>"+[now,past].map(r=>"<tr><td>"+sh(r)+"</td>"+ks.map(([k])=>`<td>${V(r,k)!=null?V(r,k).toFixed(2):"–"}</td>`).join("")+"</tr>").join("")+"<tr><td>Chg (bp)</td>"+ks.map(([k])=>{const d=(V(now,k)-V(past,k))*100;return `<td class="${d>0?"up":d<0?"down":""}">${isNaN(d)?"–":(d>0?"+":"")+Math.round(d)}</td>`}).join("")+"</tr>";
}
function loadCurve(){
  const d=new Date(),p=new Date(d.getFullYear(),d.getMonth()-1,1);
  const get=m=>fetchText(["/api/yields/"+m]).then(parseCurve).catch(()=>[]);
  Promise.all([get(ym(p)),get(ym(d))]).then(([a,b])=>{const r=[...a,...b];if(r.length>=2)renderCurve(r)});
}
if($("#levels")||$("#curve-chart")){renderCurve(FALLBACK_CURVE,false);loadCurve();setInterval(loadCurve,30*60000)}
function loadDebt(){
  fetchText(["/api/debt"]).then(t=>JSON.parse(t)).then(j=>{
    const r=j.data&&j.data[0]; if(!r) return; const T=n=>"$"+(n/1e12).toFixed(2)+"T", tot=+r.tot_pub_debt_out_amt;
    const dt=document.getElementById("debt-total"); if(dt) dt.innerHTML="$"+(tot/1e12).toFixed(2)+"<small>trillion</small>";
    set("debt-public",T(+r.debt_held_public_amt)); set("debt-intra",T(+r.intragov_hold_amt));
    set("debt-date","As of "+fmtDay(r.record_date)+" · U.S. Treasury, Debt to the Penny");
    set("lv-debt",T(tot)); set("lv-debt-d","as of "+fmtDay(r.record_date).replace(/, \d{4}$/,""));
  }).catch(()=>{});
}
if($("#lv-debt")||$("#debt-total")){loadDebt();setInterval(loadDebt,60*60000)}
})();
