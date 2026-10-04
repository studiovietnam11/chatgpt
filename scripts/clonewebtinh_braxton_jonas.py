import os, subprocess, urllib.request, urllib.parse, xml.etree.ElementTree as ET, json, zipfile
from pathlib import Path

SITES = [
    {
        "name":"Braxton",
        "slug":"braxton",
        "seed":"https://braxton.webflow.io/",
        "explicit":[
            "https://braxton.webflow.io/",
            "https://braxton.webflow.io/about",
            "https://braxton.webflow.io/services",
            "https://braxton.webflow.io/projects",
            "https://braxton.webflow.io/blog",
            "https://braxton.webflow.io/shop",
            "https://braxton.webflow.io/contact",
            "https://braxton.webflow.io/checkout",
            "https://braxton.webflow.io/401",
            "https://braxton.webflow.io/404",
            "https://braxton.webflow.io/templete-info/style-guide",
            "https://braxton.webflow.io/templete-info/licenses",
            "https://braxton.webflow.io/templete-info/changelog",
            "https://braxton.webflow.io/projects/boldstream",
            "https://braxton.webflow.io/projects/innovatex",
            "https://braxton.webflow.io/projects/pixelforge",
            "https://braxton.webflow.io/projects/synccraft",
            "https://braxton.webflow.io/projects/cipherworks",
            "https://braxton.webflow.io/projects/spectrashift",
            "https://braxton.webflow.io/projects/nextwave",
            "https://braxton.webflow.io/projects/corevision",
            "https://braxton.webflow.io/blogs/5-design-principles-that-elevate-your-projects",
            "https://braxton.webflow.io/blogs/lessons-learned-from-my-most-challenging-project",
            "https://braxton.webflow.io/blogs/how-storytelling-enhances-your-design-and-branding",
            "https://braxton.webflow.io/blogs/essential-tools-every-creative-professional-should-use",
            "https://braxton.webflow.io/blogs/tips-for-overcoming-creative-blocks-and-staying-productive",
            "https://braxton.webflow.io/blogs/5-ways-to-improve-your-skills-as-a-designer-or-creative",
            "https://braxton.webflow.io/blogs/why-continuous-learning-is-the-key-to-staying-ahead-in-design",
            "https://braxton.webflow.io/blogs/how-to-choose-the-right-designer-for-your-project",
            "https://braxton.webflow.io/blogs/the-importance-of-collaboration-in-successful-projects",
            "https://braxton.webflow.io/product/premium-coffee-mug",
            "https://braxton.webflow.io/product/shopping-bag",
            "https://braxton.webflow.io/product/premium-notebook",
            "https://braxton.webflow.io/product/laptop-mockup-kit",
            "https://braxton.webflow.io/product/design-system-course",
            "https://braxton.webflow.io/product/dashboard-ui-design-kit",
            "https://braxton.webflow.io/projects-categories/motion",
            "https://braxton.webflow.io/projects-categories/devolopment",
            "https://braxton.webflow.io/projects-categories/marketing",
            "https://braxton.webflow.io/projects-categories/web-design",
            "https://braxton.webflow.io/projects-categories/branding",
            "https://braxton.webflow.io/category/digital-goods",
            "https://braxton.webflow.io/category/physical-goods"
        ]
    },
    {
        "name":"Jonas",
        "slug":"jonas",
        "seed":"https://jonas-template.webflow.io/",
        "explicit":[
            "https://jonas-template.webflow.io/",
            "https://jonas-template.webflow.io/work/rule-ratio",
            "https://jonas-template.webflow.io/work/dry-air",
            "https://jonas-template.webflow.io/work/variable-compose",
            "https://jonas-template.webflow.io/work/situation",
            "https://jonas-template.webflow.io/work/vertical",
            "https://jonas-template.webflow.io/work/scope-shift",
            "https://jonas-template.webflow.io/admin/styleguide",
            "https://jonas-template.webflow.io/admin/licenses",
            "https://jonas-template.webflow.io/admin/changelog",
            "https://jonas-template.webflow.io/401",
            "https://jonas-template.webflow.io/404"
        ]
    }
]

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36"
ALLOWED_EXTRA=[
    "cdn.prod.website-files.com","assets.website-files.com","assets-global.website-files.com",
    "uploads-ssl.webflow.com","d3e54v103j8qbb.cloudfront.net",
    "code.jquery.com","cdn.jsdelivr.net","cdnjs.cloudflare.com","unpkg.com",
    "fonts.googleapis.com","fonts.gstatic.com","use.typekit.net","p.typekit.net"
]

def get(u):
    req=urllib.request.Request(u,headers={"User-Agent":UA})
    return urllib.request.urlopen(req,timeout=40).read()

def sitemap_urls(origin):
    seen=set()
    queue=[origin+"sitemap.xml", origin+"sitemap_index.xml"]
    visited=set()
    while queue:
        sm=queue.pop(0)
        if sm in visited: continue
        visited.add(sm)
        try:
            root=ET.fromstring(get(sm))
            locs=[(x.text or "").strip() for x in root.iter() if x.tag.lower().endswith("loc")]
            for u in locs:
                if not u: continue
                if u.endswith(".xml") and u.startswith(origin):
                    queue.append(u)
                elif u.startswith(origin):
                    seen.add(u)
        except Exception as e:
            print("SITEMAP_WARN",sm,repr(e))
    return sorted(seen)

def normalize_url(u):
    p=urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path.rstrip("/") or "/",p.query,""))

def count_types(mirror):
    counts={"html":0,"css":0,"js":0,"images":0,"fonts":0,"other":0}
    image_ext={".png",".jpg",".jpeg",".webp",".gif",".svg",".avif",".ico"}
    font_ext={".woff",".woff2",".ttf",".otf",".eot"}
    for p in mirror.rglob("*"):
        if not p.is_file(): continue
        ext=p.suffix.lower()
        if ext in {".html",".htm"}: counts["html"]+=1
        elif ext==".css": counts["css"]+=1
        elif ext==".js": counts["js"]+=1
        elif ext in image_ext: counts["images"]+=1
        elif ext in font_ext: counts["fonts"]+=1
        else: counts["other"]+=1
    return counts

root=Path("clonewebtinh-braxton-jonas")
root.mkdir(exist_ok=True)
manifest=[]

for site in SITES:
    name,slug,seed=site["name"],site["slug"],site["seed"]
    host=urllib.parse.urlparse(seed).netloc
    origin=f"https://{host}/"
    out=root/slug
    mirror=out/"mirror"
    out.mkdir(parents=True,exist_ok=True)
    urls=sorted({normalize_url(u) for u in (sitemap_urls(origin)+site["explicit"])})
    (out/"SEEDS.txt").write_text("\n".join(urls)+"\n",encoding="utf-8")
    domains=",".join([host]+ALLOWED_EXTRA)
    cmd=[
        "wget","--recursive","--level=inf","--page-requisites","--convert-links","--adjust-extension",
        "--span-hosts",f"--domains={domains}","--execute","robots=off",f"--user-agent={UA}",
        "--timeout=40","--tries=3","--retry-connrefused","--waitretry=1","--no-verbose",
        "--no-clobber",f"--directory-prefix={mirror}",f"--input-file={out/'SEEDS.txt'}"
    ]
    with open(out/"wget.log","w",encoding="utf-8") as log:
        proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=False)
    counts=count_types(mirror)
    local_home=mirror/host/"index.html"
    start=f'<!doctype html><meta charset="utf-8"><title>{name} local start</title><p><a href="mirror/{host}/index.html">Open {name} local clone</a></p>'
    (out/"START-HERE.html").write_text(start,encoding="utf-8")
    routes=[urllib.parse.urlsplit(u).path or "/" for u in urls]
    (out/"ROUTES.md").write_text("# Routes\n\n"+"\n".join("- "+r for r in routes)+"\n",encoding="utf-8")
    info={
        "name":name,"slug":slug,"source":seed,"host":host,"seed_count":len(urls),
        "wget_returncode":proc.returncode,"counts":counts,
        "local_home_exists":local_home.exists()
    }
    (out/"SOURCE-TRUTH.json").write_text(json.dumps(info,indent=2,ensure_ascii=False),encoding="utf-8")
    manifest.append(info)
    print("DONE",name,info)

(root/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
(root/"README.md").write_text(
    "# CloneWebTinh — Braxton + Jonas\n\n"
    "Mirrored directly from live Webflow sources with wget page requisites and link conversion. "
    "The mirror keeps published Webflow HTML/CSS/JS, fonts, and available assets instead of replacing them with a generic stylesheet.\n",
    encoding="utf-8"
)

for slug in ["braxton","jonas"]:
    zipname=f"clonewebtinh-{slug}-source-mirror.zip"
    with zipfile.ZipFile(zipname,"w",zipfile.ZIP_DEFLATED) as z:
        base=root/slug
        for p in base.rglob("*"):
            if p.is_file():
                z.write(p,p.relative_to(root).as_posix())
    print("ZIP",zipname,Path(zipname).stat().st_size)

combined="clonewebtinh-braxton-jonas-source-mirror.zip"
with zipfile.ZipFile(combined,"w",zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob("*"):
        if p.is_file():
            z.write(p,p.relative_to(root.parent).as_posix())
print("ZIP",combined,Path(combined).stat().st_size)
