import re, os, urllib.request, urllib.parse, zipfile, json, shutil
from pathlib import Path

ROOT=Path("clonewebtinh-braxton-jonas")
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36"

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    return urllib.request.urlopen(req,timeout=45).read()

def patch_query_names(mirror):
    n=0
    for p in list(mirror.rglob("*")):
        if p.is_file() and "?" in p.name:
            q=p.with_name(p.name.replace("?","%3F"))
            if not q.exists():
                shutil.copy2(p,q); n+=1
    return n

def localize_braxton_fonts(site_root):
    host="braxton.webflow.io"
    mirror=site_root/"mirror"
    hostroot=mirror/host
    assets=hostroot/"_local"
    fonts=assets/"fonts"
    fonts.mkdir(parents=True,exist_ok=True)
    api="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Bebas+Neue&family=Poppins:wght@400;500;600;700&display=swap"
    css=fetch(api).decode("utf-8","replace")
    urls=re.findall(r"url\\((https://[^)]+)\\)",css)
    mapping={}
    for i,u in enumerate(dict.fromkeys(urls),1):
        ext=".woff2"
        fn=f"font-{i:02d}{ext}"
        data=fetch(u)
        (fonts/fn).write_bytes(data)
        mapping[u]="fonts/"+fn
    for u,local in mapping.items():
        css=css.replace(u,local)
    (assets/"google-fonts.css").write_text(css,encoding="utf-8")
    patched=0
    for h in hostroot.rglob("*.html"):
        s=h.read_text(encoding="utf-8",errors="ignore")
        rel=os.path.relpath(assets/"google-fonts.css",h.parent).replace(os.sep,"/")
        tag=f'<link rel="stylesheet" href="{rel}" data-clonewebtinh-local-fonts="true">'
        if "data-clonewebtinh-local-fonts" not in s:
            s=s.replace("</head>",tag+"</head>")
            h.write_text(s,encoding="utf-8")
            patched+=1
    return {"font_files":len(mapping),"html_patched":patched}

def localize_external_placeholder(site_root,host):
    mirror=site_root/"mirror"
    hostroot=mirror/host
    url="https://cdn.prod.website-files.com/plugins/Basic/assets/placeholder.60f9b1840c.svg"
    target=hostroot/"_local"/"placeholder.svg"
    try:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(fetch(url))
    except Exception as e:
        return {"downloaded":False,"error":repr(e)}
    count=0
    for h in hostroot.rglob("*.html"):
        s=h.read_text(encoding="utf-8",errors="ignore")
        if url in s:
            rel=os.path.relpath(target,h.parent).replace(os.sep,"/")
            s=s.replace(url,rel)
            h.write_text(s,encoding="utf-8")
            count+=1
    return {"downloaded":True,"html_patched":count}

def qa(site_root,host):
    mirror=site_root/"mirror"; hostroot=mirror/host
    htmls=list(hostroot.rglob("*.html"))
    css=list(mirror.rglob("*.css")); js=list(mirror.rglob("*.js*"))
    images=[p for p in mirror.rglob("*") if p.is_file() and p.suffix.lower() in {".png",".jpg",".jpeg",".webp",".gif",".svg",".avif",".ico"}]
    fonts=[p for p in mirror.rglob("*") if p.is_file() and p.suffix.lower() in {".woff",".woff2",".ttf",".otf",".eot"}]
    external=set(); missing=[]
    attr_rx=re.compile(r'''(?:href|src)=["']([^"'#]+)''',re.I)
    for h in htmls:
        s=h.read_text(encoding="utf-8",errors="ignore")
        for v in attr_rx.findall(s):
            if v.startswith(("data:","mailto:","tel:","javascript:")): continue
            if v.startswith(("http://","https://","//")):
                external.add(v)
            else:
                raw=v.split("#",1)[0]
                if not raw: continue
                # Preserve wget's encoded query filename convention.
                p=(h.parent/raw).resolve()
                if not p.exists():
                    missing.append({"page":str(h.relative_to(mirror)),"ref":v})
    return {
        "html":len(htmls),"css":len(css),"js":len(js),"images":len(images),"fonts":len(fonts),
        "external_refs_count":len(external),
        "external_refs":sorted(external),
        "missing_local_refs_count":len(missing),
        "missing_local_refs":missing[:100]
    }

results={}
for slug,host in [("braxton","braxton.webflow.io"),("jonas","jonas-template.webflow.io")]:
    site=ROOT/slug
    patched=patch_query_names(site/"mirror")
    extra={"query_filename_aliases":patched}
    if slug=="braxton":
        try:
            extra["fonts"]=localize_braxton_fonts(site)
        except Exception as e:
            extra["fonts"]={"error":repr(e)}
        extra["placeholder"]=localize_external_placeholder(site,host)
    report=qa(site,host)
    report["fixes"]=extra
    results[slug]=report
    md=["# QA REPORT", "", f"Site: {slug}", f"Source host: {host}", "",
        f"- HTML pages: {report['html']}",
        f"- CSS files: {report['css']}",
        f"- JS files: {report['js']}",
        f"- Image files: {report['images']}",
        f"- Font files: {report['fonts']}",
        f"- Missing local href/src refs: {report['missing_local_refs_count']}",
        f"- External href/src refs remaining: {report['external_refs_count']}",
        "", "## Remaining external refs"]
    md += [f"- {x}" for x in report["external_refs"]] or ["- None"]
    md += ["", "## Missing local refs"]
    md += [f"- {x['page']} -> {x['ref']}" for x in report["missing_local_refs"]] or ["- None"]
    (site/"QA-REPORT.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    (site/"QA-REPORT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")

(ROOT/"FINAL-QA.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")

for slug in ["braxton","jonas"]:
    zipname=f"clonewebtinh-{slug}-FINAL.zip"
    with zipfile.ZipFile(zipname,"w",zipfile.ZIP_DEFLATED) as z:
        base=ROOT/slug
        for p in base.rglob("*"):
            if p.is_file():
                z.write(p,p.relative_to(ROOT).as_posix())
    print("FINAL",zipname,Path(zipname).stat().st_size)

combined="clonewebtinh-braxton-jonas-FINAL.zip"
with zipfile.ZipFile(combined,"w",zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob("*"):
        if p.is_file():
            z.write(p,p.relative_to(ROOT.parent).as_posix())
print("FINAL",combined,Path(combined).stat().st_size)
print(json.dumps(results,indent=2))
