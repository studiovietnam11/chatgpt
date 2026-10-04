import sys, os, json, csv, shutil, zipfile
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

IN=Path(sys.argv[1] if len(sys.argv)>1 else "incoming")
OUT=Path(sys.argv[2] if len(sys.argv)>2 else "CLONEWEBTINH-WEBFLOW-12")
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
stage=Path("_stage_clonewebtinh")
if stage.exists(): shutil.rmtree(stage)
stage.mkdir()
for z in sorted(IN.rglob("clonewebtinh-raw-batch-*.zip")):
    with zipfile.ZipFile(z) as f: f.extractall(stage)

sites=[
("01","Catalysty","catalysty","https://catalysty-temp.webflow.io/"),
("02","Merkil","merkil","https://merkil.webflow.io/"),
("03","Copora","copora","https://copora-wbs.webflow.io/"),
("04","Fer.Do","fer-do","https://fardo-portfolio.webflow.io/"),
("05","Firs","firs","https://firsstudio-template.webflow.io/"),
("06","Fropie","fropie","https://fropie.webflow.io/"),
("07","Fylla","fylla","https://fylla-template.webflow.io/"),
("08","Finox","finox","https://finox.webflow.io/"),
("09","Strobe Home A","strobe-home-a","https://strobe.webflow.io/homepage/home-a"),
("10","Sidenote","sidenote","https://sidenote-template.webflow.io/"),
("11","Boldway","boldway","https://boldway.webflow.io/"),
("12","PrimeFolio","primefolio","https://primefolio.webflow.io/"),
]
summary=[]; index_links=[]
for no,name,slug,seed in sites:
    src=stage/"raw"/slug
    meta=json.loads((src/"SOURCE.json").read_text(encoding="utf-8"))
    host=meta["host"]; dst=OUT/(no+"-"+slug)
    shutil.copytree(src/"mirror",dst/"mirror")
    for a,b in [("SOURCE.json","SOURCE.json"),("seeds.txt","SEEDS.txt"),("wget.log","WGET-LOG.txt")]:
        shutil.copy2(src/a,dst/b)
    hostroot=dst/"mirror"/host
    sp=urlparse(seed).path.strip("/")
    candidate=(hostroot/(sp+".html")) if sp else (hostroot/"index.html")
    if not candidate.exists() and sp: candidate=hostroot/sp/"index.html"
    if not candidate.exists():
        hs=sorted(hostroot.rglob("*.html")); candidate=hs[0] if hs else None
    if candidate:
        rel=os.path.relpath(candidate,dst).replace(os.sep,"/")
        (dst/"index.html").write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url='+rel+'"><title>'+name+'</title><p><a href="'+rel+'">Open '+name+'</a></p>',encoding="utf-8")

    css_refs=set(); remote_css=set(); broken=[]; section_rows=[]
    htmls=sorted(hostroot.rglob("*.html")) if hostroot.exists() else []
    for p in htmls:
        relhost=p.relative_to(hostroot).as_posix()
        soup=BeautifulSoup(p.read_text(encoding="utf-8",errors="ignore"),"html.parser")
        title=soup.title.get_text(" ",strip=True) if soup.title else ""
        h1=soup.find("h1")
        sec=[el for el in soup.find_all(["section","main","article"]) if len(" ".join(el.stripped_strings))>=20 or el.find(["img","video","iframe"])]
        section_rows.append([relhost,title,h1.get_text(" ",strip=True) if h1 else "",len(sec)])
        for l in soup.find_all("link",href=True):
            if "stylesheet" in [str(x).lower() for x in (l.get("rel") or [])]:
                css_refs.add(l["href"])
                if l["href"].startswith(("http://","https://","//")): remote_css.add(l["href"])
        for tag,attrs in {"a":["href"],"img":["src"],"script":["src"],"link":["href"],"source":["src"],"video":["src","poster"]}.items():
            for n in soup.find_all(tag):
                for at in attrs:
                    v=n.get(at)
                    if not v or v.startswith(("http://","https://","//","mailto:","tel:","javascript:","data:","blob:","#")): continue
                    clean=v.split("#",1)[0].split("?",1)[0]
                    if not clean: continue
                    q=(p.parent/clean).resolve()
                    try: q.relative_to(dst.resolve())
                    except Exception: continue
                    if not q.exists(): broken.append((relhost,tag,at,v))

    css_files=sorted((dst/"mirror").rglob("*.css")); js_files=sorted((dst/"mirror").rglob("*.js"))
    all_files=[p for p in (dst/"mirror").rglob("*") if p.is_file()]
    assets=[p for p in all_files if p.suffix.lower() in {".jpg",".jpeg",".png",".webp",".avif",".svg",".gif",".woff",".woff2",".ttf",".otf",".mp4",".webm",".mov"}]
    css_ok=len(css_files)>0 and len(remote_css)==0

    (dst/"ROUTES.md").write_text("# ROUTES — "+name+"\\n\\nSource: "+seed+"\\n\\nTotal downloaded HTML routes: **"+str(len(htmls))+"**\\n\\n"+"\\n".join("- "+p.relative_to(hostroot).as_posix() for p in htmls),encoding="utf-8")
    (dst/"DESIGN.md").write_text("# DESIGN — "+name+"\\n\\n- Source of truth: published Webflow HTML + published stylesheets/assets.\\n- No generic redesign CSS introduced.\\n- CSS files: **"+str(len(css_files))+"**\\n- JS files: **"+str(len(js_files))+"**\\n- Media/font assets: **"+str(len(assets))+"**\\n\\n## Stylesheets\\n"+"\\n".join("- "+x for x in sorted(css_refs)),encoding="utf-8")
    (dst/"SOURCE-TRUTH.md").write_text("# SOURCE TRUTH — "+name+"\\n\\n- Seed: "+seed+"\\n- Origin host: "+host+"\\n- Origin HTML files: **"+str(len(htmls))+"**\\n- Mirrored files: **"+str(len(all_files))+"**\\n- Published CSS localized: **"+("PASS" if css_ok else "REVIEW")+"**\\n- Remote CSS remaining: **"+str(len(remote_css))+"**\\n- Broken local refs: **"+str(len(broken))+"**\\n\\nDOM/class names and Webflow-published CSS/JS/assets are preserved wherever returned by the live source/CDNs.\\n",encoding="utf-8")
    qa=["# QA REPORT — "+name,"","- Routes/HTML captured: **"+str(len(htmls))+"**","- CSS files: **"+str(len(css_files))+"**","- JS files: **"+str(len(js_files))+"**","- Assets/fonts/media: **"+str(len(assets))+"**","- Remote CSS refs remaining: **"+str(len(remote_css))+"**","- Broken local refs: **"+str(len(broken))+"**","","## CSS status",("PASS — published CSS is present locally and stylesheet links are localized." if css_ok else "REVIEW — stylesheet localization needs attention."),"","## Broken references (first 100)"]
    qa += ["- "+a+" — "+b+"["+c+"] -> "+d for a,b,c,d in broken[:100]] or ["- None detected."]
    if remote_css: qa += ["","## Remote stylesheet references"]+["- "+x for x in sorted(remote_css)]
    (dst/"QA-REPORT.md").write_text("\\n".join(qa),encoding="utf-8")
    with (dst/"PAGE-INVENTORY.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["route_file","title","h1","section_like_count"]); w.writerows(section_rows)
    x={"no":no,"name":name,"slug":slug,"seed":seed,"routes":len(htmls),"files":len(all_files),"css":len(css_files),"js":len(js_files),"assets":len(assets),"remote_css":len(remote_css),"broken_refs":len(broken),"css_status":"PASS" if css_ok else "REVIEW"}
    summary.append(x)
    index_links.append('<li><a href="'+no+'-'+slug+'/index.html">'+no+'. '+name+'</a> — '+str(len(htmls))+' HTML, '+str(len(css_files))+' CSS, CSS '+x["css_status"]+'</li>')

(OUT/"INDEX.html").write_text("<!doctype html><meta charset='utf-8'><title>CloneWebTinh Webflow 12</title><h1>CloneWebTinh — 12 Webflow sites</h1><ol>"+"".join(index_links)+"</ol>",encoding="utf-8")
with (OUT/"MASTER-QA.csv").open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
md=["# MASTER QA — 12 Webflow clones","", "| # | Site | Routes | Files | CSS | Assets | Remote CSS | Broken refs | CSS status |","|---:|---|---:|---:|---:|---:|---:|---:|---|"]
for x in summary: md.append("| "+x["no"]+" | "+x["name"]+" | "+str(x["routes"])+" | "+str(x["files"])+" | "+str(x["css"])+" | "+str(x["assets"])+" | "+str(x["remote_css"])+" | "+str(x["broken_refs"])+" | "+x["css_status"]+" |")
(OUT/"QA-REPORT.md").write_text("\\n".join(md),encoding="utf-8")
(OUT/"README.md").write_text("# /clonewebtinh — Webflow 12\\n\\nMở từng thư mục site rồi mở index.html. Source HTML/class/CSS/JS/assets được mirror từ live Webflow. Xem ROUTES.md, SOURCE-TRUTH.md, DESIGN.md, QA-REPORT.md trong từng site.\\n",encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
