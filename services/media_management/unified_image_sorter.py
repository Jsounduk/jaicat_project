# services/media_management/unified_image_sorter.py
# Unified Smart Image Sorter – robust human/pose gating + folder memory
import os
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")

import sys, json, shutil
from pathlib import Path
from types import SimpleNamespace
from collections import Counter, defaultdict


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from PIL import Image, ImageTk, ImageStat
import numpy as np
import cv2
import face_recognition

# --- local modules ---
from tag_ai import generate_tags
from tag_sorter_engine import TagSorter, log_to_machine_learning
from tag_learning_helper import (
    add_image_to_tag_cluster,
    resolve_destination_from_tags as _base_resolve_destination_from_tags,
    get_tag_confidence_label,
)
from region_clip_embedder import update_embeddings_for_image, ensure_region_embeddings
from region_similarity_search import find_similar_for_image, show_region_matches
from feedback_logger import log_feedback
from people_bodypart_tagger import tag_bodyparts_with_identity
from yolo11_adapter import YOLO11Adapter
from log_utils import ensure_log_dir, jsonl_append
from app import context as app_context

# --- PATH BOOTSTRAP ---
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[2]  # .../jaicat_project
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.safety.nsfw_scanner import NSFWScanner
nsfw = NSFWScanner(enable_nudenet=True, nudenet_weight=0.65)

# ========= CONFIG =========
SOURCE_FOLDER  = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\Pictures\SORT"
PICTURES_ROOT  = r"C:\Users\josh_\OneDrive\Pictures\Samsung Gallery\Pictures\SORT"
UNSORTED_ROOT  = os.path.join(PICTURES_ROOT, "uncategorized")
FACES_PATH     = "services/media_management/faces"
LOG_DIR        = "services/media_management/datasets/logs"
FOLDER_MEMORY_PATH = "services/media_management/folder_memory.json"  # new

RECURSIVE = True
USE_YOLO11 = True
YOLO11_CFG = {
    "detect_weights": "yolo11n.pt",
    "pose_weights":   "yolo11n-pose.pt",
    "seg_weights":    "yolo11n-seg.pt",
    "device":         None,  # "cuda:0" if available
    "imgsz":          640,
    "log_dir":        LOG_DIR,
}

IMAGE_EXTS = (
    ".jpg",".jpeg",".png",".webp",".bmp",".tiff",".gif",
    ".heic",".heif",
    ".mp4",".mov"
)

STOPWORDS = {"a","in","and","the","of","on","for","at","with","is","to","as","by","an","are","it","","or","this"}
BAD_TAGS  = {"linger"}

# Globals
_y11 = None
known_encodings = []
known_names     = []
_nsfw_disabled  = False
_hog = None         # HOG people fallback
_folder_memory = {} # learned tag→folder votes

# ========= Folder memory =========
def _load_folder_memory():
    global _folder_memory
    try:
        with open(FOLDER_MEMORY_PATH, "r", encoding="utf-8") as f:
            _folder_memory = json.load(f)
    except Exception:
        _folder_memory = {}

def _save_folder_memory():
    try:
        os.makedirs(os.path.dirname(FOLDER_MEMORY_PATH), exist_ok=True)
        with open(FOLDER_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(_folder_memory, f, indent=2)
    except Exception as e:
        print("⚠️ Folder memory save failed:", e)

def _tags_key(tags:list[str])->str:
    return "|".join(sorted(set(t.lower() for t in tags)))

def remember_folder_for_tags(tags:list[str], folder:str):
    key = _tags_key(tags)
    bucket = _folder_memory.get(key, {})
    bucket[folder] = bucket.get(folder, 0) + 1
    _folder_memory[key] = bucket
    _save_folder_memory()

def suggest_folder_from_memory(tags:list[str], fallback:str)->str:
    key = _tags_key(tags)
    if key not in _folder_memory:
        return fallback
    votes = _folder_memory[key]
    # return highest voted folder
    return sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

def resolve_destination_from_tags(tags:list[str])->str:
    # call your existing resolver, then override with memory if available
    base = _base_resolve_destination_from_tags(tags)
    return suggest_folder_from_memory(tags, base)

# ========= UTIL / HEURISTICS =========
def clean_tags(raw_tags):
    tags = [t.strip(",. ").lower() for t in raw_tags if t and t.strip()]
    tags = [("lingerie" if t=="linger" else t) for t in tags if t not in STOPWORDS and t not in BAD_TAGS and len(t)>1]
    # de-dup order preserving
    seen = set(); out=[]
    for t in tags:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

def load_known_faces(faces_path):
    encs, names = [], []
    if not os.path.isdir(faces_path):
        print(f"⚠️ faces folder missing: {faces_path}")
        return encs, names
    for fname in os.listdir(faces_path):
        if not fname.lower().endswith(".npy"): 
            continue
        path = os.path.join(faces_path, fname)
        try:
            arr = np.load(path)
            if arr.shape == (128,):
                encs.append(arr)
                names.append(fname.rsplit("_",1)[0].replace("_"," ").replace("-"," "))
            else:
                print(f"⚠️ Skipping corrupt or empty file: {fname}")
        except Exception as e:
            print(f"⚠️ Could not load {fname}: {e}")
    print(f"✅ Loaded {len(encs)} face encodings for {len(set(names))} people.")
    return encs, names

def get_all_tags():
    tag_set = set()
    for p in ("services/media_management/tag_learning_log.json",
              "services/media_management/tag_clusters.json",
              "services/media_management/region_annotations.json"):
        try:
            data = json.load(open(p, "r", encoding="utf-8"))
            if isinstance(data, list):
                for r in data:
                    for t in (r.get("tags",[]) if "tags" in r else [r.get("label") or r.get("tag")]):
                        if t: tag_set.add(t)
            elif isinstance(data, dict):
                tag_set.update(data.keys())
        except Exception:
            pass
    tags = sorted(t for t in tag_set if t and t not in STOPWORDS and len(t)>1)
    return tags or ["Rose","Erin","Becky","Lace","Smile"]

def _imread_bgr(path:str)->np.ndarray:
    img = Image.open(path).convert("RGB")
    return np.array(img)[:,:,::-1].copy()

def _bbox_pose_fallback(box):
    x1,y1,x2,y2 = box
    w = max(1,int(x2-x1)); h = max(1,int(y2-y1))
    if w > h*1.25: return "pose:laying"
    if h > w*1.20: return "pose:standing"
    return "pose:kneeling_or_crouched"

def _pose_from_keypoints(kps):
    try:
        pts = kps[0]["keypoints"] if isinstance(kps[0],dict) else kps[0]
        def get(i):
            if i < len(pts): 
                p = pts[i]
                return p if len(p)>=2 else None
            return None
        Lsh,Rsh = get(5), get(6)
        Lhip,Rhip= get(11),get(12)
        Lank,Rank= get(15),get(16)
        if not (Lsh and Rsh and (Lhip or Rhip)):
            return "pose:detected"
        sh_y = (Lsh[1]+Rsh[1])/2
        hip_y= ( (Lhip[1] if Lhip else Rhip[1]) + (Rhip[1] if Rhip else Lhip[1]) )/2
        torso = abs(sh_y-hip_y)
        ank_y = None
        if Lank and Rank: ank_y = (Lank[1]+Rank[1])/2
        elif Lank: ank_y = Lank[1]
        elif Rank: ank_y = Rank[1]
        if ank_y is not None and (ank_y - hip_y) > torso*1.2:  return "pose:standing"
        if ank_y is not None and (hip_y - ank_y) > torso*0.25: return "pose:sitting"
        if (hip_y - sh_y) > torso*0.5:                        return "pose:bent_over"
        if abs(sh_y-hip_y) < max(8, torso*0.25):              return "pose:laying"
        return "pose:detected"
    except Exception:
        return "pose:detected"

def _skin_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower1 = np.array([0,  15,  40], np.uint8)
    upper1 = np.array([20, 180, 255], np.uint8)
    lower2 = np.array([160,15,  40], np.uint8)
    upper2 = np.array([179,180,255], np.uint8)
    mask = cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)
    mask = cv2.medianBlur(mask, 5)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8), iterations=1)
    return mask

def _estimate_skin_ratio(bgr):
    mask = _skin_mask(bgr)
    return float(mask.mean()/255.0)

def _tattoo_present(bgr):
    mask = _skin_mask(bgr)
    edges = cv2.Canny(cv2.GaussianBlur(bgr,(3,3),0), 70, 150)
    ink = cv2.bitwise_and(edges, edges, mask=mask)
    skin_px = max(1, int(mask.sum()/255))
    ink_density = float(ink.sum()) / (255.0 * skin_px)
    return ink_density > 0.022

# --- Bed heuristic: bright sheet + parallel rails ---
def _likely_bed(bgr):
    try:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        # brightness/whiteness
        white_ratio = (rgb[...,0] > 200) & (rgb[...,1] > 200) & (rgb[...,2] > 200)
        white_ratio = float(white_ratio.mean())
        # rails (parallel lines)
        edges = cv2.Canny(gray, 80, 160)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=60, minLineLength=120, maxLineGap=20)
        horizontals = 0
        if lines is not None:
            for l in lines:
                x1,y1,x2,y2 = l[0]
                if abs(y2-y1) < 8 and abs(x2-x1) > 80:
                    horizontals += 1
        return (white_ratio > 0.25 and horizontals >= 2)
    except Exception:
        return False

def _safe_nsfw_scan(*, caption_tags, body_parts, faces_adult_probs, image_path):
    global _nsfw_disabled
    if _nsfw_disabled:
        return SimpleNamespace(label=None, score=0.0, reasons=["disabled"], tags=[])
    try:
        out = nsfw.scan(
            caption_tags=caption_tags,
            body_parts=body_parts or [],
            faces_adult_probs=faces_adult_probs,
            image_path=image_path
        )
        if out is None:
            return SimpleNamespace(label=None, score=0.0, reasons=[], tags=[])
        if isinstance(out, dict):
            return SimpleNamespace(
                label=out.get("label"),
                score=float(out.get("score",0.0)),
                reasons=out.get("reasons",[]),
                tags=out.get("tags",[]),
            )
        if hasattr(out,"label"):
            return out
        return SimpleNamespace(label=None, score=0.0, reasons=[], tags=[])
    except Exception as e:
        print("⚠️ NSFW scan disabled (error):", e)
        _nsfw_disabled = True
        return SimpleNamespace(label=None, score=0.0, reasons=["error"], tags=[])

def _list_media_files(root:str, recursive:bool):
    files = []
    if not recursive:
        try:
            for n in os.listdir(root):
                if n.lower().endswith(IMAGE_EXTS):
                    files.append(os.path.join(root,n))
        except FileNotFoundError:
            return []
    else:
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if not d.startswith(".") and d.lower() not in {"thumbs.db","__macosx"}]
            for n in fn:
                if n.lower().endswith(IMAGE_EXTS):
                    files.append(os.path.join(dp,n))
    return sorted(files, key=lambda p:(os.path.dirname(p).lower(), os.path.basename(p).lower()))

# ========= REGION TAGGER UI =========
class RegionTaggerPanel(tk.Frame):
    def __init__(self, parent, image_path, tag_suggestions=None, on_done=None, y11: YOLO11Adapter|None=None):
        super().__init__(parent, bg="white")
        self.image_path = image_path
        self._orig_img = Image.open(image_path)
        self.tk_image = None
        self.tag_suggestions = tag_suggestions or get_all_tags()
        self.boxes = []
        self.current_box = None
        self.start_x = None
        self.start_y = None
        self.on_done = on_done
        self._y11 = y11

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=10)
        self.draw_image()
        self.canvas.bind("<Configure>", self.redraw_image)
        self.canvas.bind("<ButtonPress-1>", self.on_start_box)
        self.canvas.bind("<B1-Motion>", self.on_draw_box)
        self.canvas.bind("<ButtonRelease-1>", self.on_finish_box)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="✅ Save & Return", command=self.save_and_return, bg="#4CAF50", fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="⏭️ Cancel", command=self.cancel).pack(side="left", padx=10)

    def draw_image(self):
        if not self._orig_img: return
        w = self.canvas.winfo_width(); h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            self.after(50, self.draw_image); return
        img = self._orig_img.copy()
        if hasattr(Image,"Resampling"):
            img.thumbnail((w,h), Image.Resampling.LANCZOS)
        else:
            img.thumbnail((w,h), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(w//2, h//2, anchor="center", image=self.tk_image)
        for box in self.boxes:
            x0,y0,x1,y1 = box["coords"]
            self.canvas.create_rectangle(x0,y0,x1,y1, outline="red", width=2)

    def redraw_image(self, event=None): self.draw_image()

    def on_start_box(self, e):
        self.start_x,self.start_y = e.x,e.y
        self.current_box = self.canvas.create_rectangle(self.start_x,self.start_y,e.x,e.y, outline="red", width=2)

    def on_draw_box(self, e):
        if self.current_box: self.canvas.coords(self.current_box, self.start_x,self.start_y,e.x,e.y)

    def on_finish_box(self, e):
        x0,y0,x1,y1 = [int(v) for v in self.canvas.coords(self.current_box)]
        self.prompt_tag_for_box(self.current_box, x0,y0,x1,y1)

    def _crop_to_bgr(self,x0,y0,x1,y1):
        img = self._orig_img.copy().convert("RGB")
        crop = img.crop((max(0,x0),max(0,y0),max(1,x1),max(1,y1)))
        return np.array(crop)[:,:,::-1].copy()

    def prompt_tag_for_box(self, box_id, x0,y0,x1,y1):
        clothing_tags=[]; pose_keypoints=[]
        try:
            if self._y11:
                region_bgr = self._crop_to_bgr(x0,y0,x1,y1)
                segs = self._y11.segment(region_bgr, conf=0.25) or []
                clothing_tags = [s.get("label") for s in segs if s.get("label")]
                kps = self._y11.pose(region_bgr, conf=0.25) or []
                if kps: pose_keypoints = [_pose_from_keypoints(kps)]
        except Exception as e:
            print(f"Region detection failed: {e}")

        all_suggestions = list(dict.fromkeys([t for t in (clothing_tags + pose_keypoints + self.tag_suggestions) if t and len(t)>1]))

        popup = tk.Toplevel(self); popup.title("Assign Tag")
        var = tk.StringVar()
        cb = ttk.Combobox(popup, textvariable=var, values=all_suggestions, width=32)
        cb.pack(padx=10, pady=10)
        if all_suggestions: cb.set(all_suggestions[0])

        def save_tag():
            tag = var.get()
            region = {"box_id":box_id, "coords":(x0,y0,x1,y1), "tag":tag}
            self.boxes.append(region)
            add_image_to_tag_cluster(tag, self.image_path)
            try:
                det_path = ensure_log_dir(LOG_DIR) / "detections.jsonl"
                jsonl_append(det_path, {
                    "task":"detect","source":"user_confirmed","model":"human",
                    "image": self.image_path, "boxes_xyxy":[[x0,y0,x1,y1]],
                    "classes":[None], "confs":[1.0], "labels":[tag]
                })
            except Exception as e:
                print("⚠️ Failed to log region confirmation:", e)
            popup.destroy()
            if tag not in self.tag_suggestions:
                log_feedback(self.image_path, self.tag_suggestions, [tag], correction_type="region")
        tk.Button(popup, text="OK", command=save_tag).pack(pady=5)

    def save_and_return(self):
        print(f"✅ Regions tagged for {self.image_path}")
        update_embeddings_for_image(self.image_path)
        try:
            if self.boxes:
                det_path = ensure_log_dir(LOG_DIR) / "detections.jsonl"
                boxes  = [list(r["coords"]) for r in self.boxes]
                labels = [r.get("tag") for r in self.boxes]
                jsonl_append(det_path, {
                    "task":"detect","source":"user_confirmed","model":"human",
                    "image": self.image_path, "boxes_xyxy":boxes,
                    "classes":[None]*len(boxes), "confs":[1.0]*len(boxes), "labels":labels
                })
        except Exception as e:
            print("⚠️ Failed to log region batch:", e)
        if self.on_done: self.on_done(self.boxes)
        self.destroy()

    def cancel(self):
        print(f"⏭️ Region tagging cancelled: {self.image_path}")
        self.destroy()

# ========= UNIFIED TAGGER WINDOW =========
class UnifiedTaggerUI:
    def __init__(self, image_path, auto_tags, available_tags, resolve_destination_from_tags, y11:YOLO11Adapter|None=None, *, sorter:TagSorter|None=None, auto_retrain_default:bool=True):
        self.image_path = image_path
        self.auto_tags  = auto_tags
        self.available_tags = get_all_tags()
        self.resolve_destination_from_tags = resolve_destination_from_tags
        self._y11 = y11
        self._sorter = sorter

        self.root = tk.Tk()
        self.root.title("Jaicat – Unified Smart Image Sorter")
        self.root.geometry("950x920")
        self.root.resizable(True, True)
        self.root.configure(bg="#f9f9fb")

        self.main_frame = tk.Frame(self.root, bg="#f9f9fb")
        self.main_frame.pack(fill="both", expand=True, padx=18, pady=6)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self.main_frame, textvariable=self.status_var, anchor="w").pack(fill="x", side="bottom")

        if self._sorter:
            self._sorter.on_status = self._threadsafe_status
            self._sorter.on_toast  = self._threadsafe_toast
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.img_canvas = tk.Canvas(self.main_frame, bg="#f9f9fb", highlightthickness=0)
        self.img_canvas.pack(fill="both", expand=True, pady=10)
        self.tk_img=None; self._orig_img=None
        self.load_image()
        self.img_canvas.bind("<Configure>", self.redraw_image)

        # Tag input row
        tag_frame = tk.Frame(self.main_frame, bg="#f9f9fb"); tag_frame.pack(pady=6)
        self.tags_entry = tk.Entry(tag_frame, width=62, font=("Segoe UI",12))
        self.tags_entry.pack(side="left", padx=5)
        self.tags_entry.insert(0, ", ".join(self.auto_tags))
        self.tags_entry.bind("<KeyRelease>", lambda e: self.update_destination_label())
        self.tag_dropdown = ttk.Combobox(tag_frame, values=self.available_tags, width=23); self.tag_dropdown.pack(side="left", padx=5)
        self.tag_dropdown.bind("<Return>", self.add_suggested_tag)
        tk.Button(tag_frame, text="+", command=self.add_suggested_tag, width=2).pack(side="left")

        # Suggestions row
        suggestion_frame = tk.Frame(self.main_frame, bg="#f9f9fb"); suggestion_frame.pack(pady=3)
        for tag in self.auto_tags[:10]:
            tk.Button(suggestion_frame, text=f"{tag} {get_tag_confidence_label(tag)}",
                      command=lambda t=tag: self.add_tag(t),
                      width=14, relief="flat", bg="#e6eaff").pack(side="left", padx=2)

        # Destination chooser
        folder_choose_frame = tk.Frame(self.main_frame, bg="#f9f9fb"); folder_choose_frame.pack(pady=8)
        self.chosen_folder = tk.StringVar(value="")
        tk.Button(folder_choose_frame, text="Choose Destination Folder...", command=self.pick_folder, width=28, bg="#e6eaff").pack(side="left")
        self.chosen_folder_label = tk.Label(folder_choose_frame, text="", bg="#f9f9fb", fg="#3651a5", font=("Segoe UI",9))
        self.chosen_folder_label.pack(side="left", padx=6)

        # Subfolder row
        sub_frame = tk.Frame(self.main_frame, bg="#f9f9fb"); sub_frame.pack(pady=6)
        tk.Label(sub_frame, text="Subfolder:", bg="#f9f9fb").pack(side="left")
        self.sub_entry = tk.Entry(sub_frame, width=32, font=("Segoe UI",11)); self.sub_entry.pack(side="left", padx=5)
        self.sub_entry.insert(0, ""); self.sub_entry.bind("<KeyRelease>", lambda e: self.update_destination_label())

        # Retrain controls
        retrain_frame = tk.Frame(self.main_frame, bg="#f9f9fb"); retrain_frame.pack(pady=4)
        self.auto_retrain_var = tk.BooleanVar(value=auto_retrain_default)
        ttk.Checkbutton(retrain_frame, text="Auto retrain after move", variable=self.auto_retrain_var).pack(side="left")
        ttk.Button(retrain_frame, text="Retrain Now", command=self._on_retrain_now).pack(side="left", padx=(10,0))

        # Destination label
        self.dest_label = tk.Label(self.main_frame, text="", fg="#3651a5", bg="#f9f9fb", font=("Segoe UI",11,"bold"), wraplength=760)
        self.dest_label.pack(pady=8); self.update_destination_label()

        # Action buttons
        btn = tk.Frame(self.main_frame, bg="#f9f9fb"); btn.pack(pady=14)
        tk.Button(btn, text="✅ Save & Next",   command=self.confirm,            width=14, bg="#baffba", font=("Segoe UI",10,"bold")).pack(side="left", padx=8)
        tk.Button(btn, text="🟦 Tag Region",    command=self.launch_region_tagger, width=14, bg="#c0e6ff", font=("Segoe UI",10,"bold")).pack(side="left", padx=8)
        tk.Button(btn, text="🟩 Find Similar Region", command=self.find_similar_region, width=17, bg="#e6ffc0", font=("Segoe UI",10,"bold")).pack(side="left", padx=8)
        tk.Button(btn, text="🗑️ Delete",       command=self.delete_image,       width=12, font=("Segoe UI",10,"bold")).pack(side="left", padx=8)
        tk.Button(btn, text="🔁 Uncategorized", command=self.mark_uncategorized, width=15, font=("Segoe UI",10,"bold")).pack(side="left", padx=8)
        tk.Button(btn, text="❌ Cancel",        command=self.cancel,             width=10, font=("Segoe UI",10,"bold")).pack(side="left", padx=8)

        self.result=None; self.region_panel=None
        self.root.mainloop()

    # thread-safe status/toast
    def _threadsafe_status(self,t): 
        try: self.root.after(0, self._set_status, t)
        except tk.TclError: pass
    def _threadsafe_toast(self,t):
        try: self.root.after(0, self._toast, t)
        except tk.TclError: pass
    def _set_status(self,t): self.status_var.set(t)
    def _toast(self,t): self.status_var.set(t); self.root.after(3000, lambda: self.status_var.set("Ready."))
    def _detach_sorter_callbacks(self):
        if self._sorter: self._sorter.on_status=None; self._sorter.on_toast=None
    def _on_close(self):
        self.result=None; self._detach_sorter_callbacks(); self.root.destroy()

    def _on_retrain_now(self):
        if self._sorter: self._sorter.request_retrain(reason="manual")
        else: self._toast("No sorter attached.")

    def load_image(self):
        try: self._orig_img = Image.open(self.image_path)
        except Exception as e:
            self._orig_img=None
            self.img_canvas.delete("all")
            self.img_canvas.create_text(self.img_canvas.winfo_width()//2, self.img_canvas.winfo_height()//2,
                                        text=f"⚠️ Failed to load image\n{e}", fill="red", font=("Segoe UI",14))
    def redraw_image(self, event=None):
        if not self._orig_img: return
        W = self.img_canvas.winfo_width(); H = self.img_canvas.winfo_height()
        img = self._orig_img.copy()
        if hasattr(Image,"Resampling"): img.thumbnail((W,H), Image.Resampling.LANCZOS)
        else: img.thumbnail((W,H), Image.ANTIALIAS)
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_canvas.delete("all")
        self.img_canvas.create_image(W//2, H//2, anchor="center", image=self.tk_img)

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.chosen_folder.set(folder); self.chosen_folder_label.config(text=folder)
        else:
            self.chosen_folder.set(""); self.chosen_folder_label.config(text="")
        self.update_destination_label()

    def add_tag(self,tag):
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        if tag not in tags:
            tags.append(tag)
            self.tags_entry.delete(0,tk.END); self.tags_entry.insert(0,", ".join(tags))
            self.update_destination_label()

    def add_suggested_tag(self,_=None):
        tag = self.tag_dropdown.get().strip()
        if tag: self.add_tag(tag); self.tag_dropdown.set("")

    def update_destination_label(self):
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        sub = self.sub_entry.get().strip()
        if hasattr(self,"chosen_folder") and self.chosen_folder.get():
            base = self.chosen_folder.get()
        else:
            base = resolve_destination_from_tags(tags)
        full = os.path.join(base, sub) if sub else base
        self.dest_label.config(text=f"Destination: {full}")

    def confirm(self):
        tags = [t.strip() for t in self.tags_entry.get().split(",") if t.strip()]
        sub  = self.sub_entry.get().strip()
        folder = self.chosen_folder.get() if hasattr(self,"chosen_folder") and self.chosen_folder.get() else None
        if set(tags) != set(self.auto_tags):
            log_feedback(self.image_path, self.auto_tags, tags, correction_type="image")
        self.result = {"tags":tags, "subfolder":sub, "folder":folder, "auto_retrain": bool(getattr(self,"auto_retrain_var",tk.BooleanVar(value=True)).get())}
        self._detach_sorter_callbacks(); self.root.destroy()

    def delete_image(self):
        if messagebox.askyesno("Confirm Delete","Really delete this image?"):
            self.result="DELETE_FILE"; self._detach_sorter_callbacks(); self.root.destroy()

    def mark_uncategorized(self):
        self.result="SORT_UNCATEGORIZED"; self._detach_sorter_callbacks(); self.root.destroy()

    def cancel(self):
        self.result=None; self._detach_sorter_callbacks(); self.root.destroy()

    def launch_region_tagger(self):
        self.img_canvas.pack_forget()
        self.region_panel = RegionTaggerPanel(self.main_frame, self.image_path,
                                              tag_suggestions=self.available_tags,
                                              on_done=self.region_tagger_done,
                                              y11=_y11 if USE_YOLO11 else None)
        self.region_panel.pack(fill="both", expand=True, pady=10)

    def region_tagger_done(self, regions):
        update_embeddings_for_image(self.image_path)
        self.region_panel.pack_forget()
        self.img_canvas.pack(fill="both", expand=True, pady=10)
        self.redraw_image()
        messagebox.showinfo("Region Saved","Region(s) added & embeddings updated for this image!")

    def find_similar_region(self):
        ensure_region_embeddings()
        idx = simpledialog.askinteger("Region Index","Enter region # (0 for first region in this image):", minvalue=0)
        if idx is not None:
            similar = find_similar_for_image(self.image_path, idx, top_n=5)
            show_region_matches(self.image_path, idx, similar)

# ========= MAIN PIPE =========
def _ensure_hog():
    global _hog
    if _hog is None:
        _hog = cv2.HOGDescriptor()
        _hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def _hog_person_boxes(bgr):
    try:
        _ensure_hog()
        rects, _ = _hog.detectMultiScale(bgr, winStride=(8,8), padding=(8,8), scale=1.05)
        boxes=[]
        for (x,y,w,h) in rects:
            boxes.append([x,y,x+w,y+h])
        return boxes
    except Exception:
        return []

def process_image(image_path, *, sorter:TagSorter|None):
    global known_encodings, known_names
    app_context.current_image_path = image_path

    if image_path.lower().endswith((".mp4",".mov")):
        print(f"⏭️ Skipping video for now: {image_path}")
        return

    # Face identity + quick "person" inference from face present
    person=None
    face_present=False
    try:
        image = face_recognition.load_image_file(image_path)
        encs  = face_recognition.face_encodings(image)
        if encs:
            face_present=True
        for e in encs:
            res = face_recognition.compare_faces(known_encodings, e, tolerance=0.5)
            if True in res:
                person = known_names[res.index(True)]
                break
    except Exception:
        pass

    auto_tags = clean_tags(generate_tags(image_path))

    fashion_tags=[]; pose_tags=[]; body_tags=[]
    yolo_person_boxes=[]

    # YOLO branch
    try:
        if USE_YOLO11 and _y11 is not None:
            bgr = _imread_bgr(image_path)

            # detect persons for bbox fallback
            dets = _y11.detect(bgr, conf=0.30) or []
            for d in dets:
                label = (d.get("label") or "").lower()
                if label == "person" and "xyxy" in d:
                    yolo_person_boxes.append(d["xyxy"])

            # segmentation → clothing-ish labels (if provided)
            segs = _y11.segment(bgr, conf=0.30) or []
            fashion_tags = [s.get("label") for s in segs if s.get("label")]

            # Only try pose if we saw any person boxes
            if yolo_person_boxes:
                kps = _y11.pose(bgr, conf=0.25) or []
                if kps:
                    pose_tags = [_pose_from_keypoints(kps)]
                else:
                    # bbox shape fallback
                    big = max(yolo_person_boxes, key=lambda bb: (bb[2]-bb[0])*(bb[3]-bb[1]))
                    pose_tags = [_bbox_pose_fallback(big)]
        # No else: legacy path off
    except Exception as e:
        print(f"YOLO/legacy detection failed: {e}")

    # If YOLO missed, but faces present → add person and HOG to get a bbox for pose
    human_seen = False
    if yolo_person_boxes or face_present or person:
        human_seen = True
        if "person" not in auto_tags:
            auto_tags.append("person")

    # HOG fallback to estimate pose when no YOLO person boxes but a human is likely present
    if human_seen and not yolo_person_boxes:
        try:
            bgr = _imread_bgr(image_path)
            hog_boxes = _hog_person_boxes(bgr)
            if hog_boxes:
                big = max(hog_boxes, key=lambda bb: (bb[2]-bb[0])*(bb[3]-bb[1]))
                pose_tags = [ _bbox_pose_fallback(big) ]
        except Exception:
            pass

    # Bed heuristic (helps your lingerie/bed scene)
    try:
        bgr_full = _imread_bgr(image_path)
        if _likely_bed(bgr_full):
            if "bed" not in auto_tags:
                auto_tags.append("bed")
    except Exception:
        pass

    # NSFW + wardrobe heuristics
    nsfw_result = _safe_nsfw_scan(caption_tags=auto_tags, body_parts=body_tags, faces_adult_probs=None, image_path=image_path)
    if nsfw_result.label in ("SUGGESTIVE","EXPLICIT"):
        nsfw_tag = "NSFW:explicit" if nsfw_result.label=="EXPLICIT" else "NSFW:suggestive"
        if nsfw_tag not in auto_tags: auto_tags.append(nsfw_tag)
    try:
        nsfw_path = ensure_log_dir(LOG_DIR) / "nsfw.jsonl"
        jsonl_append(nsfw_path, {
            "task":"nsfw","image":image_path,"label":nsfw_result.label,
            "score":float(nsfw_result.score),"reasons":nsfw_result.reasons,"tags_added":nsfw_result.tags
        })
    except Exception as e:
        print(f"⚠️ NSFW log failed: {e}")

    # wardrobe guesses from skin coverage
    try:
        bgr_full = _imread_bgr(image_path) if 'bgr_full' not in locals() else bgr_full
        skin_ratio = _estimate_skin_ratio(bgr_full)
        if nsfw_result.label=="EXPLICIT" and skin_ratio>0.60:
            if "nude" not in auto_tags: auto_tags.append("nude")
        elif nsfw_result.label in ("SUGGESTIVE","EXPLICIT") and 0.22 < skin_ratio <= 0.65:
            pref = "lingerie" if any(t for t in fashion_tags if t and t not in {"person"}) else "underwear"
            if pref not in auto_tags: auto_tags.append(pref)
    except Exception:
        pass

    # tattoo detector
    try:
        bgr_full = _imread_bgr(image_path) if 'bgr_full' not in locals() else bgr_full
        if _tattoo_present(bgr_full):
            if "tattoos" not in auto_tags: auto_tags.append("tattoos")
    except Exception:
        pass

    # Identity-aware body-part tags (kept)
    try:
        owner = person
        nsfw_label = getattr(nsfw_result,"label",None)
        id_tags, id_regions = tag_bodyparts_with_identity(image_path=image_path, owner_name=owner, nsfw_label=nsfw_label)

        for t in id_tags:
            if t and t not in auto_tags: auto_tags.append(t)

        # friendly synonyms
        synonym_map = {
            "breasts": ["breasts","boobs"],
            "buttocks": ["ass","bum"],
            "vulva": ["pussy"],
        }
        if id_regions:
            for r in id_regions:
                base = (r.label or "").lower()
                for k, syns in synonym_map.items():
                    if k in base:
                        for s in syns:
                            if s not in auto_tags: auto_tags.append(s)

            # log regions
            det_path = ensure_log_dir(LOG_DIR) / "detections.jsonl"
            boxes = [list(r.box_xyxy) for r in id_regions]
            labels = [f"{r.owner}_{r.label}" if r.owner else r.label for r in id_regions]
            jsonl_append(det_path, {
                "task":"detect","source":"mediapipe_pose","model":"mediapipe_pose_v1",
                "image":image_path,"boxes_xyxy":boxes,"classes":[None]*len(boxes),
                "confs":[float(r.conf) for r in id_regions],"labels":labels
            })
    except Exception as e:
        print(f"⚠️ Identity/body-part tagging failed: {e}")

    # ---- Merge & human-gate for pose ----
    # Only add pose tags if we actually saw a human
    for tag in (fashion_tags or []):
        if tag and tag not in auto_tags: auto_tags.append(tag)
    if human_seen:
        for tag in (pose_tags or []):
            if tag and tag not in auto_tags: auto_tags.append(tag)
    else:
        # ensure no pose:* lands on drawings etc.
        auto_tags = [t for t in auto_tags if not t.startswith("pose:")]

    if person and person not in auto_tags:
        auto_tags.insert(0, person)

    # modelling helper
    if human_seen and any(p.startswith("pose:") for p in auto_tags) and any(t in auto_tags for t in ("lingerie","underwear","nude")):
        if "modelling" not in auto_tags: auto_tags.append("modelling")

    # === UI ===
    ui = UnifiedTaggerUI(
        image_path, auto_tags, get_all_tags(), resolve_destination_from_tags,
        y11=_y11 if USE_YOLO11 else None, sorter=sorter, auto_retrain_default=True
    )
    result = ui.result

    # === Post-UI ===
    if isinstance(result, dict):
        tags = result.get("tags",[]) or []
        sub  = result.get("subfolder","") or ""
        folder = result.get("folder") or None
        auto_retrain = bool(result.get("auto_retrain", True))

        if not folder: folder = resolve_destination_from_tags(tags)
        if sub: folder = os.path.join(folder, sub)

        # image-level confirmations
        try:
            with Image.open(image_path) as im: w,h = im.size
            det_path = ensure_log_dir(LOG_DIR) / "detections.jsonl"
            for tag in tags:
                jsonl_append(det_path, {
                    "task":"detect","source":"user_confirmed","model":"human",
                    "image":image_path,"boxes_xyxy":[[0,0,w,h]],
                    "classes":[None],"confs":[1.0],"labels":[tag]
                })
        except Exception as e:
            print("⚠️ Failed to log image-level tags:", e)

        # learn chosen folder for these tags
        remember_folder_for_tags(tags, folder)

        log_to_machine_learning(image_path, tags, folder)
        for t in tags: add_image_to_tag_cluster(t, image_path)

        os.makedirs(folder, exist_ok=True)
        dest_path = os.path.join(folder, os.path.basename(image_path))
        if os.path.abspath(image_path) != os.path.abspath(dest_path):
            try:
                shutil.move(image_path, dest_path)
                print(f"✅ Moved {image_path} → {dest_path}")
            except Exception as e:
                print(f"❌ Failed to move file: {e}")

        if sorter and auto_retrain: sorter.request_retrain(reason="post-move")

    elif result == "DELETE_FILE":
        try: os.remove(image_path); print(f"🗑️ Deleted {image_path}")
        except Exception as e: print(f"❌ Delete failed: {e}")

    elif result == "SORT_UNCATEGORIZED":
        os.makedirs(UNSORTED_ROOT, exist_ok=True)
        dest_path = os.path.join(UNSORTED_ROOT, os.path.basename(image_path))
        if os.path.abspath(image_path) != os.path.abspath(dest_path):
            try:
                shutil.move(image_path, dest_path)
                print(f"🔁 Marked uncategorized: {image_path} → {dest_path}")
            except Exception as e:
                print(f"❌ Failed to move to uncategorized: {e}")

def run(sorter:TagSorter|None):
    if not os.path.isdir(SOURCE_FOLDER):
        print(f"❌ SOURCE_FOLDER not found: {SOURCE_FOLDER}"); return
    files = _list_media_files(SOURCE_FOLDER, RECURSIVE)
    print(f"📂 Source: {SOURCE_FOLDER}  (recursive={'ON' if RECURSIVE else 'OFF'})")
    print(f"🖼️ Found {len(files)} media files with IMAGE_EXTS={IMAGE_EXTS}")
    if not files:
        print("ℹ️ No matching files. Drop images into this folder."); return
    for fp in files:
        try: process_image(fp, sorter=sorter)
        except Exception as e: print(f"⚠️ Failed on {fp}: {e}")

if __name__ == "__main__":
    _load_folder_memory()
    # HOG is lazy-initialised
    # single-file quick open
    if len(sys.argv)>1 and os.path.isfile(sys.argv[1]):
        known_encodings, known_names = load_known_faces(FACES_PATH)
        try: tag_sorter = TagSorter(); tag_sorter.train_from_log()
        except Exception as e: print(f"⚠️ TagSorter init failed: {e}"); tag_sorter=None
        if USE_YOLO11:
            try: _y11 = YOLO11Adapter(**YOLO11_CFG)
            except Exception as e: print(f"⚠️ YOLO11 disabled (init failed): {e}"); _y11=None
        process_image(sys.argv[1], sorter=tag_sorter); sys.exit(0)

    # normal batch mode
    known_encodings, known_names = load_known_faces(FACES_PATH)
    try: tag_sorter = TagSorter(); tag_sorter.train_from_log()
    except Exception as e: print(f"⚠️ TagSorter init failed: {e}"); tag_sorter=None
    if USE_YOLO11:
        try: _y11 = YOLO11Adapter(**YOLO11_CFG)
        except Exception as e: print(f"⚠️ YOLO11 disabled (init failed): {e}"); _y11=None
    run(tag_sorter)
# --- END ---