#!/usr/bin/env python3
import os, re, sys, csv, json, shutil, hashlib, threading, time
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

SITES = [
{"name":"Catalysty","slug":"catalysty","seed":"https://catalysty-temp.webflow.io/"},
{"name":"Merkil","slug":"merkil","seed":"https://merkil.webflow.io/"},
{"name":"Copora","slug":"copora","seed":"https://copora-wbs.webflow.io/"},
{"name":"Fer.Do","slug":"fer-do","seed":"https://fardo-portfolio.webflow.io/"},
{"name":"Firs","slug":"firs","seed":"https://firsstudio-template.webflow.io/"},
{"name":"Fropie","slug":"fropie","seed":"https://fropie.webflow.io/"},
{"name":"Fylla","slug":"fylla","seed":"https://fylla-template.webflow.io/"},
{"name":"Finox","slug":"finox","seed":"https://finox.webflow.io/"},
{"name":"Strobe Home A","slug":"strobe-home-a","seed":"https://strobe.webflow.io/homepage/home-a"},
{"name":"Sidenote","slug":"sidenote","seed":"https://sidenote-template.webflow.io/"},
{"name":"Boldway","slug":"boldway","seed":"https://boldway.webflow.io/"},
{"name":"PrimeFolio","slug":"primefolio","seed":"https://primefolio.webflow.io/"},
]

RAW=Path(sys.argv[1] if len(sys.argv)>1 else "raw")
OUT=Path(sys.argv[2] if len(sys.argv)>2 else "clonewebtinh-webflow-12")
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)

def csvwrite(p, head, rows):
    with open(p,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(head); w.writerows(rows)

def route_from_rel(rel):
    s=rel.replace(os.sep,"/")
    if s=="index.html": return "/"
    if s.endswith("/index.html"): return "/"+s[:-10].strip("/")+"/"
    if s.endswith(".html"): return "/"+s[:-5]
    return "/"+s

def seed_target(seed, host):
    p=urlparse(seed).path or "/"
    if p=="/": return f"mirror/{host}/index.html"
    p=p.lstrip("/")
    if p.endswith("/"): return f"mirror/{host}/{p}index.html"
    return f"mirror/{host}/{p}.html"

def css_design(css_files):
    fonts=[]; colors=[]; vars_=[]; breaks=[]
    for fp in css_files[:80]:
        try: txt=fp.read_text(encoding="utf-8",errors="ignore")
        except: continue
        fonts += re.findall(r"font-family\s*:\s*([^;}{]+)",txt,re.I)
        colors += re.findall(r"#[0-9a-fA-F]{3,8}\b",txt)
        vars_ += re.findall(r"(--[A-Za-z0-9_-]+)\s*:",txt)
        breaks += re.findall(r"@media\s*\(([^)]+)\)",txt,re.I)
    def uniq(items,n=40):
        seen=[]; keys=set()
        for x in items:
            x=re.sub(r"\s+"," ",x.strip())
            if not x or x in keys: continue
            keys.add(x); seen.append(x)
            if len(seen)>=n: break
        return seen
    return uniq(fonts,30), uniq(colors,40), uniq(vars_,60), uniq(breaks,30)

master=[]
for site in SITES:
    name,slug,seed=site["name"],site["slug"],site["seed"]
    src=RAW/slug
    if not src.exists():
        master.append([name,slug,"MISSING_RAW",0,0,0,0,0]); continue
    dst=OUT/slug
    dst.mkdir(parents=True)
    mirror_src=src/"mirror"
    mirror_dst=dst/"mirror"
    shutil.copytree(mirror_src,mirror_dst,dirs_exist_ok=True)
    for fn in ["SOURCE.json","seeds.txt","wget.log"]:
        if (src/fn).exists(): shutil.copy2(src/fn,dst/fn)

    u=urlparse(seed); host=u.netloc
    hostdir=mirror_dst/host
    htmls=sorted(hostdir.rglob("*.html")) if hostdir.exists() else []
    css_files=sorted(mirror_dst.rglob("*.css"))
    js_files=sorted(mirror_dst.rglob("*.js"))
    assets=[p for p in mirror_dst.rglob("*") if p.is_file()]
    route_rows=[]; section_rows=[]; broken=[]; pages_with_css=0
    for fp in htmls:
        rel=fp.relative_to(hostdir)
        route=route_from_rel(str(rel))
        try:
            txt=fp.read_text(encoding="utf-8",errors="ignore")
            soup=BeautifulSoup(txt,"html.parser")
        except Exception as e:
            route_rows.append([route,str(rel),"PARSE_ERR",0,0,0,0,0]); continue
        title=soup.title.get_text(" ",strip=True) if soup.title else ""
        h1=len(soup.find_all("h1")); h2=len(soup.find_all("h2"))
        secs=soup.find_all("section")
        if not secs:
            main=soup.find("main")
            if main: secs=[x for x in main.find_all(recursive=False) if getattr(x,"name",None)]
        css_refs=[]
        for x in soup.find_all("link",href=True):
            rels=[z.lower() for z in (x.get("rel") or [])]
            if "stylesheet" in rels: css_refs.append(x["href"])
        if css_refs: pages_with_css+=1
        route_rows.append([route,str(rel),title,len(txt),len(secs),h1,h2,len(css_refs)])
        for i,s in enumerate(secs,1):
            hh=s.find(["h1","h2","h3","h4"])
            stitle=hh.get_text(" ",strip=True)[:180] if hh else " ".join(s.stripped_strings)[:180]
            section_rows.append([route,i,s.name,s.get("id","")," ".join(s.get("class") or [])[:220],stitle,len(" ".join(s.stripped_strings))])
        for tag,attr in [("a","href"),("img","src"),("script","src"),("link","href"),("source","src"),("video","src"),("video","poster")]:
            for el in soup.find_all(tag):
                v=el.get(attr)
                if not v or v.startswith(("#","http://","https://","//","mailto:","tel:","javascript:","data:","blob:")): continue
                vv=v.split("#",1)[0].split("?",1)[0]
                if not vv: continue
                p=(fp.parent/unquote(vv)).resolve()
                try: p.relative_to(mirror_dst.resolve())
                except: continue
                if not p.exists(): broken.append([route,tag,attr,vv])
    csvwrite(dst/"ROUTE-INVENTORY.csv",["route","local_file","title","html_bytes","section_count","h1_count","h2_count","css_ref_count"],route_rows)
    csvwrite(dst/"SECTION-MATRIX.csv",["route","index","tag","id","class","heading_or_text","text_chars"],section_rows)
    csvwrite(dst/"BROKEN-REFS.csv",["route","tag","attr","target"],broken)

    fonts,colors,vars_,breaks=css_design(css_files)
    launcher=seed_target(seed,host)
    launcher_exists=(dst/launcher).exists()
    if not launcher_exists:
        alt=f"mirror/{host}/index.html"
        if (dst/alt).exists(): launcher=alt; launcher_exists=True
    (dst/"index.html").write_text(f"""<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={launcher}"><title>{name}</title><style>body{{font-family:Arial,sans-serif;padding:40px}}a{{font-size:20px}}</style></head><body><a href="{launcher}">Open {name}</a></body></html>""",encoding="utf-8")

    seeds=(src/"seeds.txt").read_text(encoding="utf-8",errors="ignore").splitlines() if (src/"seeds.txt").exists() else [seed]
    (dst/"ROUTES.md").write_text("# ROUTES — "+name+"\n\nSource-discovered URLs: **"+str(len(seeds))+"**. Mirrored HTML routes: **"+str(len(route_rows))+"**.\n\n"+ "\n".join(f"- `{r[0]}` → `mirror/{host}/{r[1]}`" for r in route_rows),encoding="utf-8")
    (dst/"SOURCE-TRUTH.md").write_text(f"""# SOURCE TRUTH — {name}

- Live source: {seed}
- Published host: {host}
- Method: Webflow published HTML + original linked CSS/JS/assets mirrored with recursive page requisites and link conversion.
- Source-discovered URLs: {len(seeds)}
- Mirrored HTML pages on source host: {len(route_rows)}
- CSS files mirrored: {len(css_files)}
- JS files mirrored: {len(js_files)}
- Total mirrored files: {len(assets)}
- No generic replacement stylesheet was generated.
- Entry launcher: index.html → {launcher}
""",encoding="utf-8")
    (dst/"DESIGN.md").write_text("# DESIGN DNA — "+name+"\n\nThis file is extracted from the mirrored published CSS; values below are not guessed.\n\n## Font-family declarations\n"+("\n".join(f"- `{x}`" for x in fonts) or "- none detected")+"\n\n## Color tokens observed\n"+("\n".join(f"- `{x}`" for x in colors) or "- none detected")+"\n\n## CSS custom properties\n"+("\n".join(f"- `{x}`" for x in vars_) or "- none detected")+"\n\n## Media-query conditions\n"+("\n".join(f"- `{x}`" for x in breaks) or "- none detected")+"\n",encoding="utf-8")
    status="PASS" if launcher_exists and len(route_rows)>0 and pages_with_css>0 else "FAIL"
    if broken: status="WARN" if status=="PASS" else status
    (dst/"QA-REPORT.md").write_text(f"""# QA REPORT — {name}

- Status: **{status}**
- Launcher target exists: {launcher_exists}
- HTML routes: {len(route_rows)}
- Section records: {len(section_rows)}
- Pages containing stylesheet references: {pages_with_css}/{len(route_rows)}
- CSS files: {len(css_files)}
- JS files: {len(js_files)}
- Mirrored files total: {len(assets)}
- Broken local refs detected: {len(broken)}

## Fidelity guardrails
- Published Webflow CSS retained; no synthesized generic CSS.
- Published DOM/class names retained from downloaded HTML.
- Internal page crawl includes sitemap URLs plus recursive same-host links.
- External Webflow/CDN prerequisites were mirrored when referenced and reachable.
- See ROUTE-INVENTORY.csv, SECTION-MATRIX.csv and BROKEN-REFS.csv for page-level evidence.
""",encoding="utf-8")
    master.append([name,slug,status,len(route_rows),len(section_rows),len(css_files),len(assets),len(broken)])

csvwrite(OUT/"MASTER-QA.csv",["site","slug","status","html_routes","sections","css_files","mirrored_files","broken_local_refs"],master)
readme=["# /clonewebtinh — 12 Webflow sites","", "Serve this directory through a local static server for the most reliable behavior:", "", "    python -m http.server 8080", "", "Then open each `/<slug>/index.html`.", "", "## Sites"]
for r in master:
    readme.append(f"- {r[0]} — `/{r[1]}/index.html` — {r[2]} — {r[3]} routes")
(OUT/"README.md").write_text("\n".join(readme)+"\n",encoding="utf-8")
print(json.dumps({"master":master},ensure_ascii=False))
