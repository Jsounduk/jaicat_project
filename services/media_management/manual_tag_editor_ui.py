# services/media_management/manual_tag_editor_ui.py

import os
import difflib
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Optional: Pass in FOLDER_INDEX, DISPLAY_NAME_FOR, etc. if needed.

WIN_W, WIN_H = 980, 820
IMG_MAX_W, IMG_MAX_H = 1400, 1400
SUGGESTION_LIMIT = 12
FUZZY_CUTOFF = 0.55

# You will need to inject AVAILABLE_TAGS, resolve_destination_from_tags, and _ensure_local_and_open from the parent

# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────
def manual_tag_editor(image_path, auto_tags, AVAILABLE_TAGS, resolve_destination_from_tags, _ensure_local_and_open):
    root = tk.Tk()
    root.title("Jaicat — Edit Tags")
    root.geometry(f"{WIN_W}x{WIN_H}")
    root.minsize(WIN_W, WIN_H - 40)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=0)

    canvas = tk.Canvas(root, highlightthickness=0)
    vbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    vbar.grid(row=0, column=1, sticky="ns")

    content = tk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=content, anchor="nw")

    def _on_content_config(_evt=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
    content.bind("<Configure>", _on_content_config)

    def _on_canvas_config(evt):
        canvas.itemconfigure(canvas_window, width=evt.width)
    canvas.bind("<Configure>", _on_canvas_config)

    def _on_wheel(evt):
        try:
            canvas.yview_scroll(int(-1 * (evt.delta / 120)), "units")
        except Exception:
            pass
    canvas.bind_all("<MouseWheel>", _on_wheel)

    try:
        img = _ensure_local_and_open(image_path)
        img.thumbnail((IMG_MAX_W, IMG_MAX_H))
    except Exception:
        img = Image.new("RGB", (1024, 768), "grey")
    tk_img = ImageTk.PhotoImage(img)
    img_label = tk.Label(content, image=tk_img)
    img_label.image = tk_img
    img_label.pack(pady=(10, 8))

    tk.Label(content, text=f"Source: {image_path}", wraplength=WIN_W - 120, justify="left").pack(pady=(0, 10))
    tk.Label(content, text="Tags (comma-separated):").pack()

    entry = tk.Entry(content, width=120)
    seen = set()
    seed_list = [t for t in (auto_tags or []) if t]
    seed_list = [t for t in seed_list if not (t.lower() in seen or seen.add(t.lower()))]
    entry.insert(0, ", ".join(seed_list))
    entry.pack(pady=(4, 6), fill="x")

    tk.Label(content, text="Manual Sub-Tag (optional — creates a subfolder):").pack()
    manual_entry = tk.Entry(content, width=120)
    manual_entry.pack(pady=(4, 10), fill="x")

    dest_var = tk.StringVar(value="Destination: (type tags to see prediction)")
    dest_label = tk.Label(content, textvariable=dest_var, fg="#1a73e8", wraplength=WIN_W - 120, justify="left")
    dest_label.pack(pady=(0, 10), fill="x")

    sugg_list = tk.Listbox(content, height=8, width=120, selectmode=tk.EXTENDED)
    sugg_list.place_forget()
    add_btn = tk.Button(content, text="Add Selected Suggestions")
    add_btn.place_forget()

    def parsed_tags():
        text = entry.get()
        parts = [t.strip() for t in text.split(",") if t.strip()]
        cleaned, seen_local = [], set()
        for t in parts:
            l = t.lower()
            if l not in seen_local:
                cleaned.append(t)
                seen_local.add(l)
        return cleaned

    def current_fragment():
        text = entry.get()
        caret = entry.index(tk.INSERT)
        left = text[:caret]
        parts = left.split(",")
        return parts[-1].strip()

    def refresh_destination():
        tags = parsed_tags()
        sub = manual_entry.get().strip()
        try:
            base = resolve_destination_from_tags(tags) if tags else "?"
            full = os.path.join(base, sub) if sub else base
            dest_var.set(f"Destination: {full}")
        except Exception:
            dest_var.set("Destination: (unable to predict)")

    def set_entry_with_selection(sel):
        text = entry.get()
        full = [t.strip() for t in text.split(",")]
        full[-1] = sel
        entry.delete(0, tk.END)
        entry.insert(0, ", ".join(full))
        entry.icursor(tk.END)
        refresh_destination()

    def add_selected():
        try:
            sels = [sugg_list.get(i) for i in sugg_list.curselection()]
            if not sels:
                return
            text = entry.get()
            full = [t.strip() for t in text.split(",")]
            if full:
                full[-1] = sels[0]
            else:
                full = [sels[0]]
            seen_local = {t.lower() for t in full if t}
            for s in sels[1:]:
                if s.lower() not in seen_local:
                    full.append(s)
                    seen_local.add(s.lower())
            entry.delete(0, tk.END)
            entry.insert(0, ", ".join([t for t in full if t]))
            entry.icursor(tk.END)
            sugg_list.place_forget()
            add_btn.place_forget()
            refresh_destination()
        except Exception:
            pass

    add_btn.configure(command=add_selected)

    def update_suggestions(_evt=None):
        frag = current_fragment().lower()
        if not frag:
            sugg_list.place_forget()
            add_btn.place_forget()
            refresh_destination()
            return

        starts = [t for t in AVAILABLE_TAGS if t.lower().startswith(frag)]
        contains = [t for t in AVAILABLE_TAGS if frag in t.lower() and t not in starts]
        fuzzy = difflib.get_close_matches(frag, AVAILABLE_TAGS, n=5, cutoff=FUZZY_CUTOFF)

        seen_local, merged = set(), []
        for group in (starts, contains, fuzzy):
            for item in group:
                l = item.lower()
                if l not in seen_local:
                    merged.append(item)
                    seen_local.add(l)
        merged = merged[:SUGGESTION_LIMIT]

        if merged:
            sugg_list.delete(0, tk.END)
            for s in merged:
                sugg_list.insert(tk.END, s)
            content.update_idletasks()
            ex = entry.winfo_rootx() - root.winfo_rootx()
            ey = entry.winfo_rooty() - root.winfo_rooty() + entry.winfo_height()
            sugg_list.place(x=ex, y=ey)
            add_btn.place(x=ex, y=ey + sugg_list.winfo_reqheight() + 4)
        else:
            sugg_list.place_forget()
            add_btn.place_forget()

        refresh_destination()

    sugg_list.bind("<Double-Button-1>", lambda _: set_entry_with_selection(sugg_list.get(sugg_list.curselection()[0])))

    result = {"value": None}

    def save_tags():
        result["value"] = {
            "tags": parsed_tags(),
            "subfolder": manual_entry.get().strip() or None
        }
        root.destroy()

    def skip():
        result["value"] = None
        root.destroy()

    def sort_uncat():
        result["value"] = "SORT_UNCATEGORIZED"
        root.destroy()

    def delete():
        if messagebox.askyesno("Delete image", "Permanently delete this image?"):
            result["value"] = "DELETE_FILE"
            root.destroy()

    footer = tk.Frame(root)
    footer.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 10))
    tk.Button(footer, text="Save & Continue", command=save_tags).pack(side="left", padx=6)
    tk.Button(footer, text="Skip (leave file)", command=skip).pack(side="left", padx=6)
    tk.Button(footer, text="Skip → SORT/uncategorized", command=sort_uncat).pack(side="left", padx=6)
    tk.Button(footer, text="Delete", command=delete).pack(side="left", padx=6)

    entry.bind("<KeyRelease>", update_suggestions)
    manual_entry.bind("<KeyRelease>", lambda _: refresh_destination())
    root.after(50, lambda: (update_suggestions(), refresh_destination()))
    root.mainloop()
    return result["value"]
