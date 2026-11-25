
import requests
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import fitz, json, re, unicodedata, shutil, uuid, subprocess, os, zipfile, ftplib, ssl, urllib.request, time

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "issues"
UPLOADS = BASE / "uploads"
GENERATED = BASE / "generated"
STATIC = BASE / "app" / "static"

app = FastAPI(title="Skutečské noviny Digital")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/generated", StaticFiles(directory=GENERATED), name="generated")
templates = Jinja2Templates(directory=BASE / "app" / "templates")

def historical_lexicon() -> set[str]:
    words=set()
    for p in DATA.glob("*.json"):
        try:
            d=json.loads(p.read_text(encoding="utf-8"))
            for a in d.get("articles",[]):
                for w in re.findall(r"[A-Za-zÁ-ž]{4,}", a.get("text","").lower()):
                    words.add(w)
        except Exception: pass
    return words

def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\ufffe","").replace("\u00ad","")
    lex = historical_lexicon()

    def join_hyphen(m):
        left, right = m.group(1), m.group(2)
        joined = (left + right).lower()
        # Typický PDF zlom: "objek- tu", "pří- stupu", "kan- celářím".
        # Mezera nebo nový řádek za spojovníkem je silný signál dělení slova.
        if joined in lex or right[:1].islower():
            return left + right
        return left + "-" + right

    # DŮLEŽITÉ: funguje pro nový řádek i pro mezery vzniklé spojením PDF bloků.
    text = re.sub(
        r'([A-Za-zÁ-ž]{2,})-[ \t\r\n]+([a-zá-ž][A-Za-zÁ-ž]*)',
        join_hyphen,
        text
    )
    text = re.sub(r'\s*\n\s*', ' ', text)
    return re.sub(r'[ \t]+', ' ', text).strip()

def article_checks(a: dict) -> dict:
    errors=[]
    warnings=[]
    title=(a.get("title") or "").strip()
    text=(a.get("text") or "").strip()
    has_media=bool(a.get("images") or a.get("regions"))
    if not title or title=="Nový článek":
        errors.append("Položka nemá vyplněný nadpis.")
    if a.get("type","article")=="visual":
        if not has_media:
            errors.append("Obrazový příspěvek nemá vybraný obrázek ani oblast.")
        return {"errors":errors,"warnings":warnings}
    # Prázdný nebo krátký text je u obrazových položek, vzpomínek a krátkých oznámení validní.
    if text:
        low=text.lower()
        if title and low.startswith(title.lower()):
            warnings.append("Text začíná zopakovaným nadpisem.")
        if re.search(r"[A-Za-zÁ-ž]-\s*$",text):
            warnings.append("Text končí rozděleným slovem.")
        paras=[p.strip() for p in re.split(r"\n\s*\n|\n",text) if p.strip()]
        if len(paras)!=len(set(paras)):
            warnings.append("V článku je duplicitní odstavec.")
    return {"errors":errors,"warnings":warnings}

def article_warnings(a: dict) -> list[str]:
    return article_checks(a)["warnings"]

def category_guess(text: str):
    t=text.lower()
    rules=[("odpad","Odpad",["odpad","svoz","popelnic","recykl"]),
    ("doprava","Doprava",["doprava","silnic","uzavír","parkov","chodník"]),
    ("investice","Investice",["rekonstruk","investic","stavb","oprava"]),
    ("kultura","Kultura",["koncert","divadl","festival","kultur"]),
    ("skolstvi","Školství",["škola","školní","žák","student","mateřsk"]),
    ("sport","Sport",["sport","fotbal","hokej","turnaj","závod"]),
    ("knihovna","Knihovna",["knihovn","kniha","čtenář"]),
    ("muzeum","Muzeum",["muze","expozic","výstav"]),
    ("socialni","Sociální oblast",["sociál","senior","pečovat"]),
    ("ekonomika","Ekonomika",["rozpočet","finance","hospodař"]),
    ("spolky","Spolky",["spolek","hasič","skaut"]),
    ("historie","Historie",["histor","výročí","před lety"]),
    ("pozvanky","Pozvánky",["zveme","pozván","uskuteční se"]),
    ("radnice","Z radnice",["radnice","městský úřad","zastupitel","rada města"])]
    for slug,label,keys in rules:
        if any(k in t for k in keys): return slug,label
    return "ostatni","Ostatní"

def suggest_articles(issue: dict):
    # Conservative layout heuristic learned from previously approved issues:
    # short blocks act as title candidates; following same-column blocks are grouped until next title.
    approved=[]
    for p in DATA.glob("*.json"):
        try:
            d=json.loads(p.read_text(encoding="utf-8"))
            approved += [a for a in d.get("articles",[]) if a.get("approved")]
        except Exception: pass
    title_max=max(90, int(sum(len(a.get("title","")) for a in approved)/max(1,len(approved))*2.2)) if approved else 90
    out=[]
    for page in issue.get("pages",[]):
        bs=page.get("blocks",[])
        candidates=[i for i,b in enumerate(bs) if 3<=len(b["text"].strip())<=title_max and len(b["text"].split())<=12 and not b["text"].strip().endswith((".",",",";"))]
        for ci,i in enumerate(candidates):
            title=bs[i]; x0,y0,x1,y1=title["bbox"]; ids=[]
            stop=candidates[ci+1] if ci+1<len(candidates) else len(bs)
            for b in bs[i+1:stop]:
                bx0,by0,bx1,by1=b["bbox"]
                overlap=max(0,min(x1,bx1)-max(x0,bx0))/max(1,min(x1-x0,bx1-bx0))
                if overlap>.45 or abs(bx0-x0)<45: ids.append(b["id"])
            if ids:
                text=" ".join(next(x["text"] for x in bs if x["id"]==bid) for bid in ids)
                cat,label=category_guess(title["text"]+" "+text)
                out.append({"id":str(uuid.uuid4()),"title":title["text"],"headline":title["id"],"blocks":ids,"images":[],"regions":[],"text":text,"content":[{"type":"paragraph","text":text}],"manuallyEdited":False,"type":"article","category":cat,"categoryLabel":label,"approved":False,"suggested":True})
    # remove likely duplicates/very weak proposals
    seen=set(); clean=[]
    for a in out:
        key=a["title"].lower()
        if key not in seen and len(a["text"])>80:
            seen.add(key); clean.append(a)
    return clean[:80]


def text_quality(text: str) -> dict:
    """Heuristika: pozná rozbitý PDF encoding typu ýW\ĜOHWp..."""
    sample = text[:30000]
    letters = [c for c in sample if c.isalpha()]
    if not letters:
        return {"score": 0.0, "broken": True, "reason": "bez textu"}
    suspicious_chars = set("Ĝþÿ￾ýĢĤĜĖ")
    suspicious = sum(c in suspicious_chars for c in sample)
    tokens = re.findall(r"[A-Za-zÁ-ž]{4,}", sample)
    mojibake_tokens = sum(
        bool(re.search(r"[A-Z]{2,}[a-z]|[A-Z][a-z]?[A-Z]{2,}|[ĜþýĢĤĖ]", t))
        for t in tokens
    )
    ratio = mojibake_tokens / max(len(tokens), 1)
    score = max(0.0, 1.0 - min(1.0, ratio * 2.2 + suspicious / max(len(letters),1) * 5))
    return {
        "score": round(score, 3),
        "broken": score < 0.58,
        "reason": f"podezřelé tokeny {mojibake_tokens}/{len(tokens)}, podezřelé znaky {suspicious}"
    }

def find_tesseract():
    candidates = [
        shutil.which("tesseract"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    return next((str(p) for p in candidates if p and Path(p).exists()), None)

def ocr_page_blocks(page, pno: int):
    tess = find_tesseract()
    if not tess:
        raise RuntimeError(
            "PDF má rozbitou textovou vrstvu a vyžaduje OCR, ale Tesseract nebyl nalezen. "
            "Zavři aplikaci a spusť znovu run.bat; V1.5 Tesseract automaticky doinstaluje."
        )
    tmp = GENERATED / "_ocr_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    image = tmp / f"ocr-{uuid.uuid4().hex}.png"
    tsv = tmp / f"ocr-{uuid.uuid4().hex}"
    pix = page.get_pixmap(matrix=fitz.Matrix(300/72,300/72), alpha=False)
    pix.save(image)
    env = os.environ.copy()
    cmd = [tess, str(image), str(tsv), "-l", "ces", "--psm", "3", "tsv"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    image.unlink(missing_ok=True)
    tsv_file = Path(str(tsv) + ".tsv")
    if proc.returncode != 0 or not tsv_file.exists():
        raise RuntimeError("České OCR selhalo: " + (proc.stderr.strip() or "neznámá chyba"))
    rows = tsv_file.read_text(encoding="utf-8", errors="replace").splitlines()
    tsv_file.unlink(missing_ok=True)
    groups = {}
    for row in rows[1:]:
        cols = row.split("\t", 11)
        if len(cols) < 12: continue
        try:
            level, block, par, left, top, width, height, conf = int(cols[0]), int(cols[2]), int(cols[3]), int(cols[6]), int(cols[7]), int(cols[8]), int(cols[9]), float(cols[10])
        except ValueError:
            continue
        word = cols[11].strip()
        if level != 5 or not word or conf < 25: continue
        key=(block,par)
        g=groups.setdefault(key, {"words":[], "x0":left, "y0":top, "x1":left+width, "y1":top+height})
        g["words"].append(word)
        g["x0"]=min(g["x0"],left); g["y0"]=min(g["y0"],top)
        g["x1"]=max(g["x1"],left+width); g["y1"]=max(g["y1"],top+height)
    scale=72/300
    blocks=[]
    for i,g in enumerate(sorted(groups.values(), key=lambda x:(x["y0"],x["x0"])),1):
        text=clean_text("\n".join(g["words"]))
        if not text: continue
        blocks.append({
            "id":f"p{pno}-ocr{i:03d}",
            "bbox":[round(g[k]*scale,2) for k in ("x0","y0","x1","y1")],
            "text":text
        })
    return blocks

def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+","-",s).strip("-").lower() or "clanek"

templates.env.globals["slugify"] = slugify

def issue_path(issue_id): return DATA / f"{issue_id}.json"

def load_issue(issue_id):
    p = issue_path(issue_id)
    if not p.exists(): raise HTTPException(404)
    return json.loads(p.read_text(encoding="utf-8"))

def save_issue(data):
    issue_path(data["id"]).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def public_archive(request: Request):
    issues=[]
    for p in DATA.glob("*.json"):
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("published"): issues.append(d)
    issues.sort(key=lambda x:(x["year"],x["month"]), reverse=True)
    return templates.TemplateResponse(request, "archive.html", {"issues": issues})

@app.get("/admin/", response_class=HTMLResponse)
def admin(request: Request):
    issues=[json.loads(p.read_text(encoding="utf-8")) for p in DATA.glob("*.json")]
    issues.sort(key=lambda x:(x["year"],x["month"]), reverse=True)
    return templates.TemplateResponse(request, "admin.html", {"issues": issues})

@app.post("/admin/upload")
async def upload_issue(pdf: UploadFile=File(...), month:int=Form(...), year:int=Form(...)):
    issue_id=f"{year}-{month:02d}"
    pdf_file=UPLOADS/f"{issue_id}.pdf"
    with pdf_file.open("wb") as f: shutil.copyfileobj(pdf.file,f)

    doc=fitz.open(pdf_file)
    native_sample = " ".join(page.get_text("text") for page in doc)
    quality = text_quality(native_sample)
    use_ocr = quality["broken"]
    issue_dir=GENERATED/issue_id
    if issue_dir.exists(): shutil.rmtree(issue_dir)
    (issue_dir/"pages").mkdir(parents=True)
    pages=[]
    for pno,page in enumerate(doc,1):
        texts=[]; images=[]; ti=ii=0
        page_dict = page.get_text("dict")
        if use_ocr:
            texts = ocr_page_blocks(page, pno)
        for b in page_dict["blocks"]:
            if b.get("type")==0 and not use_ocr:
                lines=[]
                for line in b.get("lines",[]):
                    t="".join(s.get("text","") for s in line.get("spans",[]))
                    if t.strip(): lines.append(t)
                raw="\n".join(lines).strip()
                if raw:
                    ti+=1
                    texts.append({"id":f"p{pno}-b{ti:03d}","bbox":[round(v,2) for v in b["bbox"]],"text":clean_text(raw)})
            elif b.get("type")==1:
                x0,y0,x1,y1=b["bbox"]
                if (x1-x0)>=35 and (y1-y0)>=35:
                    ii+=1
                    images.append({"id":f"p{pno}-img{ii:03d}","bbox":[round(v,2) for v in b["bbox"]]})
        pix=page.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False)
        img=f"page-{pno:02d}.jpg"
        pix.save(issue_dir/"pages"/img,jpg_quality=88)
        pages.append({"page":pno,"width":page.rect.width,"height":page.rect.height,"image":f"/generated/{issue_id}/pages/{img}","blocks":texts,"images":images})
    data={"id":issue_id,"month":month,"year":year,"pdf":str(pdf_file.relative_to(BASE)),"pages":pages,"articles":[],"published":False,
          "extraction":{"mode":"ocr" if use_ocr else "pdf-text","quality":quality}}
    save_issue(data)
    return RedirectResponse(f"/admin/editor/{issue_id}",303)

@app.get("/admin/editor/{issue_id}", response_class=HTMLResponse)
def editor(request:Request, issue_id:str):
    issue=load_issue(issue_id)
    return templates.TemplateResponse(request, "editor.html", {"issue": issue, "issue_json": json.dumps(issue, ensure_ascii=False)})

@app.post("/admin/api/issues/{issue_id}/save")
async def save_editor(issue_id:str, request:Request):
    current=load_issue(issue_id)
    payload=await request.json()
    current["articles"]=payload.get("articles",[])
    save_issue(current)
    return {"ok":True}

@app.post("/admin/api/issues/{issue_id}/publish")
async def publish(issue_id:str, request:Request):
    current=load_issue(issue_id)
    payload=await request.json()
    current["articles"]=payload.get("articles",current["articles"])
    pending=[a for a in current["articles"] if not a.get("approved")]
    if pending:
        return JSONResponse({"ok":False,"error":f"{len(pending)} článků není schváleno."}, status_code=400)
    current["published"]=True
    save_issue(current)
    return {"ok":True,"url":f"/{current['year']}/{current['month']:02d}/"}



@app.post("/admin/api/issues/{issue_id}/suggest")
def suggest(issue_id:str):
    current=load_issue(issue_id)
    if current.get("articles"):
        return JSONResponse({"ok":False,"error":"Návrhy lze vytvořit jen u vydání bez článků. Existující práci nemažu."},status_code=400)
    current["articles"]=suggest_articles(current)
    save_issue(current)
    return {"ok":True,"count":len(current["articles"])}

@app.post("/admin/api/issues/{issue_id}/validate")
async def validate_issue(issue_id:str, request:Request):
    current=load_issue(issue_id); payload=await request.json()
    arts=payload.get("articles",current.get("articles",[]))
    return {"ok":True,"results":[{"id":a.get("id"),"title":a.get("title"),**article_checks(a)} for a in arts]}

def make_export_zip(current):
    issue_id=current["id"]
    export_root=GENERATED/"_exports"/issue_id
    if export_root.exists(): shutil.rmtree(export_root)
    media_dir=export_root/"media";media_dir.mkdir(parents=True,exist_ok=True)
    doc=fitz.open(BASE/current["pdf"]);public_articles=[]
    for ai,a in enumerate(current["articles"],1):
        article={"title":a.get("title",""),"slug":slugify(a.get("title","")),"type":a.get("type","article"),"text":a.get("text",""),"category":a.get("category","ostatni"),"categoryLabel":a.get("categoryLabel","Ostatní"),"media":[],"content":a.get("content",[])}
        sources=[]
        for img_id in a.get("images",[]):
            for page_data in current["pages"]:
                im=next((x for x in page_data.get("images",[]) if x["id"]==img_id),None)
                if im:
                    meta=(a.get("mediaMeta") or {}).get(img_id,{})
                    sources.append({"id":img_id,"page":page_data["page"],"bbox":im["bbox"],"caption":meta.get("caption","")})
                    break
        sources+=a.get("regions",[])
        for ji,src in enumerate(sources,1):
            try:
                page=doc[int(src["page"])-1];clip=fitz.Rect(*src["bbox"])&page.rect
                if clip.is_empty:continue
                pix=page.get_pixmap(matrix=fitz.Matrix(240/72,240/72),clip=clip,alpha=False)
                name=f"{ai:02d}-{slugify(a.get('title',''))}-{ji:02d}.jpg";pix.save(media_dir/name,jpg_quality=94)
                article["media"].append({"id":src.get("id",f"region-{ji}"),"src":"media/"+name,"caption":src.get("caption","")})
            except Exception:continue
        if not article["content"]:
            article["content"]=[{"type":"paragraph","text":p.strip()} for p in re.split(r"\n\s*\n|\n",article["text"]) if p.strip()]
            article["content"] += [{"type":"image","mediaId":m["id"]} for m in article["media"]]
        public_articles.append(article)
    pdf_name=f"skutecske-noviny-{issue_id}.pdf";shutil.copy2(BASE/current["pdf"],export_root/pdf_name)
    manifest={"format":"skutec-diginoviny-package-v2","id":current["id"],"month":current["month"],"year":current["year"],"pdf":pdf_name,"articles":public_articles}
    (export_root/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    zp=GENERATED/"_exports"/f"skutecske-noviny-{issue_id}.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(export_root/"manifest.json","manifest.json");z.write(export_root/pdf_name,pdf_name)
        for f in media_dir.glob("*"):z.write(f,"media/"+f.name)
    return zp


def ftp_connect(cfg: dict, mode: str):
    host=cfg["host"]; user=cfg["user"]; password=cfg["password"]
    port=int(cfg.get("port",21)); timeout=int(cfg.get("timeout",90))
    ftp=ftplib.FTP_TLS(timeout=timeout) if mode=="tls" else ftplib.FTP(timeout=timeout)
    ftp.connect(host,port)
    ftp.login(user,password)
    ftp.set_pasv(bool(cfg.get("passive",True)))
    if mode=="tls":
        ftp.prot_p()
    return ftp

def ftp_cwd_mkdirs(ftp, remote: str):
    # Start from FTP login root. The configured path is therefore relative to that root.
    try: ftp.cwd("/")
    except Exception: pass
    for part in [x for x in remote.replace("\\","/").split("/") if x]:
        try: ftp.cwd(part)
        except ftplib.error_perm:
            ftp.mkd(part); ftp.cwd(part)

def upload_package_with_retry(zp: Path, cfg: dict):
    remote=cfg.get("remote_import_dir","diginoviny/import")
    attempts=int(cfg.get("retries",2))
    # FileZilla setting "Use explicit FTP over TLS if available" is opportunistic:
    # try explicit FTPS first, then automatically fall back to plain FTP.
    configured=cfg.get("mode","auto")
    modes=["tls","plain"] if configured=="auto" else [configured]
    errors=[]
    for mode in modes:
        for attempt in range(1,attempts+1):
            ftp=None
            tmp_name=zp.name+".uploading"
            try:
                ftp=ftp_connect(cfg,mode)
                ftp_cwd_mkdirs(ftp,remote)
                with zp.open("rb") as fh:
                    ftp.storbinary("STOR "+tmp_name,fh,blocksize=8192)
                try: ftp.delete(zp.name)
                except Exception: pass
                ftp.rename(tmp_name,zp.name)
                try: ftp.quit()
                except Exception: ftp.close()
                return {"ok":True,"attempt":attempt,"mode":mode}
            except Exception as exc:
                errors.append(f"{mode} pokus {attempt}: {type(exc).__name__}: {exc}")
                if ftp is not None:
                    try: ftp.close()
                    except Exception: pass
                if attempt<attempts: time.sleep(2*attempt)
    return {"ok":False,"error":" | ".join(errors)}

@app.post("/admin/api/issues/{issue_id}/queue")
async def queue_publish(issue_id:str, request:Request):
    current=load_issue(issue_id)
    payload=await request.json()
    current["articles"]=payload.get("articles",current.get("articles",[]))
    checks=[{"title":a.get("title"),**article_checks(a)} for a in current["articles"]]
    errors=[x for x in checks if x["errors"]]
    warnings=[x for x in checks if x["warnings"]]
    pending=[a for a in current["articles"] if not a.get("approved")]
    if pending:
        return JSONResponse({"ok":False,"error":f"{len(pending)} položek není schváleno."},status_code=400)
    if errors:
        return JSONResponse({"ok":False,"error":"Kontrola našla blokující chyby.","errors":errors},status_code=400)
    if warnings and not payload.get("ignore_warnings"):
        return JSONResponse({"ok":False,"warning_only":True,"error":"Vydání obsahuje upozornění.","warnings":warnings},status_code=409)
    save_issue(current)
    zp=make_export_zip(current)
    settings_file=BASE/"publish-settings.json"
    if not settings_file.exists():
        return JSONResponse({"ok":False,"error":"Chybí publish-settings.json. Vytvoř ho podle publish-settings.example.json."},status_code=400)
    cfg=json.loads(settings_file.read_text(encoding="utf-8"))
    publish_url=cfg.get("publish_url","https://mesto.skutec.cz/diginoviny/api/publish.php")
    token=cfg.get("publish_token","")
    if not token:
        return JSONResponse({"ok":False,"error":"V publish-settings.json chybí publish_token."},status_code=400)
    try:
        with zp.open("rb") as fh:
            response=requests.post(
                publish_url,
                headers={"X-Publish-Token":token},
                files={"package":(zp.name,fh,"application/zip")},
                timeout=(20,300),
                verify=bool(cfg.get("verify_ssl", False))
            )
        try:
            data=response.json()
        except Exception:
            data={"error":response.text[:1000] or f"HTTP {response.status_code}"}
        if response.status_code>=400 or not data.get("ok"):
            return JSONResponse({"ok":False,"error":"Web publikaci odmítl: "+str(data.get("error","Neznámá chyba")),"local_zip":str(zp)},status_code=502)
        return {"ok":True,"message":data.get("message","Vydání bylo publikováno."),"url":data.get("url"),"issue":data.get("issue")}
    except requests.RequestException as exc:
        return JSONResponse({"ok":False,"error":"HTTPS publikace selhala. ZIP zůstal lokálně. "+str(exc),"local_zip":str(zp)},status_code=502)

@app.post("/admin/api/issues/{issue_id}/export")
async def export_issue(issue_id:str, request:Request):
    current=load_issue(issue_id);payload=await request.json();current["articles"]=payload.get("articles",current.get("articles",[]))
    pending=[a for a in current["articles"] if not a.get("approved")]
    if pending:return JSONResponse({"ok":False,"error":f"{len(pending)} položek není schváleno."},status_code=400)
    save_issue(current);zp=make_export_zip(current)
    return FileResponse(zp,media_type="application/zip",filename=zp.name)

@app.get("/{year:int}/{month:int}/", response_class=HTMLResponse)
def issue_public(request:Request, year:int, month:int):
    issue=load_issue(f"{year}-{month:02d}")
    if not issue.get("published"): raise HTTPException(404)
    return templates.TemplateResponse(request, "issue.html", {"issue": issue})

@app.get("/{year:int}/{month:int}/{slug}/", response_class=HTMLResponse)
def article_public(request:Request, year:int, month:int, slug:str):
    issue=load_issue(f"{year}-{month:02d}")
    if not issue.get("published"): raise HTTPException(404)
    article=next((a for a in issue["articles"] if slugify(a.get("title",""))==slug),None)
    if not article: raise HTTPException(404)
    return templates.TemplateResponse(request, "article.html", {"issue": issue, "article": article})

@app.get("/api/health")
def health(): return {"ok":True}
