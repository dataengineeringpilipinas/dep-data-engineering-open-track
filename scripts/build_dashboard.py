#!/usr/bin/env python3
"""Build the deployable dashboard: dashboard/index.html (single self-contained file).

Run from the repository root (after scripts/analysis/m5_segmentation_kpis.py):
    python scripts/build_dashboard.py

Inputs : data/processed/dpwh_flood_control_analysis_ready.csv and data/processed/m5_*.csv
Output : dashboard/index.html   (published to GitHub Pages by .github/workflows/pages.yml)
The page embeds its data, so it needs no server, no internet and no extra files.
"""
import json
from pathlib import Path

import pandas as pd

PROC = Path("data/processed")
OUT = Path("dashboard/index.html")
COST = "contract_cost_php"


def build_data() -> dict:
    d = pd.read_csv(PROC / "dpwh_flood_control_analysis_ready.csv")
    prov = pd.read_csv(PROC / "m5_province_concentration.csv")
    coords = d.groupby("province").agg(lat=("provincialcapitallatitude", "mean"), lon=("provincialcapitallongitude", "mean"),
                                       cost=(COST, "sum")).reset_index()
    prov = prov.merge(coords, on="province")
    regions = list(d.region.value_counts().index)
    pidx = {p: i for i, p in enumerate(prov.province)}
    P = [[r.province, regions.index(r.region), int(r.projects), round(r.cost / 1e9, 2), round(r.top1_share, 3), round(r.top3_share, 3),
          int(r.contractors), int(round(r.outlier_rate * r.projects)), round(r.lat, 2), round(r.lon, 2)] for r in prov.itertuples()]
    o = d[d.is_high_cost_outlier == 1]
    O = [[str(r.project_id), pidx[r.province], round(getattr(r, COST) / 1e6, 1), round(r.cost_zscore_regional, 1)] for r in o.itertuples()]
    kq = pd.read_csv(PROC / "m5_kpi_quarterly.csv")
    Q = [[r.quarter, int(r.projects), r.kpi1_outlier_rate, r.kpi1b_outlier_rate_time_adjusted, r.kpi2_avg_cost_php_m,
          r.kpi3_top10_contractor_share, r.kpi5_over_budget_rate, bool(r.low_volume)] for r in kq.itertuples()]
    seg = pd.read_csv(PROC / "m5_segment_island_year.csv")
    S = [[r.mainisland, int(r.completion_year), int(r.projects), r.outlier_rate, r.outlier_rate_time_adjusted] for r in seg.itertuples()]
    t = pd.read_csv(PROC / "m5_segment_contractor_tier.csv")
    T = [[str(r.tier), int(r.contractors), r.share_of_projects, r.share_of_value] for r in t.itertuples()]
    k = pd.read_csv(PROC / "m5_kpi_summary.csv")
    K = [[r.kpi, r.name, r.value] for r in k.itertuples()]
    K[0][2] = len(o) / len(d)  # full precision (the CSV is rounded to 4 decimals)
    sl = pd.read_csv(PROC / "m5_review_shortlist.csv")
    SL = [[r.province, r.region, int(r.projects), r.top1_share, r.top3_share, r.outlier_rate_time_adjusted] for r in sl.itertuples()]
    meta = {"n": len(d), "cost": round(d[COST].sum() / 1e9, 1)}
    return {"R": regions, "P": P, "O": O, "Q": Q, "S": S, "T": T, "K": K, "SL": SL, "meta": meta}


TEMPLATE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>DPWH Flood Control Projects: Pattern Review Dashboard</title>
<meta name="description" content="Public-data dashboard of contractor concentration and cost outliers in DPWH flood control projects, 2022-2025.">
<style>
:root{--bg:#F4F6FA;--card:#fff;--ink:#14213D;--mut:#4A5A75;--line:#E3E8F0;--acc:#1F6FEB;--warn:#B45309;--ok:#0F766E;--flag:#C026D3}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0F1623;--card:#1A2434;--ink:#E8EDF6;--mut:#9AABC6;--line:#2B3850;--acc:#6FA3F5;--warn:#F5A94E;--ok:#34D3BD;--flag:#E879F9;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
.w{max-width:1240px;margin:0 auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.r{display:flex;gap:14px;flex-wrap:wrap}.k,.p{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;flex:1 1 200px;min-width:0}.p{flex:1 1 420px;padding:18px}
h1{margin:0;font-size:24px}h2{margin:8px 0 0;font-size:18px}h3{margin:0 0 4px;font-size:15px}.s{margin:0 0 10px;font-size:12.5px;color:var(--mut)}.v{font-size:26px;font-weight:700;margin:2px 0}
nav{display:flex;flex-wrap:wrap;gap:6px 16px}nav a{color:var(--acc);text-decoration:none;padding:6px 0}a{color:var(--acc)}
select,button{font:inherit;min-height:44px;padding:8px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink)}button.a{background:var(--acc);border-color:var(--acc);color:#fff}
table{width:100%;border-collapse:collapse}td,th{padding:7px 6px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}th{color:var(--mut);font-weight:600}td:first-child,th:first-child,td:nth-child(2),th:nth-child(2){text-align:left}
.sc{overflow-x:auto}tr[data-id],tr[data-g]{cursor:pointer}tr.f{background:color-mix(in srgb,var(--flag) 18%,transparent)}
.b{display:flex;align-items:center;gap:8px;margin:6px 0}.b i{display:block;height:14px;border-radius:3px;background:var(--acc)}
textarea{width:100%;min-height:56px;font:12px monospace;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:8px}
.lg{font-size:12px;color:var(--mut);display:flex;gap:12px;flex-wrap:wrap}.lg b{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px}
.ins{border-left:4px solid var(--acc);padding:4px 12px;margin:8px 0}
</style></head><body><div class="w">
<header><h1>DPWH Flood Control Projects: Pattern Review Dashboard</h1>
<p class="s" style="margin:6px 0 8px">Can public data reveal geographic, financial and contractor patterns that may justify a closer audit look? __N__ completed projects (about PHP __COST__B), July 2022 to May 2025. Indicators for review, not evidence of wrongdoing.</p>
<nav><a href="#overview">Overview</a><a href="#trends">Trends</a><a href="#segments">Segments</a><a href="#hotspots">Hotspots</a><a href="#shortlist">Shortlist</a><a href="#method">Method</a></nav></header>
<h2 id="overview">1. Overview: five KPIs</h2><div class="r" id="kp"></div>
<h2 id="trends">2. Trends by completion quarter</h2>
<div class="p"><p class="s">Does the share of unusual projects really rise over time? Red rings mark quarters with fewer than 100 projects, so read them with care.</p><div id="tr" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:14px"></div></div>
<h2 id="segments">3. Segments</h2>
<div class="r"><div class="p"><h3>Outlier rate by island group and completion year</h3><p class="s">Original flag / time-adjusted flag (project count under each). Time-adjusted compares within region and year.</p><div class="sc"><table id="sg"></table></div></div>
<div class="p"><h3>Contractor size tiers</h3><p class="s">Share of projects and of contract value, by projects won</p><div id="tt"></div></div></div>
<h2 id="hotspots">4. Hotspots and flagged projects (interactive)</h2>
<div class="r" style="align-items:center"><select id="rg" aria-label="Region"></select><select id="pv" aria-label="Province"></select><button id="rs">Reset filters</button></div>
<div class="r" id="kp2"></div>
<div class="r"><div class="p" style="flex:0 1 400px"><h3>Concentration map</h3><p class="s">Bubble size = projects. Darker = larger top-contractor share. Click a province to filter.</p><svg id="mp" viewBox="0 0 330 520" role="img" aria-label="Province bubble map coloured by top contractor share" style="width:100%;max-height:540px;background:var(--bg);border-radius:8px"></svg><p class="s" style="margin:8px 0 0">Light 0% to dark 50%+ of province value held by one contractor</p></div>
<div class="p"><h3>Contractor concentration ranking</h3><p class="s">Provinces with 30+ projects: top contractor share · top-3 share</p><div id="rk"></div></div></div>
<div class="r"><div class="p"><h3>Cost dispersion of flagged outliers</h3><p class="s">Contract cost vs. z-score within region. Click a dot to flag it for review.</p><div class="sc"><svg id="sp" viewBox="0 0 560 300" role="img" aria-label="Scatter of flagged outlier cost against z-score" style="width:100%;min-width:460px"></svg></div></div>
<div class="p"><h3>Projects to review</h3><p class="s" id="tn"></p><div class="sc"><table id="tb"></table></div><p class="s" style="margin:12px 0 6px">Flagged IDs (<span id="fc">0</span>)</p><textarea id="fl" readonly></textarea><div style="margin-top:8px"><button id="cp" class="a">Copy flagged IDs</button></div></div></div>
<div class="p"><h3>Regional summary</h3><p class="s">Click a row to filter</p><div class="sc"><table id="rt"></table></div></div>
<h2 id="shortlist">5. Review shortlist and key insight</h2>
<div class="r"><div class="p"><h3>Provinces to review first</h3><p class="s">30+ projects, top-quartile contractor concentration and above-median time-adjusted outlier rate</p><div class="sc"><table id="sl"></table></div></div>
<div class="p"><h3>Key insights</h3>
<div class="ins"><b>The leads are local, not national.</b> No contractor dominates nationally, but in a few provinces one contractor holds 36% to 41% of value.</div>
<div class="ins"><b>Costs rose over time.</b> Much of the climb in flagged projects is a cost-level effect, so projects should be compared within the same year.</div>
<div class="ins"><b>Region IV-B stands out</b> on cost flags even after the time adjustment, led by Oriental Mindoro.</div>
<div class="ins"><b>Next step:</b> check shortlisted projects against DPWH Project DIME and COA reports before drawing conclusions.</div></div></div>
<div class="p" id="method"><h3>Method and limitations</h3><p class="s" style="margin:0">Completed projects only. The outlier flag compares a project with its region (and, for the time-adjusted version, region and completion year) but not project type or size. Contractor names are as recorded, so some are truncated and joint ventures are not split. Provinces under 30 projects are left out of concentration rankings. This page is a static snapshot. Source code, notebooks and the full write-up are in the <a href="https://github.com/michaelbacus-lab/dep-data-engineering-open-track">project repository</a>.</p></div>
</div><script>
const D=__DATA__;const R=D.R,P=D.P,O=D.O,Q=D.Q;const S={g:-1,v:-1,f:new Set()};const $=i=>document.getElementById(i);
const xy=(a,b)=>[(b-116)/11*330,(21.5-a)/17*520],fm=n=>n.toLocaleString("en-US"),pc=(x,d=1)=>(x*100).toFixed(d)+"%";
const NOTE={"KPI 1":"Share of projects flagged as unusually costly for their region","KPI 2":"Mean contract cost per project","KPI 3":"Share of total value held by the ten largest contractors","KPI 4":"Typical local concentration (provinces with 30+ projects)","KPI 5":"Share of contracts costing more than their approved budget"};
$("kp").innerHTML=D.K.map(([k,n,v])=>{const val=k=="KPI 2"?"PHP "+v.toFixed(1)+"M":pc(v);return `<div class="k"><div class="s" style="margin:0"><b>${k}</b> · ${n.split(" (")[0]}</div><div class="v">${val}</div><div class="s" style="margin:0">${NOTE[k]}</div></div>`}).join("");
function line(title,series,fmt){const W=360,H=190,l=44,r=8,t=10,b=30,n=Q.length,mx=Math.max(...series.flatMap(s=>s.v))*1.1||1,X=i=>l+i/(n-1)*(W-l-r),Y=v=>H-b-v/mx*(H-b-t);let g="";
for(let k=0;k<=3;k++){const v=mx*k/3;g+=`<line x1="${l}" x2="${W-r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--line)"/><text x="${l-4}" y="${Y(v)+4}" text-anchor="end" font-size="10" fill="var(--mut)">${fmt(v)}</text>`}
Q.forEach((q,i)=>{if(i%3==0)g+=`<text x="${X(i)}" y="${H-10}" text-anchor="middle" font-size="10" fill="var(--mut)">${q[0].replace("20","").replace("Q"," Q")}</text>`});
series.forEach(s=>{g+=`<polyline fill="none" stroke="${s.c}" stroke-width="2" ${s.d?'stroke-dasharray="5 3"':""} points="${s.v.map((v,i)=>X(i)+","+Y(v)).join(" ")}"/>`;s.v.forEach((v,i)=>{g+=`<circle cx="${X(i)}" cy="${Y(v)}" r="${Q[i][7]?6:3}" fill="${Q[i][7]?"none":s.c}" stroke="${Q[i][7]?"#dc2626":s.c}" stroke-width="${Q[i][7]?2:1}"><title>${Q[i][0]} · ${Q[i][1]} projects · ${fmt(v)}</title></circle>`})});
return `<div style="min-width:0"><h3>${title}</h3><svg viewBox="0 0 ${W} ${H}" style="width:100%" role="img" aria-label="${title}">${g}</svg><div class="lg">${series.map(s=>`<span><b style="background:${s.c}"></b>${s.n}</span>`).join("")}</div></div>`}
$("tr").innerHTML=line("KPI 1. High-cost outlier rate",[{n:"Original flag",c:"#B45309",v:Q.map(q=>q[2]*100)},{n:"Time-adjusted",c:"#1F6FEB",v:Q.map(q=>q[3]*100),d:1}],v=>v.toFixed(0)+"%")+line("KPI 2. Average contract cost (PHP M)",[{n:"Average cost",c:"#1F6FEB",v:Q.map(q=>q[4])}],v=>v.toFixed(0))+line("KPI 3. Top-10 contractor share of value",[{n:"Top-10 share",c:"#0F766E",v:Q.map(q=>q[5]*100)}],v=>v.toFixed(0)+"%")+line("KPI 5. Over-budget rate",[{n:"Over-budget",c:"#6D28D9",v:Q.map(q=>q[6]*100)}],v=>v.toFixed(0)+"%");
const yrs=[...new Set(D.S.map(s=>s[1]))].sort(),isl=[...new Set(D.S.map(s=>s[0]))];
$("sg").innerHTML="<tr><th>Island group</th>"+yrs.map(y=>`<th>${y}</th>`).join("")+"</tr>"+isl.map(i=>"<tr><td>"+i+"</td>"+yrs.map(y=>{const s=D.S.find(x=>x[0]==i&&x[1]==y);return s?`<td style="background:color-mix(in srgb,var(--warn) ${Math.min(s[3]*500,60)}%,transparent)">${pc(s[3])} / ${pc(s[4])}<div class="s" style="margin:0">n=${s[2]}</div></td>`:"<td>–</td>"}).join("")+"</tr>").join("");
$("tt").innerHTML=D.T.map(t=>`<div style="margin:10px 0"><div style="display:flex;justify-content:space-between"><span><b>${t[0]}</b> · ${fm(t[1])} contractors</span><span class="s" style="margin:0">projects ${pc(t[2])} · value ${pc(t[3])}</span></div><div class="b" style="margin:3px 0"><i style="width:${t[2]*100}%"></i></div><div class="b" style="margin:0"><i style="width:${t[3]*100}%;background:var(--ok)"></i></div></div>`).join("")+'<div class="lg"><span><b style="background:var(--acc)"></b>Share of projects</span><span><b style="background:var(--ok)"></b>Share of value</span></div>';
$("sl").innerHTML="<tr><th>Province</th><th>Region</th><th>Projects</th><th>Top-1</th><th>Top-3</th><th>Flag rate*</th></tr>"+D.SL.map(s=>`<tr><td>${s[0]}</td><td>${s[1]}</td><td>${s[2]}</td><td>${pc(s[3],0)}</td><td>${pc(s[4],0)}</td><td>${pc(s[5])}</td></tr>`).join("")+'<tr><td colspan="6" class="s" style="text-align:left;white-space:normal">*Time-adjusted outlier rate</td></tr>';
function ids(){const s=new Set();P.forEach((p,i)=>{if((S.g<0||p[1]===S.g)&&(S.v<0||i===S.v))s.add(i)});return s}
function opts(){$("rg").innerHTML='<option value="-1">All regions</option>'+R.map((r,i)=>`<option value="${i}"${i===S.g?" selected":""}>${r}</option>`).join("");
$("pv").innerHTML='<option value="-1">All provinces</option>'+P.map((p,i)=>[p,i]).filter(([p])=>S.g<0||p[1]===S.g).sort((a,b)=>a[0][0].localeCompare(b[0][0])).map(([p,i])=>`<option value="${i}"${i===S.v?" selected":""}>${p[0]}</option>`).join("")}
function draw(){const I=ids(),A=[...I].map(i=>P[i]);const n=A.reduce((a,p)=>a+p[2],0),c=A.reduce((a,p)=>a+p[3],0),ou=A.reduce((a,p)=>a+p[7],0);const big=A.filter(p=>p[2]>=30).sort((a,b)=>b[4]-a[4])[0];
$("kp2").innerHTML=[["Projects",fm(n)],["Contract cost","PHP "+c.toFixed(1)+"B"],["High-cost outliers",fm(ou)],["Most concentrated province",big?`${big[0]}<div class="s" style="margin:0">${pc(big[4],0)} held by one contractor</div>`:"n/a"]].map(([t,v])=>`<div class="k"><div class="s" style="margin:0">${t}</div><div class="v" style="font-size:${t[0]=="M"?18:26}px">${v}</div></div>`).join("");
$("mp").innerHTML=P.map((p,i)=>{const [x,y]=xy(p[8],p[9]),L=90-Math.min(p[4],.5)/.5*60;return `<circle data-i="${i}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(2.5+Math.sqrt(p[2])*.75).toFixed(1)}" fill="hsl(215 80% ${L}%)" stroke="var(--ink)" stroke-width="${i===S.v?3:.6}" stroke-opacity="${i===S.v?1:.35}" opacity="${I.has(i)?1:.12}" style="cursor:pointer"><title>${p[0]}: ${p[2]} projects, top contractor ${pc(p[4],0)}</title></circle>`}).join("");
$("rk").innerHTML=A.filter(p=>p[2]>=30).sort((a,b)=>b[4]-a[4]).slice(0,10).map(p=>`<div class="b"><div style="width:130px;flex:none">${p[0]}</div><div style="flex:1"><i style="width:${p[4]*200}%"></i></div><div style="width:100px;text-align:right;flex:none">${pc(p[4],0)} · ${pc(p[5],0)}</div></div>`).join("")||'<p class="s">No provinces with 30+ projects in this filter.</p>';
const F=O.filter(o=>I.has(o[1])).sort((a,b)=>b[3]-a[3]);const mx=Math.max(1,...F.map(o=>o[2])),zs=F.map(o=>o[3]),z0=Math.min(0,...zs),z1=Math.max(1,...zs),X=v=>44+v/mx*500,Y=v=>270-(v-z0)/(z1-z0)*250;
let sv="";for(let t=0;t<=4;t++){const v=mx*t/4,w=z0+(z1-z0)*t/4;sv+=`<line x1="44" x2="544" y1="${Y(w)}" y2="${Y(w)}" stroke="var(--line)"/><text x="40" y="${Y(w)+4}" text-anchor="end" font-size="11" fill="var(--mut)">${w.toFixed(1)}</text><text x="${X(v)}" y="292" text-anchor="middle" font-size="11" fill="var(--mut)">${v.toFixed(0)}</text>`}
sv+=`<text x="294" y="10" text-anchor="middle" font-size="11" fill="var(--mut)">Contract cost (PHP millions) → · z-score ↑</text>`+F.map(o=>`<circle data-id="${o[0]}" cx="${X(o[2]).toFixed(1)}" cy="${Y(o[3]).toFixed(1)}" r="${S.f.has(o[0])?7:4.5}" fill="${S.f.has(o[0])?"var(--flag)":"var(--warn)"}" fill-opacity=".75" stroke="var(--ink)" stroke-width=".5" style="cursor:pointer"><title>${o[0]} · ${P[o[1]][0]} · PHP ${o[2]}M · z ${o[3]}</title></circle>`).join("");$("sp").innerHTML=sv;
$("tn").textContent=`Top 12 of ${F.length} flagged outliers in this view. Click a row to flag it.`;
$("tb").innerHTML="<tr><th>Project ID</th><th>Province</th><th>Cost PHP M</th><th>z</th></tr>"+F.slice(0,12).map(o=>`<tr data-id="${o[0]}" class="${S.f.has(o[0])?"f":""}"><td>${o[0]}</td><td>${P[o[1]][0]}</td><td>${o[2]}</td><td>${o[3]}</td></tr>`).join("");
$("fc").textContent=S.f.size;$("fl").value=[...S.f].join(", ");
$("rt").innerHTML="<tr><th>Region</th><th>Projects</th><th>Cost PHP B</th><th>Outliers</th><th>Max top-1 share</th></tr>"+R.map((r,g)=>{const q=P.filter(p=>p[1]===g),m=Math.max(0,...q.filter(p=>p[2]>=30).map(p=>p[4]));return `<tr data-g="${g}"><td>${r}</td><td>${fm(q.reduce((a,p)=>a+p[2],0))}</td><td>${q.reduce((a,p)=>a+p[3],0).toFixed(1)}</td><td>${q.reduce((a,p)=>a+p[7],0)}</td><td>${m?pc(m,0):"–"}</td></tr>`}).join("")}
function tog(id){S.f.has(id)?S.f.delete(id):S.f.add(id);draw()}
$("rg").onchange=e=>{S.g=+e.target.value;S.v=-1;opts();draw()};$("pv").onchange=e=>{S.v=+e.target.value;draw()};
$("rs").onclick=()=>{S.g=S.v=-1;opts();draw()};
$("mp").onclick=e=>{const c=e.target.closest("circle");if(c){S.v=+c.dataset.i;S.g=P[S.v][1];opts();draw()}};
$("sp").onclick=e=>{const c=e.target.closest("circle");if(c)tog(c.dataset.id)};
$("tb").onclick=e=>{const r=e.target.closest("tr[data-id]");if(r)tog(r.dataset.id)};
$("rt").onclick=e=>{const r=e.target.closest("tr[data-g]");if(r){S.g=+r.dataset.g;S.v=-1;opts();draw()}};
$("cp").onclick=()=>{const t=$("fl");t.select();try{navigator.clipboard.writeText(t.value)}catch(_){}};
opts();draw();
</script></body></html>'''


def main() -> None:
    data = build_data()
    html = (TEMPLATE.replace("__DATA__", json.dumps(data, separators=(",", ":"), ensure_ascii=False))
            .replace("__N__", f"{data['meta']['n']:,}").replace("__COST__", f"{data['meta']['cost']:,.1f}"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
