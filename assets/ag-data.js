/* AlphaGen data modules: Macro Dashboard, Treasury auctions, Charts, Earnings */
(function(){
"use strict";
const AG=window.AG||{}; const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmtDay=s=>{const [y,m,d]=s.slice(0,10).split("-").map(Number);return new Date(y,m-1,d).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"})};
const shortDay=s=>fmtDay(s).replace(/, \d{4}$/,"");
const getJSON=p=>fetch(p+(p.includes("?")?"&":"?")+"t="+Date.now(),{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.json()});
const live=items=>(items||[]).filter(i=>!i.time||new Date(i.time)<=Date.now()).sort((a,b)=>new Date(b.time)-new Date(a.time));
const C={paper:"#eef3fb",steel:"#93a7c4",mute:"#6b82a3",rule:"#1c3354",signal:"#4c8dff",up:"#36c98b",down:"#ff6b6b",ink:"#07121f",panel:"#0e1f36"};
const SERIES_COLORS=["#4c8dff","#f2b84b","#36c98b","#c58cff","#ff6b6b"];

/* ---------- FRED (via /api/fred proxy) ---------- */
const fredCache={};
function fred(id,start){
  const k=id+start; if(fredCache[k]) return fredCache[k];
  return fredCache[k]=fetch("/api/fred/"+id+"/"+start,{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.text()}).then(t=>{
    if(/^\s*</.test(t)) throw 0;
    return t.trim().split(/\r?\n/).slice(1).map(l=>{const [d,v]=l.split(",");return {d,v:parseFloat(v)}}).filter(o=>o.d&&!isNaN(o.v));
  });
}
function transform(obs,t){
  if(t==="yoy"){const m=new Map(obs.map(o=>[o.d,o.v]));return obs.map(o=>{const [y,mo,d]=o.d.split("-");const p=m.get((+y-1)+"-"+mo+"-"+d);return p?{d:o.d,v:(o.v/p-1)*100}:null}).filter(Boolean)}
  if(t==="diff") return obs.slice(1).map((o,i)=>({d:o.d,v:o.v-obs[i].v}));
  if(t==="k") return obs.map(o=>({d:o.d,v:o.v/1000}));
  if(t&&t.startsWith("div:")){const d=+t.slice(4);return obs.map(o=>({d:o.d,v:o.v/d}))}
  return obs;
}
AG.fred=fred; AG.transform=transform;

/* ---------- sparkline ---------- */
function spark(pts,color){
  if(pts.length<2) return "";
  const W=220,H=54,P=3, vs=pts.map(p=>p.v), lo=Math.min(...vs), hi=Math.max(...vs), r=hi-lo||1;
  const x=i=>P+i*(W-2*P)/(pts.length-1), y=v=>H-P-(v-lo)*(H-2*P)/r;
  const line=pts.map((p,i)=>x(i).toFixed(1)+","+y(p.v).toFixed(1)).join(" ");
  const id="g"+Math.random().toString(36).slice(2,8);
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".25"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs><polygon points="${P},${H} ${line} ${W-P},${H}" fill="url(#${id})"/><polyline points="${line}" fill="none" stroke="${color}" stroke-width="1.6" vector-effect="non-scaling-stroke"/><circle cx="${x(pts.length-1)}" cy="${y(pts[pts.length-1].v)}" r="2.6" fill="${color}"/></svg>`;
}

/* ---------- Macro Dashboard ---------- */
const SETS={core:[
 {g:"Inflation",items:[
  {id:"CPIAUCSL",n:"CPI inflation",t:"yoy",u:"%",good:"down",lb:3,note:"Headline CPI, year over year"},
  {id:"CPILFESL",n:"Core CPI",t:"yoy",u:"%",good:"down",lb:3,note:"Ex food & energy, y/y"},
  {id:"PCEPILFE",n:"Core PCE",t:"yoy",u:"%",good:"down",lb:3,note:"The Fed's preferred gauge, y/y"},
  {id:"T5YIE",n:"5Y breakeven",t:"lvl",u:"%",good:"down",lb:63,note:"Market inflation expectations"}]},
 {g:"Labor",items:[
  {id:"UNRATE",n:"Unemployment rate",t:"lvl",u:"%",good:"down",lb:3,note:"BLS household survey"},
  {id:"PAYEMS",n:"Payroll gains",t:"diff",u:"k",good:"up",lb:3,note:"Monthly change, thousands"},
  {id:"ICSA",n:"Initial jobless claims",t:"k",u:"k",good:"down",lb:13,note:"Weekly, thousands"}]},
 {g:"Growth",items:[
  {id:"GDPNOW",n:"GDPNow",t:"lvl",u:"%",good:"up",lb:1,note:"Atlanta Fed real-time GDP estimate"},
  {id:"INDPRO",n:"Industrial production",t:"yoy",u:"%",good:"up",lb:3,note:"Year over year"},
  {id:"RSAFS",n:"Retail sales",t:"yoy",u:"%",good:"up",lb:3,note:"Nominal, year over year"}]},
 {g:"Policy & rates",items:[
  {id:"DFEDTARU",n:"Fed funds target (upper)",t:"lvl",u:"%",lb:63,note:"FOMC policy rate"},
  {id:"DGS10",n:"10-year Treasury",t:"lvl",u:"%",lb:63,note:"Constant maturity"},
  {id:"DFII10",n:"10-year real yield",t:"lvl",u:"%",lb:63,note:"TIPS, constant maturity"},
  {id:"T10Y2Y",n:"2s10s spread",t:"lvl",u:"pp",lb:63,note:"10Y minus 2Y"}]},
 {g:"Credit & conditions",items:[
  {id:"BAMLH0A0HYM2",n:"High-yield spread",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA US HY OAS"},
  {id:"BAMLC0A0CM",n:"Investment-grade spread",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA US Corporate OAS"},
  {id:"NFCI",n:"Financial conditions",t:"lvl",u:"",good:"down",lb:13,note:"Chicago Fed NFCI; below 0 = looser than average"},
  {id:"VIXCLS",n:"VIX",t:"lvl",u:"",good:"down",lb:63,note:"Implied S&P 500 volatility"}]},
 {g:"Dollar & energy",items:[
  {id:"DTWEXBGS",n:"Broad dollar index",t:"lvl",u:"",lb:63,note:"Fed nominal broad index"},
  {id:"DCOILWTICO",n:"WTI crude",t:"lvl",u:"$",lb:63,note:"Dollars per barrel, spot"}]}
],
fed:[
 {g:"Policy rate",items:[
  {id:"DFEDTARU",n:"Target range, upper",t:"lvl",u:"%",lb:63,note:"FOMC target, upper bound"},
  {id:"DFEDTARL",n:"Target range, lower",t:"lvl",u:"%",lb:63,note:"FOMC target, lower bound"},
  {id:"DFF",n:"Effective fed funds",t:"lvl",u:"%",lb:63,note:"Daily effective rate"},
  {id:"SOFR",n:"SOFR",t:"lvl",u:"%",lb:63,note:"Secured overnight financing rate"}]},
 {g:"Balance sheet & liquidity",items:[
  {id:"WALCL",n:"Fed total assets",t:"div",d:1e6,u:"$T",lb:13,note:"Weekly, H.4.1"},
  {id:"WRESBAL",n:"Bank reserves",t:"div",d:1e3,u:"$T",lb:13,note:"Reserve balances, weekly"},
  {id:"RRPONTSYD",n:"Overnight reverse repo",t:"lvl",u:"$B",lb:63,note:"ON RRP usage, daily"},
  {id:"WTREGEN",n:"Treasury General Account",t:"div",d:1e3,u:"$B",lb:13,note:"Treasury cash at the Fed, weekly"}]}],
credit:[
 {g:"Corporate spreads",items:[
  {id:"BAMLC0A0CM",n:"Investment grade",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA US Corporate OAS"},
  {id:"BAMLC0A4CBBB",n:"BBB",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA BBB OAS"},
  {id:"BAMLH0A0HYM2",n:"High yield",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA US HY OAS"},
  {id:"BAMLH0A1HYBB",n:"BB",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA BB OAS"},
  {id:"BAMLH0A3HYC",n:"CCC & lower",t:"lvl",u:"%",good:"down",lb:63,note:"ICE BofA CCC & lower OAS"}]},
 {g:"Lending & conditions",items:[
  {id:"DRTSCILM",n:"Banks tightening C&I standards",t:"lvl",u:"%",good:"down",lb:1,note:"Fed SLOOS, net % tightening, quarterly"},
  {id:"NFCI",n:"Financial conditions",t:"lvl",u:"",good:"down",lb:13,note:"Chicago Fed NFCI; below 0 = looser"},
  {id:"MORTGAGE30US",n:"30-year mortgage",t:"lvl",u:"%",good:"down",lb:13,note:"Freddie Mac PMMS, weekly"}]}],
housing:[
 {g:"Rates & prices",items:[
  {id:"MORTGAGE30US",n:"30-year mortgage rate",t:"lvl",u:"%",good:"down",lb:13,note:"Freddie Mac PMMS, weekly"},
  {id:"CSUSHPINSA",n:"Home prices (Case-Shiller)",t:"yoy",u:"%",lb:3,note:"S&P CoreLogic national, y/y"}]},
 {g:"Activity & supply",items:[
  {id:"HOUST",n:"Housing starts",t:"lvl",u:"k",good:"up",lb:3,note:"Thousands, annualized"},
  {id:"PERMIT",n:"Building permits",t:"lvl",u:"k",good:"up",lb:3,note:"Thousands, annualized"},
  {id:"EXHOSLUSM495S",n:"Existing home sales",t:"div",d:1e6,u:"M",good:"up",lb:3,note:"Millions, annualized (NAR)"},
  {id:"MSACSR",n:"New-home months' supply",t:"lvl",u:"mo",lb:3,note:"Census, months"}]}],
global:[
 {g:"Policy & yields",items:[
  {id:"ECBDFR",n:"ECB deposit rate",t:"lvl",u:"%",lb:63,note:"European Central Bank"},
  {id:"IRLTLT01DEM156N",n:"Germany 10-year",t:"lvl",u:"%",lb:3,note:"OECD, monthly"},
  {id:"IRLTLT01GBM156N",n:"UK 10-year",t:"lvl",u:"%",lb:3,note:"OECD, monthly"},
  {id:"IRLTLT01JPM156N",n:"Japan 10-year",t:"lvl",u:"%",lb:3,note:"OECD, monthly"}]},
 {g:"Currencies",items:[
  {id:"DEXUSEU",n:"EUR/USD",t:"lvl",u:"",lb:63,note:"Dollars per euro"},
  {id:"DEXUSUK",n:"GBP/USD",t:"lvl",u:"",lb:63,note:"Dollars per pound"},
  {id:"DEXJPUS",n:"USD/JPY",t:"lvl",u:"",lb:63,note:"Yen per dollar"},
  {id:"DEXCHUS",n:"USD/CNY",t:"lvl",u:"",lb:63,note:"Yuan per dollar"}]}],
energy:[
 {g:"Energy",items:[
  {id:"DCOILWTICO",n:"WTI crude",t:"lvl",u:"$",lb:63,note:"Spot, $/barrel (EIA)"},
  {id:"DCOILBRENTEU",n:"Brent crude",t:"lvl",u:"$",lb:63,note:"Spot, $/barrel (EIA)"},
  {id:"DHHNGSP",n:"Henry Hub natural gas",t:"lvl",u:"$",lb:63,note:"Spot, $/MMBtu (EIA)"},
  {id:"GASREGW",n:"U.S. regular gasoline",t:"lvl",u:"$",good:"down",lb:13,note:"Retail, $/gallon (EIA), weekly"}]},
 {g:"Metals & agriculture",items:[
  {id:"PCOPPUSDM",n:"Copper",t:"lvl",u:"$",lb:3,note:"IMF, $/metric ton, monthly"},
  {id:"PALUMUSDM",n:"Aluminum",t:"lvl",u:"$",lb:3,note:"IMF, $/metric ton, monthly"},
  {id:"PWHEAMTUSDM",n:"Wheat",t:"lvl",u:"$",lb:3,note:"IMF, $/metric ton, monthly"},
  {id:"PMAIZMTUSDM",n:"Corn",t:"lvl",u:"$",lb:3,note:"IMF, $/metric ton, monthly"}]}],
crypto:[
 {g:"Crypto (Coinbase via FRED)",items:[
  {id:"CBBTCUSD",n:"Bitcoin",t:"lvl",u:"$",lb:63,note:"Coinbase, USD, daily"},
  {id:"CBETHUSD",n:"Ether",t:"lvl",u:"$",lb:63,note:"Coinbase, USD, daily"}]}]
};
const DASH=SETS.core;
function fmtVal(v,u){if(u==="$T")return "$"+v.toFixed(2)+"T";if(u==="$B")return "$"+Math.round(v).toLocaleString("en-US")+"B";if(u==="M")return v.toFixed(2)+"M";if(u==="mo")return v.toFixed(1)+" mo";if(u==="$"&&v>=1000)return "$"+Math.round(v).toLocaleString("en-US");if(u==="$")return "$"+v.toFixed(2);if(u==="k")return Math.round(v).toLocaleString("en-US")+"k";if(u==="pp")return (v>0?"+":"")+v.toFixed(2);return v.toFixed(2)+(u==="%"?"%":"")}
function renderDash(root){
  const compact=root.dataset.dash==="compact";
  const base=SETS[root.dataset.dashSet||"core"]||DASH;
  const groups=(compact?base.map(g=>({g:g.g,items:g.items.slice(0,2)})):base).map(g=>({g:g.g,items:g.items.map(i=>i.t==="div"?Object.assign({},i,{t:"div:"+i.d}):i)}));
  root.innerHTML=groups.map(g=>`<div class="dg"><div class="dg-h">${esc(g.g)}</div><div class="dg-grid">${g.items.map(i=>`<a class="ind" data-ind="${i.id}" href="https://fred.stlouisfed.org/series/${i.id}" target="_blank" rel="noopener"><div class="ind-top"><span class="ind-n">${esc(i.n)}</span><span class="sig">…</span></div><div class="ind-v num">—</div><div class="ind-d num">Loading</div><div class="ind-s"></div><div class="ind-note">${esc(i.note)} · FRED: ${i.id}</div></a>`).join("")}</div></div>`).join("");
  let improving=0,worsening=0,done=0,total=0;
  groups.forEach(g=>g.items.forEach(i=>{total++;
    fred(i.id,"2020-01-01").then(o=>{
      const s=transform(o,i.t); if(!s.length) throw 0;
      const last=s[s.length-1], prev=s[s.length-2], back=s[Math.max(0,s.length-1-i.lb)];
      const el=root.querySelector('[data-ind="'+i.id+'"]'); if(!el) return;
      el.querySelector(".ind-v").textContent=fmtVal(last.v,i.u);
      const ch=last.v-(prev?prev.v:last.v); const chs=i.u==="k"?Math.round(ch).toLocaleString("en-US")+"k":i.u==="$B"?(ch>0?"+":"")+Math.round(ch).toLocaleString("en-US")+"B":(ch>0?"+":"")+(Math.abs(ch)>=100?Math.round(ch).toLocaleString("en-US"):ch.toFixed(2))+(i.u==="%"||i.u==="pp"?" pp":i.u==="$T"?"T":"");
      el.querySelector(".ind-d").textContent=(ch>0&&i.u==="k"?"+":"")+chs+" vs prior · "+shortDay(last.d);
      const trend=last.v-back.v, dir=Math.abs(trend)<1e-9?"flat":trend>0?"up":"down";
      let cls="neu",lab=dir==="up"?"Rising":dir==="down"?"Falling":"Flat";
      if(i.good&&dir!=="flat"){const ok=dir===i.good;cls=ok?"good":"bad";ok?improving++:worsening++}
      const sig=el.querySelector(".sig"); sig.textContent=(dir==="up"?"▲ ":dir==="down"?"▼ ":"■ ")+lab; sig.className="sig "+cls;
      const pts=s.slice(-Math.min(s.length,i.t==="lvl"&&i.lb>=60?750:i.lb>=13?156:36));
      el.querySelector(".ind-s").innerHTML=spark(pts,cls==="good"?C.up:cls==="bad"?C.down:C.signal);
    }).catch(()=>{const el=root.querySelector('[data-ind="'+i.id+'"]');if(el){el.querySelector(".ind-d").textContent="Data temporarily unavailable";el.querySelector(".sig").textContent=""}})
    .finally(()=>{done++;if(done===total){if(root.dataset.dashSet)return;$$("[data-pulse]").forEach(p=>{const n=improving+worsening;p.innerHTML=n?`<b>${improving}</b> of ${n} directional indicators are moving in a supportive direction over the past quarter; <b>${worsening}</b> are moving against.`:""})}});
  }));
}
$$("[data-dash]").forEach(renderDash);

/* ---------- Treasury auctions ---------- */
const num=v=>v==null||v==="null"||v===""?null:+v;
const bn=v=>v==null?"–":"$"+(v/1e9).toFixed(v>=1e10?0:1)+"B";
function auctionRate(a){const t=a.security_type;if(t==="Bill")return num(a.high_investment_rate)??num(a.high_discnt_rate);return num(a.high_yield)??num(a.high_discnt_margin)}
function sec(a){return a.security_term+" "+(a.security_type==="Bill"?"bill":a.security_type==="Note"?"note":a.security_type==="Bond"?"bond":a.security_type)+(a.inflation_index_security==="Yes"?" (TIPS)":a.floating_rate==="Yes"?" (FRN)":"")+(a.reopening==="Yes"?" · reopening":"")}
let AUC=null;
function loadAuctions(){
  if(AUC) return AUC;
  return AUC=fetch("/api/auctions",{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.json()}).then(j=>j.data||[]);
}
function renderAuctions(){
  const upEl=$("#auc-upcoming"), resEl=$("#auc-results"), keyEl=$("#auc-key"), miniEl=$("#auc-mini");
  if(!upEl&&!resEl&&!miniEl) return;
  loadAuctions().then(rows=>{
    const today=new Date().toISOString().slice(0,10);
    const done=rows.filter(a=>num(a.bid_to_cover_ratio)!=null).sort((a,b)=>a.auction_date<b.auction_date?1:-1);
    const up=rows.filter(a=>num(a.bid_to_cover_ratio)==null&&a.auction_date>=today).sort((a,b)=>a.auction_date>b.auction_date?1:-1);
    const prevSame=a=>done.find(b=>b!==a&&b.security_term===a.security_term&&b.security_type===a.security_type&&b.auction_date<a.auction_date&&b.inflation_index_security===a.inflation_index_security&&b.floating_rate===a.floating_rate);
    const share=(a,k)=>{const c=num(a.comp_accepted),x=num(a[k]);return c&&x!=null?(x/c*100):null};
    const row=a=>{const r=auctionRate(a),btc=num(a.bid_to_cover_ratio),p=prevSame(a),pb=p?num(p.bid_to_cover_ratio):null,d=btc!=null&&pb!=null?btc-pb:null,ind=share(a,"indirect_bidder_accepted"),pd=share(a,"primary_dealer_accepted");
      return `<tr><td>${shortDay(a.auction_date)}</td><td class="l">${esc(sec(a))}</td><td>${r!=null?r.toFixed(3)+"%":"–"}</td><td>${btc!=null?btc.toFixed(2)+"x":"–"}</td><td class="${d==null?"":d>0?"up":d<0?"down":""}">${d==null?"–":(d>0?"+":"")+d.toFixed(2)}</td><td>${ind!=null?ind.toFixed(1)+"%":"–"}</td><td>${pd!=null?pd.toFixed(1)+"%":"–"}</td><td>${bn(num(a.offering_amt))}</td></tr>`};
    const head=`<tr><th>Date</th><th class="l">Security</th><th>High rate</th><th>Bid-to-cover</th><th>vs prior</th><th>Indirect</th><th>Dealers</th><th>Size</th></tr>`;
    if(resEl) resEl.innerHTML=head+done.slice(0,+resEl.dataset.limit||40).map(row).join("");
    if(miniEl) miniEl.innerHTML=`<tr><th>Date</th><th class="l">Security</th><th>High rate</th><th>Bid-to-cover</th></tr>`+done.filter(a=>a.security_type!=="Bill").slice(0,3).concat(done.filter(a=>a.security_type==="Bill").slice(0,3)).sort((a,b)=>a.auction_date<b.auction_date?1:-1).map(a=>{const r=auctionRate(a),b=num(a.bid_to_cover_ratio);return `<tr><td>${shortDay(a.auction_date)}</td><td class="l">${esc(sec(a))}</td><td>${r!=null?r.toFixed(3)+"%":"–"}</td><td>${b!=null?b.toFixed(2)+"x":"–"}</td></tr>`}).join("");
    if(upEl) upEl.innerHTML=up.length?up.slice(0,12).map(a=>`<div class="up-row"><span class="num">${shortDay(a.auction_date)}</span><b>${esc(sec(a))}</b><span class="num">${bn(num(a.offering_amt))}</span></div>`).join(""):'<div class="empty">No upcoming auctions announced yet.</div>';
    if(keyEl){const cpn=done.filter(a=>a.security_type!=="Bill").slice(0,3);keyEl.innerHTML=cpn.map(a=>{const r=auctionRate(a),btc=num(a.bid_to_cover_ratio),p=prevSame(a),pb=p?num(p.bid_to_cover_ratio):null,ind=share(a,"indirect_bidder_accepted");return `<div class="card auc-k"><div class="card-h"><span>${esc(sec(a))}</span><span>${shortDay(a.auction_date)}</span></div><div class="auc-big num">${r!=null?r.toFixed(3)+"%":"–"}</div><div class="auc-sub num">Bid-to-cover <b>${btc!=null?btc.toFixed(2)+"x":"–"}</b>${pb!=null?` <span class="${btc-pb>=0?"up":"down"}">(${btc-pb>=0?"+":""}${(btc-pb).toFixed(2)} vs prior)</span>`:""}</div><div class="auc-sub num">Indirect bidders <b>${ind!=null?ind.toFixed(1)+"%":"–"}</b> · Size <b>${bn(num(a.offering_amt))}</b></div></div>`}).join("")}
    $$("[data-auc-asof]").forEach(e=>{if(done[0])e.textContent="Latest result: "+fmtDay(done[0].auction_date)});
  }).catch(()=>{[upEl,resEl,miniEl,keyEl].forEach(e=>{if(e)e.innerHTML='<tr><td><div class="empty">Treasury auction data is temporarily unavailable. Refresh in a minute.</div></td></tr>'})});
}
renderAuctions();

/* ---------- Charts ---------- */
function niceTicks(lo,hi,n){const span=hi-lo||1,step0=span/n,mag=Math.pow(10,Math.floor(Math.log10(step0))),err=step0/mag,step=(err>=7.5?10:err>=3.5?5:err>=1.5?2:1)*mag;const t=[];for(let v=Math.ceil(lo/step)*step;v<=hi+1e-9;v+=step)t.push(+v.toFixed(10));return {t,step}}
function chartSVG(spec,data,opt){
  opt=opt||{}; const W=opt.w||960,H=opt.h||460,L=58,R=opt.small?16:110,T=opt.brand?92:20,B=opt.brand?70:36;
  const all=data.flatMap(s=>s.pts); if(!all.length) return "";
  const xs=all.map(p=>+new Date(p.d)), x0=Math.min(...xs), x1=Math.max(...xs);
  let lo=Math.min(...all.map(p=>p.v)), hi=Math.max(...all.map(p=>p.v)); const pad=(hi-lo)*.08||1; lo-=pad; hi+=pad;
  if(spec.zero&&lo>0) lo=0;
  const {t:ticks}=niceTicks(lo,hi,opt.small?3:5);
  const X=d=>L+(+new Date(d)-x0)/(x1-x0||1)*(W-L-R), Y=v=>T+(hi-v)/(hi-lo)*(H-T-B);
  let g="";
  ticks.forEach(v=>{if(v<lo||v>hi)return;g+=`<line x1="${L}" x2="${W-R}" y1="${Y(v)}" y2="${Y(v)}" stroke="${C.rule}"/><text x="${L-10}" y="${Y(v)+4}" text-anchor="end" font-family="IBM Plex Mono,monospace" font-size="${opt.small?10:12}" fill="${C.mute}">${+v.toFixed(2)}${spec.units==="%"?"%":""}</text>`});
  if(lo<0&&hi>0) g+=`<line x1="${L}" x2="${W-R}" y1="${Y(0)}" y2="${Y(0)}" stroke="${C.steel}" stroke-dasharray="3 3"/>`;
  const y0=new Date(x0).getFullYear(), y1=new Date(x1).getFullYear(), every=Math.max(1,Math.ceil((y1-y0+1)/(opt.small?3:8)));
  for(let y=y0+1;y<=y1;y+=every){const xx=X(y+"-01-01");g+=`<text x="${xx}" y="${H-B+20}" text-anchor="middle" font-family="IBM Plex Mono,monospace" font-size="${opt.small?10:12}" fill="${C.mute}">${y}</text>`}
  const ends=[];
  data.forEach((s,i)=>{const col=SERIES_COLORS[i%5];const step=Math.max(1,Math.floor(s.pts.length/900));const pts=s.pts.filter((p,j)=>j%step===0||j===s.pts.length-1);
    g+=`<polyline points="${pts.map(p=>X(p.d).toFixed(1)+","+Y(p.v).toFixed(1)).join(" ")}" fill="none" stroke="${col}" stroke-width="${opt.small?1.6:2.2}" stroke-linejoin="round"/>`;
    const lp=s.pts[s.pts.length-1]; ends.push({y:Y(lp.v),col,txt:(+lp.v.toFixed(2))+(spec.units==="%"?"%":""),lab:s.label});
    g+=`<circle cx="${X(lp.d)}" cy="${Y(lp.v)}" r="3.5" fill="${col}" stroke="${C.ink}" stroke-width="1.5"/>`});
  if(!opt.small){ends.sort((a,b)=>a.y-b.y);for(let i=1;i<ends.length;i++)if(ends[i].y-ends[i-1].y<30)ends[i].y=ends[i-1].y+30;ends.forEach(e=>{g+=`<text x="${W-R+10}" y="${e.y-2}" font-family="IBM Plex Mono,monospace" font-size="13" fill="${e.col}" font-weight="600">${e.txt}</text><text x="${W-R+10}" y="${e.y+13}" font-family="IBM Plex Sans,sans-serif" font-size="11" fill="${C.steel}">${esc(e.lab)}</text>`})}
  let head="";
  if(opt.brand){head=`<rect width="${W}" height="${H}" fill="${C.ink}"/><rect x="0" y="0" width="6" height="${H}" fill="${C.signal}"/><text x="${L}" y="40" font-family="Archivo,Arial Narrow,sans-serif" font-weight="800" font-size="26" fill="${C.paper}">${esc(spec.title)}</text><text x="${L}" y="66" font-family="IBM Plex Sans,sans-serif" font-size="14" fill="${C.steel}">${esc(spec.subtitle||"")}</text><text x="${L}" y="${H-18}" font-family="IBM Plex Mono,monospace" font-size="11" fill="${C.mute}">Source: ${esc(spec.source||"FRED")} · alphagenresearch.com</text><text x="${W-24}" y="${H-18}" text-anchor="end" font-family="Archivo,Arial,sans-serif" font-weight="800" font-size="16" fill="${C.paper}">Alpha<tspan fill="${C.signal}">Gen</tspan></text>`}
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${esc(spec.title)}">${head}${g}</svg>`;
}
function chartData(spec){return Promise.all(spec.series.map(s=>fred(s.id,spec.start||"2015-01-01").then(o=>({label:s.label,pts:transform(o,s.t||"lvl").filter(p=>p.d>=(spec.start||"2015-01-01"))}))))}
function legend(spec){return '<div class="clegend">'+spec.series.map((s,i)=>`<span><i style="background:${SERIES_COLORS[i%5]}"></i>${esc(s.label)}</span>`).join("")+"</div>"}
function downloadPNG(spec,data){
  const svg=chartSVG(spec,data,{brand:true,w:1200,h:675});const img=new Image();const url=URL.createObjectURL(new Blob([svg],{type:"image/svg+xml"}));
  img.onload=()=>{const c=document.createElement("canvas");c.width=2400;c.height=1350;const x=c.getContext("2d");x.scale(2,2);x.drawImage(img,0,0);URL.revokeObjectURL(url);c.toBlob(b=>{const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="alphagen-"+spec.id+".png";document.body.appendChild(a);a.click();a.remove()},"image/png")};
  img.src=url;
}
function renderChartInto(el,spec,small){
  el.innerHTML='<div class="chart-load">Loading chart…</div>';
  chartData(spec).then(data=>{
    if(!data.some(d=>d.pts.length)) throw 0;
    el.innerHTML=chartSVG(spec,data,small?{small:true,w:520,h:240}:{});
    if(!small){const b=el.parentNode.querySelector("[data-dl]");if(b){b.hidden=false;b.onclick=()=>downloadPNG(spec,data)}}
  }).catch(()=>{el.innerHTML='<div class="chart-load">Chart data is temporarily unavailable.</div>'});
}
AG.chart={render:renderChartInto,svg:chartSVG,data:chartData};
let CHARTS=null;
function drawCharts(){
  const items=live(CHARTS&&CHARTS.items); if(!items.length) return;
  const pick=id=>items.find(c=>c.id===id)||items[0];
  $$("[data-cotd]").forEach(el=>{
    const spec=el.dataset.cotd?pick(el.dataset.cotd):items[0];
    el.innerHTML=`<div class="cotd-head"><div><div class="eyebrow">Chart of the Day · ${esc(fmtDay(spec.time))}</div><h2 class="sec">${esc(spec.title)}</h2><p class="cotd-sub">${esc(spec.subtitle||"")}</p></div><div class="cotd-act"><button class="btn ghost sm" type="button" data-dl hidden>Download PNG</button><a class="btn ghost sm" href="/charts/${encodeURIComponent(spec.id)}">Share page</a></div></div><div class="cotd-chart"></div>${legend(spec)}<div class="cotd-take"><span class="eyebrow">The AlphaGen take</span><p>${esc(spec.take)}</p><div class="cotd-src">Source: <a href="${esc(spec.source_url||"https://fred.stlouisfed.org")}" target="_blank" rel="noopener">${esc(spec.source||"FRED")}</a></div></div>`;
    renderChartInto(el.querySelector(".cotd-chart"),spec,false);
  });
  $$("[data-chart-archive]").forEach(el=>{
    const rest=items.slice(1,+el.dataset.limit||24); el.innerHTML="";
    if(!rest.length){el.innerHTML='<div class="empty">The archive builds as new charts publish each trading day.</div>';return}
    rest.forEach(spec=>{const a=document.createElement("a");a.className="card chart-card";a.href="/charts/"+encodeURIComponent(spec.id);a.innerHTML=`<div class="card-h"><span>${esc(shortDay(spec.time))}</span><span>Chart</span></div><h3>${esc(spec.title)}</h3><div class="mini-c"></div>`;el.appendChild(a);
      const io=new IntersectionObserver(e=>{if(e[0].isIntersecting){io.disconnect();renderChartInto(a.querySelector(".mini-c"),spec,true)}});io.observe(a)});
  });
}
if($("[data-cotd]")||$("[data-chart-archive]")) getJSON("/charts.json").then(d=>{CHARTS=d;drawCharts()}).catch(()=>{});

/* ---------- Earnings scorecard ---------- */
function renderEarnings(){
  const els=$$("[data-earnings]"); if(!els.length) return;
  getJSON("/earnings.json").then(d=>{
    const items=live(d.items);
    els.forEach(el=>{
      const tk=el.dataset.ticker; let list=tk?items.filter(i=>i.ticker===tk):items; list=list.slice(0,+el.dataset.limit||100);
      if(!list.length){el.innerHTML='<div class="empty"><b>No reports logged yet.</b>Results are added as companies file them.</div>';return}
      el.innerHTML='<div class="tbl-wrap"><table class="etbl"><tr><th class="l">Company</th><th>Period</th><th>Reported</th><th>Revenue</th><th>Y/Y</th><th>Diluted EPS</th><th>Y/Y</th><th class="l">AlphaGen take</th></tr>'+list.map(e=>{const yy=v=>v==null?"–":`<span class="${v>0?"up":v<0?"down":""}">${v>0?"+":""}${(+v).toFixed(1)}%</span>`;return `<tr><td class="l"><a href="/stock/${esc(e.ticker.split(":").pop())}"><b>${esc(e.name)}</b> <span class="tag tk">${esc(e.ticker.split(":").pop())}</span></a></td><td>${esc(e.period||"")}</td><td>${esc(shortDay(e.report_date||e.time))}</td><td>${e.revenue!=null?"$"+(+e.revenue).toFixed(2)+"B":"–"}</td><td>${yy(e.revenue_yoy)}</td><td>${e.eps!=null?"$"+(+e.eps).toFixed(2):"–"}</td><td>${yy(e.eps_yoy)}</td><td class="l take">${esc(e.take||"")} ${e.source_url?`<a class="src" href="${esc(e.source_url)}" target="_blank" rel="noopener">Filing →</a>`:""}</td></tr>`}).join("")+"</table></div>";
    });
    $$("[data-earn-count]").forEach(e=>e.textContent=items.length);
  }).catch(()=>{});
}
renderEarnings();
})();

/* ===== Deals, SEC filings tape, search ===== */
(function(){
"use strict";
const AG=window.AG||{}; const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const getJSON=p=>fetch(p+(p.includes("?")?"&":"?")+"t="+Date.now(),{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.json()});
const live=items=>(items||[]).filter(i=>!i.time||new Date(i.time)<=Date.now()).sort((a,b)=>new Date(b.time)-new Date(a.time));
const ago=iso=>{const d=new Date(iso),m=Math.round((Date.now()-d)/60000);if(isNaN(m))return"";if(m<1)return"Just now";if(m<60)return m+"m ago";if(m<1440)return Math.round(m/60)+"h ago";return d.toLocaleDateString("en-US",{month:"short",day:"numeric"})};
const day=s=>{if(!s)return"";const d=new Date(s.length===10?s+"T12:00:00":s);return d.toLocaleDateString("en-US",{month:"short",day:"numeric"})};
const money=v=>v==null?"Undisclosed":v>=1?"$"+(+v).toFixed(v>=10?1:2)+"B":"$"+Math.round(v*1000)+"M";

/* ---------- Deals ---------- */
const TYPES=["M&A","VC","PE","IPO","Debt"];
function renderDeals(){
  const els=$$("[data-deals]"); if(!els.length) return;
  getJSON("/deals.json").then(d=>{
    const items=live(d.items);
    els.forEach(el=>{
      const v={type:el.dataset.type||"all",limit:+el.dataset.limit||60,tk:el.dataset.ticker||""};
      const draw=()=>{
        let list=items; if(v.type!=="all") list=list.filter(x=>x.type===v.type); if(v.tk) list=list.filter(x=>(x.tickers||[]).some(t=>t.split(":").pop()===v.tk));
        list=list.slice(0,v.limit);
        if(!list.length){el.innerHTML='<div class="empty"><b>No deals logged yet.</b>Deals post as companies announce them and file with the SEC.</div>';return}
        if(el.dataset.view==="cards"){el.innerHTML='<div class="deal-cards">'+list.map(x=>`<a class="deal-card" href="/deals"><div class="dk"><span class="tag dt-${esc(x.type.replace("&",""))}">${esc(x.type)}</span><span>${esc(day(x.announced||x.time))}</span></div><h3>${esc(x.headline)}</h3><div class="dv num">${esc(x.value_text||money(x.value))}</div><p>${esc(x.take||"")}</p></a>`).join("")+"</div>";return}
        el.innerHTML='<div class="tbl-wrap"><table class="etbl dtbl"><tr><th class="l">Deal</th><th>Type</th><th>Value</th><th class="l">Parties</th><th>Status</th><th>Announced</th><th class="l">AlphaGen take</th></tr>'+list.map(x=>`<tr><td class="l"><b>${esc(x.headline)}</b>${(x.tickers||[]).map(t=>` <a class="tag tk" href="/stock/${esc(t.split(":").pop())}">${esc(t.split(":").pop())}</a>`).join("")}</td><td><span class="tag dt-${esc(x.type.replace("&",""))}">${esc(x.type)}</span></td><td class="num">${esc(x.value_text||money(x.value))}</td><td class="l parties">${esc(x.parties||"")}</td><td>${esc(x.status||"")}</td><td>${esc(day(x.announced||x.time))}</td><td class="l take">${esc(x.take||"")} ${x.source_url?`<a class="src" href="${esc(x.source_url)}" target="_blank" rel="noopener">Source →</a>`:""}</td></tr>`).join("")+"</table></div>";
      };
      const bar=document.querySelector(`[data-deal-filters="${el.id}"]`);
      if(bar) bar.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{v.type=b.dataset.f;bar.querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",x===b?"true":"false"));draw()}));
      draw();
    });
    const wk=items.filter(x=>Date.now()-new Date(x.time)<7*864e5);
    $$("[data-deal-stats]").forEach(s=>{
      const by=t=>wk.filter(x=>x.type===t);
      const disclosed=wk.filter(x=>x.value!=null).reduce((a,x)=>a+(+x.value),0);
      s.innerHTML=`<div class="lvl"><div class="k">Deals logged, 7 days</div><div class="v num">${wk.length}</div><div class="d">all types</div></div>`+["M&A","VC","PE","IPO"].map(t=>`<div class="lvl"><div class="k">${t}</div><div class="v num">${by(t).length}</div><div class="d num">${by(t).some(x=>x.value!=null)?money(by(t).filter(x=>x.value!=null).reduce((a,x)=>a+(+x.value),0))+" disclosed":"&nbsp;"}</div></div>`).join("")+`<div class="lvl"><div class="k">Disclosed value</div><div class="v num">${disclosed?money(disclosed):"–"}</div><div class="d">7 days, logged deals</div></div>`;
    });
  }).catch(()=>{els.forEach(el=>el.innerHTML='<div class="empty"><b>Deal flow is loading.</b>Refresh in a moment.</div>')});
}
renderDeals();

/* ---------- SEC EDGAR live filings tape ---------- */
const FEEDS={formd:{label:"Private raise",form:"Form D"},s1:{label:"IPO filing",form:"S-1"},f1:{label:"Foreign IPO filing",form:"F-1"},merger:{label:"Merger proxy",form:"DEFM14A"},tender:{label:"Tender offer",form:"SC TO-T"},activist:{label:"Activist stake",form:"SC 13D"}};
function parseAtom(xml,key){
  const doc=new DOMParser().parseFromString(xml,"application/xml");
  return [...doc.getElementsByTagName("entry")].map(e=>{
    const g=n=>{const x=e.getElementsByTagName(n)[0];return x?x.textContent.trim():""};
    const title=g("title"); const m=title.match(/^(.+?) - (.+?) \((\d{10})\)/);
    const link=(e.getElementsByTagName("link")[0]||{getAttribute:()=>""}).getAttribute("href");
    return m?{key,form:m[1],company:m[2].replace(/\s+/g," "),cik:m[3],updated:g("updated"),link}:null;
  }).filter(Boolean);
}
function renderFilings(){
  const els=$$("[data-filings]"); if(!els.length) return;
  els.forEach(el=>{
    const keys=(el.dataset.filings||"formd,s1,merger,tender,activist").split(",");
    el.innerHTML='<div class="empty">Loading live SEC filings…</div>';
    Promise.all(keys.map(k=>fetch("/api/sec/"+k,{cache:"no-store"}).then(r=>{if(!r.ok)throw 0;return r.text()}).then(t=>parseAtom(t,k)).catch(()=>[]))).then(lists=>{
      const seen=new Set(); const all=lists.flat().filter(f=>{const k=f.form+f.cik;if(seen.has(k))return false;seen.add(k);return true}).sort((a,b)=>new Date(b.updated)-new Date(a.updated)).slice(0,+el.dataset.limit||30);
      if(!all.length){el.innerHTML='<div class="empty"><b>The SEC filings feed is temporarily unavailable.</b>It refreshes automatically.</div>';return}
      el.innerHTML=all.map(f=>`<a class="filing" href="${esc(f.link)}" target="_blank" rel="noopener"><span class="ff">${esc(f.form)}</span><span class="fc">${esc(f.company)}</span><span class="fl">${esc(FEEDS[f.key].label)}</span><span class="ft num">${esc(new Date(f.updated).toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",timeZone:"America/New_York"}))}</span></a>`).join("");
    });
  });
}
renderFilings(); setInterval(renderFilings,5*60000);

/* ---------- Site search ---------- */
(function(){
  const box=$("#search-results"), q=$("#search-q"); if(!box||!q) return;
  let DATA=[];
  Promise.all(["/wire.json","/notes.json","/deals.json","/earnings.json","/charts.json"].map(p=>getJSON(p).catch(()=>({items:[]})))).then(([w,n,d,e,c])=>{
    DATA=[].concat(
      live(w.items).map(i=>({k:"Wire",t:i.headline,s:i.take,u:"/wire",time:i.time,x:(i.ticker||"")+" "+(i.tag||"")})),
      live(n.items).map(i=>({k:i.series?"Brief":"Note",t:i.title,s:i.dek,u:"/notes/"+i.id,time:i.time,x:(i.tickers||[]).join(" ")+" "+(i.tag||"")})),
      live(d.items).map(i=>({k:"Deal",t:i.headline,s:i.take,u:"/deals",time:i.time,x:(i.tickers||[]).join(" ")+" "+i.type+" "+(i.parties||"")})),
      live(e.items).map(i=>({k:"Earnings",t:i.name+" "+(i.period||""),s:i.take,u:"/stock/"+i.ticker.split(":").pop(),time:i.time,x:i.ticker})),
      live(c.items).map(i=>({k:"Chart",t:i.title,s:i.take,u:"/charts/"+i.id,time:i.time,x:i.series.map(s=>s.id).join(" ")}))
    ); run();
  });
  const run=()=>{
    const v=q.value.trim().toLowerCase(); const terms=v.split(/\s+/).filter(Boolean);
    const res=terms.length?DATA.filter(r=>terms.every(t=>(r.t+" "+r.s+" "+r.x).toLowerCase().includes(t))):DATA;
    $("#search-count").textContent=terms.length?res.length+" results":"Latest across AlphaGen";
    box.innerHTML=res.slice(0,80).map(r=>`<a class="sres" href="${esc(r.u)}"><span class="tag">${esc(r.k)}</span><b>${esc(r.t)}</b><p>${esc((r.s||"").slice(0,220))}</p><span class="st">${esc(ago(r.time))}</span></a>`).join("")||'<div class="empty"><b>No matches.</b>Try a ticker, a company, or a topic like "auction" or "CPI".</div>';
  };
  const p=new URLSearchParams(location.search).get("q"); if(p) q.value=p;
  q.addEventListener("input",run);
})();
})();
