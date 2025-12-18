# ui/JaicatUI.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

# ---- Theme / assets ----
PANEL_BG = "#14212b"
TEXT_ON_PANEL = "#eaf2f8"
BG_IMAGE_PATH = os.path.join("assets", "jaicat_bg.jpg")


class JaicatUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.controller.set_ui(self)  # allow controller to call back

        # internal
        self._bg_pil = None
        self._bg_tk = None
        self._resize_job = None

        # build UI
        self._build_topbar()
        self._set_background()
        self._build_panel_widgets()
        self._build_statusbar()

    # ---------- Top Toolbar ----------
    def _build_topbar(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(side="top", fill="x", padx=10, pady=(8, 2))
        ttk.Button(btn_frame, text="Learn from Link", command=self._on_learn_link).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Learn from File", command=self._on_learn_file).pack(side="left")

    # ---------- Layout ----------
    def _set_background(self):
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#0e1a23")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", tags="bg")

        self.left_panel_rect = self.canvas.create_rectangle(0, 0, 0, 0, fill=PANEL_BG, outline="", stipple="gray25")
        self.right_panel_rect = self.canvas.create_rectangle(0, 0, 0, 0, fill=PANEL_BG, outline="", stipple="gray25")

        self.left_frame = tk.Frame(self.canvas, bg=PANEL_BG)
        self.right_frame = tk.Frame(self.canvas, bg=PANEL_BG)

        self.left_win = self.canvas.create_window(0, 0, window=self.left_frame, anchor="nw")
        self.right_win = self.canvas.create_window(0, 0, window=self.right_frame, anchor="nw")

        self.root.bind("<Configure>", self._on_resize)
        self._load_bg()

    def _cover_scale(self, img, w, h):
        iw, ih = img.size
        scale = max(w / iw, h / ih)
        img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
        x = max((img.width - w) // 2, 0)
        y = max((img.height - h) // 2, 0)
        return img.crop((x, y, x + w, y + h))

    def _load_bg(self):
        try:
            self._bg_pil = Image.open(BG_IMAGE_PATH).convert("RGB")
            w, h = max(self.root.winfo_width(), 1), max(self.root.winfo_height(), 1)
            scaled = self._cover_scale(self._bg_pil, w, h)
            try:
                overlay = Image.new("RGBA", (w, h), (0, 0, 0, 70))
                scaled = scaled.convert("RGBA")
                scaled.alpha_composite(overlay)
                scaled = scaled.convert("RGB")
            except Exception:
                pass
            self._bg_tk = ImageTk.PhotoImage(scaled)
            self.canvas.delete("bg")
            self.canvas.create_image(0, 0, image=self._bg_tk, anchor="nw", tags="bg")
            self.canvas.tag_lower("bg")
            self._reposition_overlay()
        except Exception:
            self.canvas.configure(bg="#2C3E50")
            self._reposition_overlay()

    def _on_resize(self, _evt=None):
        if self._resize_job:
            try:
                self.root.after_cancel(self._resize_job)
            except Exception:
                pass
        self._resize_job = self.root.after(50, self._load_bg)

    def _reposition_overlay(self):
        w, h = max(self.root.winfo_width(), 1), max(self.root.winfo_height(), 1)
        margin, gutter = 20, 20
        col_w = (w - (margin * 2) - gutter) // 2
        top_y = int(h * 0.10)
        bot_y = h - margin - 40

        lx1, ly1 = margin, top_y
        lx2 = lx1 + col_w
        self.canvas.coords(self.left_panel_rect, lx1, ly1, lx2, bot_y)
        self.canvas.coords(self.left_win, lx1 + 10, ly1 + 10)
        self.canvas.itemconfig(self.left_win, width=col_w - 20)

        rx1 = w - margin - col_w
        rx2 = w - margin
        self.canvas.coords(self.right_panel_rect, rx1, top_y, rx2, bot_y)
        self.canvas.coords(self.right_win, rx1 + 10, top_y + 10)
        self.canvas.itemconfig(self.right_win, width=col_w - 20)

    # ---------- Panel Widgets ----------
    def _build_panel_widgets(self):
        self.face_label = tk.Label(self.left_frame, text="[neutral]", bg=PANEL_BG, fg=TEXT_ON_PANEL)
        self.face_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(6, 2))

        self.calendar_lbl = tk.Label(self.left_frame, text="", font=("Arial", 14), bg="#1ABC9C", fg="white")
        self.calendar_lbl.grid(row=1, column=0, columnspan=2, sticky="ew", padx=6, pady=(6, 4))

        self.weather_lbl = tk.Label(self.left_frame, text="", font=("Arial", 14), bg="#1ABC9C", fg="white")
        self.weather_lbl.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 14))

        self.input_box = tk.Entry(self.left_frame, font=("Arial", 14))
        self.input_box.grid(row=3, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 10))
        self.input_box.grid_remove()
        self.input_box.bind("<Return>", self.on_enter_pressed)

        # Buttons on right (all grid — no pack!)
        btn_style = dict(font=("Arial", 12), fg="white", padx=10, pady=6)
        tk.Button(self.right_frame, text="Text Input", command=self._show_entry,
                  bg="#E74C3C", **btn_style).grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        tk.Button(self.right_frame, text="Play Music", command=self._play_music,
                  bg="#3498DB", **btn_style).grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        tk.Button(self.right_frame, text="Kanban Board", command=self._open_kanban,
                  bg="#9B59B6", **btn_style).grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        tk.Button(self.right_frame, text="Weather", command=self._show_weather,
                  bg="#16A085", **btn_style).grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        tk.Button(self.right_frame, text="Calendar", command=self._show_calendar,
                  bg="#16A085", **btn_style).grid(row=4, column=0, sticky="ew", padx=10, pady=10)

        ttk.Button(self.right_frame, text="Activate Surveillance",
                   command=lambda: self.controller.process_user_text("start surveillance")
                   ).grid(row=5, column=0, sticky="ew", padx=10, pady=6)

        ttk.Button(self.right_frame, text="📚 Ingest Link", command=self._on_learn_link
                   ).grid(row=6, column=0, sticky="ew", padx=10, pady=6)

        ttk.Button(self.right_frame, text="📁 Ingest File", command=self._on_learn_file
                   ).grid(row=7, column=0, sticky="ew", padx=10, pady=6)

    # ---------- Status Bar ----------
    def _build_statusbar(self):
        self.status = tk.Label(self.root, text="Ready", bd=1, anchor="w", bg="#0e1a23", fg=TEXT_ON_PANEL)
        self.status.pack(fill="x", side="bottom")

    # ---------- Controller callbacks / helpers ----------
    def set_face_by_mood(self, mood: str, user: str = "Jay"):
        """
        Accepts either UI 'mood' (happy/sad/neutral/attentive) or sentiment (positive/negative/neutral).
        """
        # Normalize
        mood_map = {"positive": "happy", "negative": "sad", "neutral": "neutral"}
        mood = mood_map.get(mood, mood)

        file_map = {
            "happy": "face_happy.png",
            "sad": "face_sad.png",
            "flirty": "face_flirty.png",
            "concerned": "face_concerned.png",
            "neutral": "face_neutral.png",
            "attentive": "face_neutral.png",
        }
        file = file_map.get(mood, "face_neutral.png")
        try:
            img = Image.open(os.path.join("assets", file))
            photo = ImageTk.PhotoImage(img)
            # Attach to label (avoid GC)
            self.face_label.configure(image=photo, text="")
            self.face_label.image = photo
        except Exception as e:
            print(f"[ui] Failed to set face: {e}")
            self.face_label.configure(text=f"[{mood}]", image="")

    def speak(self, text: str):
        msg = str(text)
        self.status.config(text=msg)
        lowered = msg.lower()
        if "weather" in lowered or "°" in lowered:
            self.weather_lbl.config(text=msg[:120])
        if "calendar" in lowered or "date" in lowered or "event" in lowered:
            self.calendar_lbl.config(text=msg[:120])

    # ---------- UI actions ----------
    def _show_entry(self):
        if self.input_box.winfo_ismapped():
            self.input_box.grid_remove()
        else:
            self.input_box.grid()
            self.input_box.focus_set()

    def on_enter_pressed(self, _event=None):
        user_input = self.input_box.get()
        self.input_box.delete(0, tk.END)
        if not user_input:
            return
        reply = self.controller.process_user_text(user_input)
        self.status.config(text=str(reply))

    def _play_music(self):
        reply = self.controller.process_user_text("play music")
        self.status.config(text=str(reply))

    def _show_weather(self):
        reply = self.controller.process_user_text("what's the weather")
        self.status.config(text=str(reply))

    def _show_calendar(self):
        reply = self.controller.process_user_text("list events")
        self.status.config(text=str(reply))

    def _open_kanban(self):
        try:
            from ui.jaicat_kanban_gui import open_kanban_window
            user_id = getattr(self.controller, "current_user", None) or "default"
            open_kanban_window(user_id=user_id, master=self.root)
            self.status.config(text=f"Kanban opened for {user_id}")
        except Exception as e:
            msg = f"Couldn’t open Kanban: {e}"
            try:
                messagebox.showerror("Kanban Error", msg)
            except Exception:
                pass
            self.status.config(text=msg)

    def _on_learn_link(self):
        try:
            from tkinter import simpledialog
            url = simpledialog.askstring("Learn from Link", "Paste a URL:")
        except Exception:
            url = None
        if not url:
            return
        if hasattr(self.controller, "ingest_url"):
            res = self.controller.ingest_url(url)
            self.status.config(text=str(res))
        else:
            self.status.config(text="No ingest_url handler wired yet.")

    def _on_learn_file(self):
        path = filedialog.askopenfilename(title="Choose a file to learn")
        if not path:
            return
        if hasattr(self.controller, "ingest_file"):
            res = self.controller.ingest_file(path)
            self.status.config(text=f"{res} ({os.path.basename(path)})")
        else:
            self.status.config(text="No ingest_file handler wired yet.")


def launch_ui(controller):
    root = tk.Tk()
    root.title("Jaicat - AI Assistant")
    root.geometry("1200x800")
    root.configure(bg="#0e1a23")

    ui = JaicatUI(root, controller)
    # optional: set initial mood
    ui.set_face_by_mood("neutral")

    root.mainloop()
