# Jaicat Kanban Board (Tkinter) â€“ drag & drop, JSON-backed
# Adds smart fallback to kanban_data_default.json so user boards inherit your seed.
# Data dir: <project>/data/

import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

KANBAN_BASE_DIR = Path(__file__).resolve().parents[1]  # project root (assumes /ui/)
KANBAN_DATA_DIR = KANBAN_BASE_DIR / "data"
KANBAN_DATA_DIR.mkdir(parents=True, exist_ok=True)

def _default_path_for(user_id: str = "default"):
    # Per-user board file (customize if you want)
    return KANBAN_DATA_DIR / f"kanban_data_{user_id}.json"

def _default_seed_path():
    return KANBAN_DATA_DIR / "kanban_data_default.json"

DEFAULT_SEED = {
    "columns": [
        {"id": "planned", "title": "Planned"},
        {"id": "in_progress", "title": "In Progress"},
        {"id": "done", "title": "Done"}
    ],
    "cards": []
}

class KanbanBoard(ttk.Frame):
    """A simple Kanban board with 3+ columns, drag/drop cards, JSON persistence."""
    def __init__(self, master, user_id: str = "default", on_change=None, json_path=None):
        super().__init__(master)
        self.user_id = user_id
        self.on_change = on_change
        self.json_path = Path(json_path) if json_path else _default_path_for(user_id)
        self.data = self._load()
        self._drag_state = {"card": None, "ghost": None, "src_col": None}
        self._build_ui()
        self._render()

    # ---------- Data ----------
    def _load(self):
        # 1) Try user file
        if self.json_path.exists():
            try:
                return json.loads(self.json_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        # 2) Fallback to default seed file (copy it into user file for persistence)
        seed_path = _default_seed_path()
        if seed_path.exists():
            try:
                data = json.loads(seed_path.read_text(encoding="utf-8"))
                try:
                    self.json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
                except Exception:
                    pass
                return data
            except Exception:
                pass
        # 3) Final fallback: in-memory seed
        return json.loads(json.dumps(DEFAULT_SEED))

    def _save(self):
        try:
            self.json_path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
            if self.on_change:
                self.on_change(self.data)
        except Exception as e:
            messagebox.showerror("Kanban", f"Failed to save board: {e}")

    def _cards_in(self, col_id):
        return [c for c in self.data.get("cards", []) if c.get("status") == col_id]

    def _move_card(self, card_id, dst_col):
        for c in self.data["cards"]:
            if c["id"] == card_id:
                c["status"] = dst_col
                break
        self._save()
        self._render_columns()

    # ---------- UI ----------
    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Kanban.TLabelframe", background="#2C3E50", foreground="white")
        style.configure("Kanban.TLabelframe.Label", foreground="white")
        style.configure("Kanban.TFrame", background="#2C3E50")
        style.configure("Card.TFrame", relief="raised")
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Desc.TLabel", font=("Arial", 10))

        # Scrollable canvas for columns
        self.canvas = tk.Canvas(self, bg="#2C3E50", highlightthickness=0)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hbar.set)

        self.columns_frame = ttk.Frame(self.canvas, style="Kanban.TFrame")
        self._columns_window = self.canvas.create_window((0,0), window=self.columns_frame, anchor="nw")

        self.canvas.pack(fill="both", expand=True, side="top")
        self.hbar.pack(fill="x", side="bottom")

        self.columns_frame.bind("<Configure>", lambda e: self._on_columns_configure())
        self.canvas.bind("<Configure>", lambda e: self._on_canvas_configure())

        # Top bar actions
        topbar = ttk.Frame(self, style="Kanban.TFrame")
        topbar.place(x=10, y=10)
        add_btn = ttk.Button(topbar, text="âž• New Card", command=self._new_card_dialog)
        add_btn.grid(row=0, column=0, padx=4)

        save_btn = ttk.Button(topbar, text="ðŸ’¾ Save", command=self._save)
        save_btn.grid(row=0, column=1, padx=4)

    def _on_columns_configure(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self):
        self.canvas.itemconfig(self._columns_window, height=self.canvas.winfo_height())

    def _render(self):
        # Render columns + cards
        for w in self.columns_frame.winfo_children():
            w.destroy()

        self._column_widgets = {}
        for idx, col in enumerate(self.data.get("columns", [])):
            lf = ttk.Labelframe(self.columns_frame, text=col["title"], style="Kanban.TLabelframe")
            lf.grid(row=0, column=idx, padx=10, pady=20, sticky="ns")
            inner = ttk.Frame(lf, style="Kanban.TFrame")
            inner.pack(fill="both", expand=True, padx=8, pady=8)
            self._column_widgets[col["id"]] = inner

        self._render_columns()

    def _render_columns(self):
        # Clear all column inner frames; re-add cards
        for col_id, inner in self._column_widgets.items():
            for w in inner.winfo_children():
                w.destroy()
            cards = self._cards_in(col_id)
            for c in cards:
                self._add_card_widget(inner, c, col_id)

    def _add_card_widget(self, parent, card, col_id):
        frame = ttk.Frame(parent, style="Card.TFrame")
        frame.pack(fill="x", expand=True, pady=6)

        # Status dot
        dot = "ðŸŸ¢" if col_id == "in_progress" else ("ðŸŸ¡" if col_id == "planned" else "âœ…")
        tl = ttk.Label(frame, text=f"{dot} {card.get('title','Untitled')}", style="Title.TLabel")
        tl.pack(anchor="w", padx=8, pady=(6, 2))

        if card.get("desc"):
            dl = ttk.Label(frame, text=card["desc"], style="Desc.TLabel", wraplength=220)
            dl.pack(anchor="w", padx=8, pady=(0,6))

        # Right-click menu
        menu = tk.Menu(frame, tearoff=0)
        for col in self.data["columns"]:
            menu.add_command(label=f"Move to: {col['title']}",
                             command=lambda cid=card["id"], dst=col["id"]: self._move_card(cid, dst))
        menu.add_separator()
        menu.add_command(label="Renameâ€¦", command=lambda c=card: self._rename_card_dialog(c))
        menu.add_command(label="Edit Descriptionâ€¦", command=lambda c=card: self._edit_desc_dialog(c))
        menu.add_separator()
        menu.add_command(label="Delete", command=lambda c=card: self._delete_card(c))

        def open_menu(evt):
            menu.tk_popup(evt.x_root, evt.y_root)
        frame.bind("<Button-3>", open_menu)
        tl.bind("<Button-3>", open_menu)

        # Drag & drop (simple ghost)
        frame.bind("<Button-1>", lambda e, c=card, f=frame: self._on_drag_start(e, c, f))
        frame.bind("<B1-Motion>", self._on_drag_motion)
        frame.bind("<ButtonRelease-1>", lambda e, c=card: self._on_drag_release(e, c))

    # ---------- Card CRUD ----------
    def _new_card_dialog(self):
        top = tk.Toplevel(self); top.title("New Card")
        tk.Label(top, text="Title").grid(row=0, column=0, padx=6, pady=6)
        t = tk.Entry(top, width=40); t.grid(row=0, column=1, padx=6, pady=6)
        tk.Label(top, text="Description").grid(row=1, column=0, padx=6, pady=6)
        d = tk.Text(top, width=40, height=4); d.grid(row=1, column=1, padx=6, pady=6)

        def ok():
            title = t.get().strip() or "Untitled"
            desc  = d.get("1.0", "end").strip()
            new_id = self._gen_id(title)
            first_col = self.data["columns"][0]["id"]
            self.data["cards"].append({"id": new_id, "title": title, "desc": desc, "status": first_col})
            self._save(); self._render_columns(); top.destroy()
        ttk.Button(top, text="Create", command=ok).grid(row=2, column=1, padx=6, pady=6, sticky="e")

    def _rename_card_dialog(self, card):
        top = tk.Toplevel(self); top.title("Rename Card")
        tk.Label(top, text="New title").grid(row=0, column=0, padx=6, pady=6)
        t = tk.Entry(top, width=40); t.grid(row=0, column=1, padx=6, pady=6)
        t.insert(0, card.get("title",""))
        def ok():
            card["title"] = t.get().strip() or card["title"]
            self._save(); self._render_columns(); top.destroy()
        ttk.Button(top, text="OK", command=ok).grid(row=1, column=1, padx=6, pady=6, sticky="e")

    def _edit_desc_dialog(self, card):
        top = tk.Toplevel(self); top.title("Edit Description")
        d = tk.Text(top, width=50, height=8); d.grid(row=0, column=0, padx=8, pady=8, columnspan=2)
        d.insert("1.0", card.get("desc",""))
        def ok():
            card["desc"] = d.get("1.0", "end").strip()
            self._save(); self._render_columns(); top.destroy()
        ttk.Button(top, text="Save", command=ok).grid(row=1, column=1, padx=8, pady=8, sticky="e")

    def _delete_card(self, card):
        if messagebox.askyesno("Delete", f"Delete card '{card.get('title','')}'?"):
            self.data["cards"] = [c for c in self.data["cards"] if c["id"] != card["id"]]
            self._save(); self._render_columns()

    def _gen_id(self, title):
        base = "".join(ch.lower() for ch in title if ch.isalnum())[:12] or "card"
        suffix = 1
        ids = {c["id"] for c in self.data["cards"]}
        new_id = base
        while new_id in ids:
            suffix += 1
            new_id = f"{base}{suffix}"
        return new_id

    # ---------- Drag helpers ----------
    def _on_drag_start(self, event, card, widget):
        self._drag_state["card"] = card
        self._drag_state["src_col"] = card["status"]
        # Create a ghost label
        ghost = tk.Toplevel(self)
        ghost.overrideredirect(True)
        ghost.attributes("-topmost", True)
        label = tk.Label(ghost, text=card.get("title",""), bg="#34495E", fg="white", padx=8, pady=4)
        label.pack()
        ghost.geometry(f"+{event.x_root}+{event.y_root}")
        self._drag_state["ghost"] = ghost

    def _on_drag_motion(self, event):
        ghost = self._drag_state.get("ghost")
        if ghost:
            ghost.geometry(f"+{event.x_root+8}+{event.y_root+8}")

    def _on_drag_release(self, event, card):
        ghost = self._drag_state.get("ghost")
        if ghost:
            try:
                ghost.destroy()
            except Exception:
                pass
        self._drag_state["ghost"] = None

        # Determine destination column by x coordinate
        x_root = event.x_root
        dst_col = self._col_at_screen_x(x_root)
        if dst_col and dst_col != card["status"]:
            self._move_card(card["id"], dst_col)

        self._drag_state["card"] = None
        self._drag_state["src_col"] = None

    def _col_at_screen_x(self, screen_x):
        # Use columns_frame children bounding boxes
        for col_id, inner in self._column_widgets.items():
            widget = inner.master  # the Labelframe
            x = widget.winfo_rootx()
            w = widget.winfo_width()
            if x <= screen_x <= x + w:
                return col_id
        return None

# ---------- Helpers to embed / open ----------
def attach_kanban_to_root(root, user_id: str = "default", on_change=None):
    """Embed the board into an existing Tk root/container."""
    board = KanbanBoard(root, user_id=user_id, on_change=on_change)
    board.pack(fill=tk.BOTH, expand=True)
    return board

def open_kanban_window(user_id: str = "default", on_change=None, master=None,
                       title: str = "Jaicat â€“ Build Board", width: int = 1100, height: int = 640):
    """Open the board in its own window (or a Toplevel if master provided)."""
    if master is None:
        root = tk.Tk(); root.title(title); root.geometry(f"{width}x{height}")
        try: ttk.Style().theme_use("clam")
        except Exception: pass
        board = KanbanBoard(root, user_id=user_id, on_change=on_change)
        board.pack(fill=tk.BOTH, expand=True)
        root.mainloop()
        return board
    else:
        win = tk.Toplevel(master); win.title(title); win.geometry(f"{width}x{height}")
        try: ttk.Style().theme_use("clam")
        except Exception: pass
        board = KanbanBoard(win, user_id=user_id, on_change=on_change)
        board.pack(fill=tk.BOTH, expand=True)
        return board

def handle_intent_open_build_board(user_id: str = "default", ui_root=None):
    """Call this when intent == OPEN_BUILD_BOARD or user says 'open build board'."""
    return open_kanban_window(user_id=user_id, master=ui_root)
