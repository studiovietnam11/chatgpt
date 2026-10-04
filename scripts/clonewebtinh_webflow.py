import os, sys, subprocess, urllib.request, urllib.parse, xml.etree.ElementTree as ET, json, zipfile
from pathlib import Path

SITES = [
("Catalysty","catalysty","https://catalysty-temp.webflow.io/"),
("Merkil","merkil","https://merkil.webflow.io/"),
("Copora","copora","https://copora-wbs.webflow.io/"),
("Fer.Do","fer-do","https://fardo-portfolio.webflow.io/"),
("Firs","firs","https://firsstudio-template.webflow.io/"),
("Fropie","fropie","https://fropie.webflow.io/"),
("Fylla","fylla","https://fylla-template.webflow.io/"),
("Finox","finox","https://finox.webflow.io/"),
("Strobe Home A","strobe-home-a","https://strobe.webflow.io/homepage/home-a"),
("Sidenote","sidenote","https://sidenote-template.webflow.io/"),
("Boldway","boldway","https://boldway.webflow.io/"),
("PrimeFolio","primefolio","https://primefolio.webflow.io/"),
]
batch=int(sys.argv[1]) if len(sys.argv)>1 else 1
sites=SITES[:6] if batch==1 else SITES[6:]
root=Path("raw"); root.mkdir(exist_ok=True)
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36"

def get(u):
    req=urllib.request.Request(u,headers={"User-Agent":UA})
    return urllib.request.urlopen(req,timeout=30).read()

def sitemap_urls(origin):
    seen={origin}
    queue=[origin+"sitemap.xml",origin+"sitemap_index.xml"]
    visited=set()
    while queue:
        sm=queue.pop(0)
        if sm in visited: continue
        visited.add(sm)
        try:
            r=ET.fromstring(get(sm))
            locs=[(x.text or "").strip() for x in r.iter() if x.tag.lower().endswith("loc")]
            for u in locs:
                if u.endswith(".xml") and u.startswith(origin):
                    queue.append(u)
                elif u.startswith(origin):
                    seen.add(u)
        except Exception as e:
            print("sitemap",sm,repr(e))
    return sorted(seen)

for name,slug,seed in sites:
    host=urllib.parse.urlparse(seed).netloc
    origin=f"https://{host}/"
    out=root/slug
    out.mkdir(parents=True,exist_ok=True)
    urls=sorted(set(sitemap_urls(origin)+[seed]))
    (out/"seeds.txt").write_text("\n".join(urls)+"\n",encoding="utf-8")
    domains=",".join([host,"cdn.prod.website-files.com","assets.website-files.com","assets-global.website-files.com","uploads-ssl.webflow.com","d3e54v103j8qbb.cloudfront.net","code.jquery.com","cdn.jsdelivr.net","cdnjs.cloudflare.com","unpkg.com","fonts.googleapis.com","fonts.gstatic.com","use.typekit.net","p.typekit.net"])
    mirror=out/"mirror"
    cmd=["wget","--recursive","--level=inf","--page-requisites","--convert-links","--adjust-extension","--span-hosts",f"--domains={domains}","--execute","robots=off",f"--user-agent={UA}","--timeout=30","--tries=3","--retry-connrefused","--waitretry=1","--no-verbose",f"--directory-prefix={mirror}",f"--input-file={out/'seeds.txt'}"]
    with open(out/"wget.log","w",encoding="utf-8") as log:
        subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=False)
    meta={"name":name,"slug":slug,"seed":seed,"origin":origin,"host":host,"seed_count":len(urls)}
    (out/"SOURCE.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    print("DONE",name,"files",sum(1 for p in mirror.rglob("*") if p.is_file()),"seeds",len(urls))

zipname=f"clonewebtinh-raw-batch-{batch}.zip"
with zipfile.ZipFile(zipname,"w",zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob("*"):
        if p.is_file():
            z.write(p,p.as_posix())
print("ZIP",zipname,Path(zipname).stat().st_size)
