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
const DASH=[
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
];
function fmtVal(v,u){if(u==="$")return "$"+v.toFixed(2);if(u==="k")return Math.round(v).toLocaleString("en-US")+"k";if(u==="pp")return (v>0?"+":"")+v.toFixed(2);return v.toFixed(2)+(u==="%"?"%":"")}
function renderDash(root){
  const compact=root.dataset.dash==="compact";
  const groups=compact?DASH.map(g=>({g:g.g,items:g.items.slice(0,2)})):DASH;
  root.innerHTML=groups.map(g=>`<div class="dg"><div class="dg-h">${esc(g.g)}</div><div class="dg-grid">${g.items.map(i=>`<a class="ind" id="ind-${i.id}" href="https://fred.stlouisfed.org/series/${i.id}" target="_blank" rel="noopener"><div class="ind-top"><span class="ind-n">${esc(i.n)}</span><span class="sig">…</span></div><div class="ind-v num">—</div><div class="ind-d num">Loading</div><div class="ind-s"></div><div class="ind-note">${esc(i.note)} · FRED: ${i.id}</div></a>`).join("")}</div></div>`).join("");
  let improving=0,worsening=0,done=0,total=0;
  groups.forEach(g=>g.items.forEach(i=>{total++;
    fred(i.id,"2020-01-01").then(o=>{
      const s=transform(o,i.t); if(!s.length) throw 0;
      const last=s[s.length-1], prev=s[s.length-2], back=s[Math.max(0,s.length-1-i.lb)];
      const el=document.getElementById("ind-"+i.id); if(!el) return;
      el.querySelector(".ind-v").textContent=fmtVal(last.v,i.u);
      const ch=last.v-(prev?prev.v:last.v); const chs=i.u==="k"?Math.round(ch).toLocaleString("en-US")+"k":(ch>0?"+":"")+ch.toFixed(2)+(i.u==="%"||i.u==="pp"?" pp":"");
      el.querySelector(".ind-d").textContent=(ch>0&&i.u==="k"?"+":"")+chs+" vs prior · "+shortDay(last.d);
      const trend=last.v-back.v, dir=Math.abs(trend)<1e-9?"flat":trend>0?"up":"down";
      let cls="neu",lab=dir==="up"?"Rising":dir==="down"?"Falling":"Flat";
      if(i.good&&dir!=="flat"){const ok=dir===i.good;cls=ok?"good":"bad";ok?improving++:worsening++}
      const sig=el.querySelector(".sig"); sig.textContent=(dir==="up"?"▲ ":dir==="down"?"▼ ":"■ ")+lab; sig.className="sig "+cls;
      const pts=s.slice(-Math.min(s.length,i.t==="lvl"&&i.lb>=60?750:i.lb>=13?156:36));
      el.querySelector(".ind-s").innerHTML=spark(pts,cls==="good"?C.up:cls==="bad"?C.down:C.signal);
    }).catch(()=>{const el=document.getElementById("ind-"+i.id);if(el){el.querySelector(".ind-d").textContent="Data temporarily unavailable";el.querySelector(".sig").textContent=""}})
    .finally(()=>{done++;if(done===total){$$("[data-pulse]").forEach(p=>{const n=improving+worsening;p.innerHTML=n?`<b>${improving}</b> of ${n} directional indicators are moving in a supportive direction over the past quarter; <b>${worsening}</b> are moving against.`:""})}});
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
