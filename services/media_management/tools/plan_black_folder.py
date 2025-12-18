import os, re, sys, csv, json, shutil, hashlib, argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\Pictures\The Black Folder")
PEOPLE = ROOT / "People"
SOURCES = ROOT / "_SOURCES"
INBOX = ROOT / "_INBOX"
SYSTEM = ROOT / "_SYSTEM"
EXTS = {".jpg",".jpeg",".png",".webp",".bmp",".tiff",".gif",".mp4",".mov",".avi",".mkv",".heic",".heif"}

# canonical name fixes
CANON = {
    "scarlletblack": "Scarlet Black",
    "scarletblack":  "Scarlet Black",
    "becky (1)":     "Becky",
    "amy h":         "Amy H",
}

def canon_person(name: str) -> str:
    n = re.sub(r"[_\-]+", " ", name).strip()
    low = n.lower()
    if low in CANON:
        return CANON[low]
    return " ".join(w.capitalize() for w in n.split())

def content_hash(p: Path, chunk=1024*1024) -> str:
    h = hashlib.sha1()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()[:12]

def guess_person_from_path(p: Path) -> str|None:
    # First subfolder under ROOT is treated as a candidate person
    try:
        rel = p.relative_to(ROOT)
        head = rel.parts[0]
        # ignore known system buckets
        if head.startswith("_"):
            return None
        return canon_person(head)
    except Exception:
        return None

def exif_datetime_or_fs(p: Path) -> datetime:
    # keep simple to avoid heavy deps; fs timestamp fallback
    try:
        import PIL.Image
        from PIL.ExifTags import TAGS
        img = PIL.Image.open(p)
        exif = img.getexif()
        if exif:
            for k,v in exif.items():
                if TAGS.get(k) == "DateTimeOriginal":
                    return datetime.strptime(str(v), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    ts = p.stat().st_mtime
    return datetime.fromtimestamp(ts)

def target_for(p: Path) -> Path:
    person = guess_person_from_path(p)
    dt = exif_datetime_or_fs(p)
    ym = dt.strftime("%Y-%m")
    if person:
        return PEOPLE / person[0].upper() / person / ym / p.name
    # unknown → ORPHANS
    return (ROOT / "_ORPHANS" / ym / p.name)

def scan():
    plan = []
    for dirpath, _, files in os.walk(ROOT):
        dpath = Path(dirpath)
        # skip system trees
        if dpath == SYSTEM or dpath.name.startswith("_") and dpath.name not in {"_SOURCES", "_INBOX"}:
            continue
        for f in files:
            p = dpath / f
            if p.suffix.lower() not in EXTS: 
                continue
            # already in canonical place?
            tgt = target_for(p)
            if p.resolve() == tgt.resolve():
                continue
            plan.append((str(p), str(tgt)))
    return plan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    PEOPLE.mkdir(parents=True, exist_ok=True)
    (ROOT/"_ORPHANS").mkdir(exist_ok=True)
    SYSTEM.mkdir(exist_ok=True)
    (SYSTEM/"move_plans").mkdir(parents=True, exist_ok=True)

    plan = scan()
    outcsv = SYSTEM/"move_plans"/"plan.csv"
    with outcsv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source","dest"])
        w.writerows(plan)

    print(f"Planned moves: {len(plan)}")
    print(f"Review CSV: {outcsv}")

    if args.apply:
        for src, dst in plan:
            src_p, dst_p = Path(src), Path(dst)
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            # hash-suffix if dest exists with different content
            if dst_p.exists() and src_p.stat().st_size != dst_p.stat().st_size:
                stem, ext = dst_p.stem, dst_p.suffix
                dst_p = dst_p.with_name(f"{stem}_{content_hash(src_p)}{ext}")
            try:
                shutil.move(str(src_p), str(dst_p))
                print(f"→ {src_p}  >>  {dst_p}")
            except Exception as e:
                print(f"!! move failed {src_p}: {e}")

if __name__ == "__main__":
    main()
