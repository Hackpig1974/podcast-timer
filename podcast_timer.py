"""
podcast_timer.py  —  Podcast Timer v1.0
Single-file app. Requires: customtkinter, pygame-ce, numpy, darkdetect
Install: pip install customtkinter pygame-ce numpy darkdetect
Run:     python podcast_timer.py
"""
import customtkinter as ctk
import tkinter as tk
import threading, time, math, os, sys, json, array as _arr

# ── Optional audio (pygame-ce preferred, plain pygame fallback) ───────────
AUDIO_OK = False
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_OK = True
except Exception:
    pass

# ── Settings ──────────────────────────────────────────────────────────────
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
DEFAULT_SETTINGS = {
    "always_on_top": False, "theme": "dark", "zoom": 1.0,
    "audio_enabled": True,  "top_minutes": 20, "top_seconds": 0,
    "bot_minutes": 2,       "bot_seconds": 0,
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            s = DEFAULT_SETTINGS.copy()
            with open(SETTINGS_FILE) as f: s.update(json.load(f))
            return s
        except Exception: pass
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w") as f: json.dump(s, f, indent=2)
    except Exception: pass

# ── Colour palettes ───────────────────────────────────────────────────────
PALETTE = {
    "dark": {
        "bg":"#0f0f1a","bg_yellow":"#2a2200","bg_red":"#2a0a00",
        "zone_bg":"#1a1a2e","zone_border":"#2a2a40","title_bg":"#1c1c2e",
        "text":"#f0f0f0","text_sub":"#888888","green":"#2ecc71",
        "yellow":"#f1c40f","red":"#e74c3c","blue":"#3498db",
        "edit_color":"#7eb3ff","bar_track":"#2a2a3a",
        "btn_start_bg":"#2ecc71","btn_start_fg":"#0a1a0f",
        "btn_stop_bg":"#e74c3c","btn_stop_fg":"#ffffff",
        "btn_next_bg":"#3498db","btn_next_fg":"#ffffff",
    },
    "light": {
        "bg":"#f4f4f8","bg_yellow":"#fffbe6","bg_red":"#fff0ee",
        "zone_bg":"#ffffff","zone_border":"#ddddee","title_bg":"#e8e8f0",
        "text":"#1a1a2e","text_sub":"#666688","green":"#27ae60",
        "yellow":"#b8860b","red":"#c0392b","blue":"#2980b9",
        "edit_color":"#2563eb","bar_track":"#d0d0e0",
        "btn_start_bg":"#27ae60","btn_start_fg":"#ffffff",
        "btn_stop_bg":"#c0392b","btn_stop_fg":"#ffffff",
        "btn_next_bg":"#2980b9","btn_next_fg":"#ffffff",
    },
}

def get_palette(theme, sys_dark=True):
    if theme == "system":
        return PALETTE["dark"] if sys_dark else PALETTE["light"]
    return PALETTE.get(theme, PALETTE["dark"])

# ── Audio helpers ─────────────────────────────────────────────────────────
def _play_tone(freq, dur_ms, vol=0.45):
    if not AUDIO_OK: return
    try:
        import numpy as np
        sr = 44100; n = int(sr * dur_ms / 1000)
        t  = np.linspace(0, dur_ms/1000, n, False)
        wave = np.sin(2 * np.pi * freq * t)
        # fade out last 20%
        fade_start = int(n * 0.8)
        wave[fade_start:] *= np.linspace(1, 0, n - fade_start)
        wave = (wave * vol * 32767).astype(np.int16)
        stereo = np.column_stack([wave, wave])
        snd = pygame.sndarray.make_sound(stereo)
        snd.play()
    except Exception: pass

def beep_yellow(): threading.Thread(target=_play_tone, args=(660, 180), daemon=True).start()
def beep_red():    threading.Thread(target=_play_tone, args=(440, 220), daemon=True).start()
def beep_done():
    threading.Thread(target=_play_tone, args=(330, 300), daemon=True).start()
    threading.Timer(0.38, lambda: threading.Thread(target=_play_tone, args=(330,300),daemon=True).start()).start()

# ── Canvas helpers ────────────────────────────────────────────────────────
def _rrect(cv, x0, y0, x1, y1, r, **kw):
    r = max(1, min(r, (x1-x0)//2, (y1-y0)//2))
    cv.create_arc(x0,y0,x0+2*r,y0+2*r,start=90, extent=90,style="pieslice",**kw)
    cv.create_arc(x1-2*r,y0,x1,y0+2*r,start=0,  extent=90,style="pieslice",**kw)
    cv.create_arc(x0,y1-2*r,x0+2*r,y1,start=180,extent=90,style="pieslice",**kw)
    cv.create_arc(x1-2*r,y1-2*r,x1,y1,start=270,extent=90,style="pieslice",**kw)
    cv.create_rectangle(x0+r,y0,x1-r,y1,**kw)
    cv.create_rectangle(x0,y0+r,x1,y1-r,**kw)

def _vbar(cv, x, y0, y1, col):
    cv.create_rectangle(x-1, y0, x+2, y1, fill=col, outline="")

def _blend(h1, h2, t):
    t = max(0.0, min(1.0, t))
    p = lambda h: tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0,2,4))
    r1,g1,b1 = p(h1); r2,g2,b2 = p(h2)
    return "#{:02x}{:02x}{:02x}".format(
        int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

# ── Canvas pencil button ──────────────────────────────────────────────────
def _make_pencil_canvas(parent, size, bg_color, command):
    cv = tk.Canvas(parent, width=size, height=size,
                   bg=bg_color, highlightthickness=0, cursor="hand2")
    def _draw(hover=False):
        import math as _m
        cv.delete("all")
        s = size
        p  = s * 0.06
        pw = s - 2*p
        ph = s * 0.30
        y_mid = s * 0.50
        y_top = y_mid - ph/2
        y_bot = y_mid + ph/2
        x0 = p
        wood_w  = pw * 0.18
        body_w  = pw * 0.50
        ferr_w  = pw * 0.12
        erase_w = pw * 0.20
        cx2, cy2 = s/2, s/2
        def rot(x, y):
            rx = x - cx2; ry = y - cy2
            a = _m.radians(-45)
            return (cx2 + rx*_m.cos(a) - ry*_m.sin(a),
                    cy2 + rx*_m.sin(a) + ry*_m.cos(a))
        def rquad(x1, x2, yt, yb, fill, outline):
            pts = [rot(x1,yt), rot(x2,yt), rot(x2,yb), rot(x1,yb)]
            flat = [v for pt in pts for v in pt]
            cv.create_polygon(flat, fill=fill, outline=outline, width=1)
        tx = x0 + wood_w
        tip_pts = [rot(x0, y_mid), rot(tx, y_top), rot(tx, y_bot)]
        flat = [v for pt in tip_pts for v in pt]
        cv.create_polygon(flat, fill="#d4956a", outline="#a06030", width=1)
        tdx, tdy = rot(x0 + s*0.015, y_mid)
        r = s * 0.032
        cv.create_oval(tdx-r, tdy-r, tdx+r, tdy+r, fill="#333", outline="")
        bx1 = x0 + wood_w; bx2 = bx1 + body_w
        body_col = "#f5a623" if not hover else "#ffc040"
        rquad(bx1, bx2, y_top, y_bot, body_col, "#c07800")
        h1 = rot(bx1, y_top + ph*0.18); h2 = rot(bx2, y_top + ph*0.18)
        cv.create_line(h1[0],h1[1], h2[0],h2[1], fill="#ffd878", width=max(1,int(s*0.035)))
        fx1 = bx2; fx2 = fx1 + ferr_w
        rquad(fx1, fx2, y_top, y_bot, "#b8b8b8", "#888888")
        ex1 = fx2; ex2 = ex1 + erase_w
        eraser_col = "#f48fb1" if not hover else "#ff6090"
        rquad(ex1, ex2, y_top, y_bot, eraser_col, "#c06080")
    _draw()
    cv.bind("<Enter>",    lambda e: _draw(hover=True))
    cv.bind("<Leave>",    lambda e: _draw(hover=False))
    cv.bind("<Button-1>", lambda e: command())
    return cv


# ─────────────────────────────────────────────────────────────────────────────
# SettingsPanel
# ─────────────────────────────────────────────────────────────────────────────
class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, settings, c, fs, on_apply, on_cancel):
        # Use a neutral mid-gray that's visible on both dark and light themes
        super().__init__(parent, fg_color="#2e2e2e", border_color="#555555",
                         border_width=2, corner_radius=12)
        self.settings = settings.copy(); self.c = c; self.fs = fs
        self.on_apply = on_apply; self.on_cancel = on_cancel
        self._build()

    def _build(self):
        c = self.c; fs = self.fs
        lf = ctk.CTkFont("Space Mono", int(10*fs))
        hf = ctk.CTkFont("Space Mono", int(11*fs), weight="bold")
        bf = ctk.CTkFont("Space Mono", int(10*fs), weight="bold")
        pad = int(20*fs)
        # Use fixed neutral colors for settings panel so it's always visible
        txt   = "#ffffff"
        txt_s = "#aaaaaa"
        sep_c = "#444444"
        sep = lambda: ctk.CTkFrame(self, height=1, fg_color=sep_c).pack(fill="x", padx=pad, pady=6)

        ctk.CTkLabel(self, text="SETTINGS", font=hf, text_color=txt_s).pack(pady=(pad,4))
        sep()

        r1 = ctk.CTkFrame(self, fg_color="transparent"); r1.pack(fill="x", padx=pad, pady=4)
        ctk.CTkLabel(r1, text="Always on Top", font=lf, text_color=txt).pack(side="left")
        self.sw_top = ctk.CTkSwitch(r1, text="", width=int(44*fs),
            progress_color=c["blue"], button_color="#cccccc")
        self.sw_top.pack(side="right")
        if self.settings.get("always_on_top"): self.sw_top.select()
        sep()

        r2 = ctk.CTkFrame(self, fg_color="transparent"); r2.pack(fill="x", padx=pad, pady=4)
        ctk.CTkLabel(r2, text="Theme", font=lf, text_color=txt).pack(side="left")
        self.theme_var = tk.StringVar(value=self.settings.get("theme","dark"))
        pf = ctk.CTkFrame(r2, fg_color="transparent"); pf.pack(side="right")
        for t in ("Light","Dark","System"):
            ctk.CTkRadioButton(pf, text=t, variable=self.theme_var, value=t.lower(),
                font=lf, text_color=txt, fg_color=c["blue"]).pack(side="left", padx=6)
        sep()

        r3 = ctk.CTkFrame(self, fg_color="transparent"); r3.pack(fill="x", padx=pad, pady=4)
        ctk.CTkLabel(r3, text="Zoom", font=lf, text_color=txt).pack(side="left")
        self.zoom_lbl = ctk.CTkLabel(r3, text=f"{int(self.settings.get('zoom',1.0)*100)}%",
            font=lf, text_color=c["blue"], width=int(44*fs))
        self.zoom_lbl.pack(side="right")
        self.zoom_sl = ctk.CTkSlider(r3, from_=0.85, to=2.0, number_of_steps=23,
            progress_color=c["blue"], button_color=c["blue"], width=int(160*fs),
            command=lambda v: self.zoom_lbl.configure(text=f"{int(v*100)}%"))
        self.zoom_sl.set(self.settings.get("zoom",1.0)); self.zoom_sl.pack(side="right", padx=8)
        sep()

        r4 = ctk.CTkFrame(self, fg_color="transparent"); r4.pack(fill="x", padx=pad, pady=4)
        ctk.CTkLabel(r4, text="Audio Cues", font=lf, text_color=txt).pack(side="left")
        self.sw_audio = ctk.CTkSwitch(r4, text="", width=int(44*fs),
            progress_color=c["blue"], button_color="#cccccc")
        self.sw_audio.pack(side="right")
        if self.settings.get("audio_enabled", True): self.sw_audio.select()
        sep()

        br = ctk.CTkFrame(self, fg_color="transparent"); br.pack(pady=(4, 8))
        ctk.CTkButton(br, text="APPLY", font=bf, fg_color=c["blue"], text_color="#ffffff",
            width=int(90*fs), command=self._apply).grid(row=0, column=0, padx=8)
        ctk.CTkButton(br, text="CANCEL", font=bf, fg_color="#555555", text_color="#cccccc",
            width=int(90*fs), command=self.on_cancel).grid(row=0, column=1, padx=8)
        
        # Credit line
        ctk.CTkLabel(self, text="Developed by Damon Downing, 2026",
            font=ctk.CTkFont("Space Mono", int(10*fs)), text_color="#ffffff").pack(pady=(4, pad))

    def _apply(self):
        self.settings["always_on_top"] = bool(self.sw_top.get())
        self.settings["theme"]         = self.theme_var.get()
        self.settings["zoom"]          = round(self.zoom_sl.get(), 2)
        self.settings["audio_enabled"] = bool(self.sw_audio.get())
        self.on_apply(self.settings)

# ─────────────────────────────────────────────────────────────────────────────
# TimerZone
# ─────────────────────────────────────────────────────────────────────────────
class TimerZone(ctk.CTkFrame):
    THRESH_YELLOW = 0.75
    THRESH_RED    = 0.90

    def __init__(self, parent, label, fs, is_top, colors,
                 on_start=None, on_stop=None, on_next=None, **kw):
        super().__init__(parent, **kw)
        self.label_text = label; self.fs = fs; self.is_top = is_top; self.c = colors
        self.on_start = on_start; self.on_stop = on_stop; self.on_next = on_next
        self.on_pause = None
        self.on_edit = None   # set by app to open editing on both zones simultaneously
        self.total_sec = 0; self.remain_sec = 0; self.running = False; self.editable = True
        self.edit_min = 0; self.edit_sec = 0; self.stage = "great"
        self._bar_pct = 0.0; self._pulse_alpha = 1.0
        self._build()

    def _build(self):
        c = self.c; fs = self.fs
        self.configure(fg_color=c["zone_bg"], border_color=c["zone_border"], border_width=1, corner_radius=10)
        ds  = int(88*fs) if self.is_top else int(62*fs)
        lbs = int(10*fs); bts = int(11*fs); sts = int(10*fs)
        ew  = int(96*fs) if self.is_top else int(68*fs)
        BTN_W = int(140*fs)   # uniform width for all bottom buttons

        self.lbl_zone = ctk.CTkLabel(self, text=self.label_text,
            font=ctk.CTkFont("Space Mono", lbs), text_color=c["text_sub"])
        self.lbl_zone.pack(pady=(6,2))

        # ── outer frame just acts as an anchor point for .place() ──
        self._digit_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._digit_outer.pack()

        # label-row (always visible except during editing)
        self._df_labels = ctk.CTkFrame(self._digit_outer, fg_color="transparent")
        self._df_labels.pack()

        self.lbl_min = ctk.CTkLabel(self._df_labels, text="00",
            font=ctk.CTkFont("Space Mono", ds, weight="bold"), text_color=c["edit_color"])
        self.lbl_min.grid(row=0, column=0)
        self.lbl_col = ctk.CTkLabel(self._df_labels, text=":",
            font=ctk.CTkFont("Space Mono", ds, weight="bold"), text_color=c["text_sub"])
        self.lbl_col.grid(row=0, column=1, padx=2)
        self.lbl_sec_d = ctk.CTkLabel(self._df_labels, text="00",
            font=ctk.CTkFont("Space Mono", ds, weight="bold"), text_color=c["edit_color"])
        self.lbl_sec_d.grid(row=0, column=2)
        # pencil canvas button — only on top zone
        if self.is_top:
            pencil_size = max(36, int(44 * fs))
            self._pencil_bg = c["zone_bg"]
            self._pencil_size = pencil_size
            self._btn_edit = _make_pencil_canvas(
                self._df_labels, pencil_size, c["zone_bg"], self._enter_edit_mode)
            self._btn_edit.grid(row=0, column=3, padx=(12, 0))
        else:
            self._btn_edit = None

        # entry-row (hidden; packed/unpacked to swap with label-row)
        self._df_entries = ctk.CTkFrame(self._digit_outer, fg_color="transparent")

        self._ent_min = ctk.CTkEntry(self._df_entries, width=int(120*fs) if self.is_top else int(90*fs), height=int(70*fs) if self.is_top else int(60*fs), justify="center",
            font=ctk.CTkFont("Space Mono", ds, weight="bold"),
            fg_color=c["bg"], text_color=c["edit_color"],
            border_color=c["edit_color"], border_width=2)
        self._ent_min.grid(row=0, column=0)
        ctk.CTkLabel(self._df_entries, text=":",
            font=ctk.CTkFont("Space Mono", ds, weight="bold"),
            text_color=c["text_sub"]).grid(row=0, column=1, padx=4)
        self._ent_sec = ctk.CTkEntry(self._df_entries, width=int(120*fs) if self.is_top else int(90*fs), height=int(70*fs) if self.is_top else int(60*fs), justify="center",
            font=ctk.CTkFont("Space Mono", ds, weight="bold"),
            fg_color=c["bg"], text_color=c["edit_color"],
            border_color=c["edit_color"], border_width=2)
        self._ent_sec.grid(row=0, column=2)
        if self.is_top:
            self._btn_confirm = ctk.CTkButton(self._df_entries, text="SAVE",
                width=int(62*fs), height=int(26*fs),
                font=ctk.CTkFont("Space Mono", int(9*fs), weight="bold"),
                fg_color="#27a85e", hover_color="#1e8449",
                text_color="#ffffff", corner_radius=4,
                command=self._commit_edit)
            self._btn_confirm.grid(row=0, column=3, padx=(10,0))

        self._ent_min.bind("<Return>", lambda e: self._commit_edit())
        self._ent_min.bind("<Escape>", lambda e: self._cancel_edit())
        self._ent_sec.bind("<Return>", lambda e: self._commit_edit())
        self._ent_sec.bind("<Escape>", lambda e: self._cancel_edit())
        self._ent_min.bind("<Tab>",    lambda e: (self._ent_sec.focus(), "break"))
        self._editing = False

        # progress bar
        bh = int(12*fs)
        self.bar_cv = tk.Canvas(self, height=bh+int(16*fs), bg=c["zone_bg"], highlightthickness=0)
        self.bar_cv.pack(fill="x", padx=int(28*fs), pady=(6,2))
        self.bar_cv.bind("<Configure>", lambda e: self._draw_bar())

        # status label
        self.lbl_status = ctk.CTkLabel(self, text="" if not self.is_top else "DOING GREAT",
            font=ctk.CTkFont("Space Mono", sts), text_color=c["green"])
        self.lbl_status.pack(pady=(0,2))

        # buttons — uniform width
        bf = ctk.CTkFrame(self, fg_color="transparent"); bf.pack(pady=(2,8))
        if self.is_top:
            self.btn_s = ctk.CTkButton(bf, text="▶  START",
                font=ctk.CTkFont("Space Mono",bts,weight="bold"),
                fg_color=c["btn_start_bg"], text_color=c["btn_start_fg"],
                width=BTN_W, height=int(34*fs), corner_radius=6,
                command=lambda: self.on_start and self.on_start())
            self.btn_s.grid(row=0,column=0,padx=6)
            self.btn_p = ctk.CTkButton(bf, text="■  STOP",
                font=ctk.CTkFont("Space Mono",bts,weight="bold"),
                fg_color="#2a1a1a", hover_color="#2a1a1a", text_color="#553333",
                width=BTN_W, height=int(34*fs), corner_radius=6,
                command=lambda: None)
            self.btn_p.grid(row=0,column=1,padx=6)
        else:
            self.btn_n = ctk.CTkButton(bf, text="↺  NEXT / RESET",
                font=ctk.CTkFont("Space Mono",bts,weight="bold"),
                fg_color="#1a2030", hover_color="#1a2030", text_color="#2a3a50",
                width=BTN_W*2+12, height=int(34*fs), corner_radius=6,
                command=lambda: None)
            self.btn_n.grid(row=0,column=0)

    # ── inline edit mode ──────────────────────────────────────────────────
    def _enter_edit_mode(self):
        if not self.editable or self._editing: return
        # If app has wired a coordinated edit callback, use that instead
        if self.on_edit:
            self.on_edit(); return
        self._start_edit_local()

    def _start_edit_local(self):
        if self._editing: return
        self._editing = True
        self._df_labels.pack_forget()
        self._ent_min.delete(0, "end"); self._ent_min.insert(0, f"{self.edit_min:02d}")
        self._ent_sec.delete(0, "end"); self._ent_sec.insert(0, f"{self.edit_sec:02d}")
        self._df_entries.pack()
        # Safety check before focusing
        try:
            self._ent_min.focus()
            self._ent_min.select_range(0, "end")
        except:
            pass  # Widget may have been destroyed
        # Dim START button while editing (same style as dimmed STOP/NEXT buttons)
        if self.is_top:
            self.btn_s.configure(fg_color="#1a2e1a", hover_color="#1a2e1a", 
                               text_color="#2a4a2a", cursor="arrow")
    def _commit_edit(self):
        if not self._editing: return
        try:
            m = max(0, min(99, int(self._ent_min.get())))
            s = max(0, min(59, int(self._ent_sec.get())))
        except ValueError:
            self._ent_min.configure(border_color=self.c["red"])
            self._ent_sec.configure(border_color=self.c["red"])
            return
        self._cancel_edit()
        self.set_time(m, s)
        # Re-enable START button after editing
        if self.is_top:
            self.btn_s.configure(fg_color=self.c["btn_start_bg"], 
                               hover_color="#27a85e",
                               text_color=self.c["btn_start_fg"], cursor="hand2")

    def _cancel_edit(self):
        if not self._editing: return
        self._editing = False
        self._df_entries.pack_forget()
        self._ent_min.configure(border_color=self.c["edit_color"])
        self._ent_sec.configure(border_color=self.c["edit_color"])
        self._df_labels.pack()
        # Re-enable START button if editing was cancelled
        if self.is_top:
            self.btn_s.configure(fg_color=self.c["btn_start_bg"], 
                               hover_color="#27a85e",
                               text_color=self.c["btn_start_fg"], cursor="hand2")

    def _draw_bar(self, pulse_alpha=None):
        c = self.c; cv = self.bar_cv; cv.delete("all")
        W = cv.winfo_width()
        if W < 4: return
        fs = self.fs; bh = int(12*fs); y0 = int(8*fs); y1 = y0+bh; r = bh//2
        stage = self.stage; pct = min(self._bar_pct, 1.0)
        track_col = {"great":c["bar_track"],
                     "yellow":_blend(c["yellow"],c["zone_bg"],0.85),
                     "red":   _blend(c["red"],c["zone_bg"],0.85),
                     "done":  _blend(c["red"],c["zone_bg"],0.80)}.get(stage,c["bar_track"])
        _rrect(cv, 0, y0, W, y1, r, fill=track_col, outline="")
        fill_col = {"great":c["green"],"yellow":c["yellow"],"red":c["red"],"done":c["red"]}.get(stage,c["green"])
        fw = int(W*pct)
        if fw > 2: _rrect(cv, 0, y0, fw, y1, r, fill=fill_col, outline="")
        ex = int(5*fs); my0 = y0-ex; my1 = y1+ex
        if stage == "great":
            _vbar(cv, int(W*0.75), my0, my1, c["yellow"])
            _vbar(cv, int(W*0.90), my0, my1, c["red"])
        elif stage == "yellow":
            _vbar(cv, int(W*0.90), my0, my1, c["red"])
        elif stage == "red":
            a = pulse_alpha if pulse_alpha is not None else self._pulse_alpha
            col = _blend(c["red"], c["zone_bg"], 1.0 - a*0.9)
            ex2 = int(7*fs)
            cv.create_rectangle(W-5, y0-ex2, W, y1+ex2, fill=col, outline="")

    def set_time(self, m, s):
        self.edit_min = m; self.edit_sec = s
        self.total_sec = m*60+s; self.remain_sec = self.total_sec
        self._refresh_display()

    def start_timer(self):
        self.running = True; self.editable = False
        if self._editing: self._cancel_edit()
        if self._btn_edit: self._btn_edit.grid_remove()
        self._refresh_digit_color()
        # Apply stage to show status text when starting
        self._apply_stage()
        if self.is_top:
            self.btn_s.configure(text="⏸  PAUSE",
                fg_color="#e67e22", hover_color="#ca6f1e", text_color="#ffffff",
                command=lambda: self.on_pause and self.on_pause())
            self.btn_p.configure(fg_color=self.c["btn_stop_bg"], hover_color="#c0392b",
                text_color=self.c["btn_stop_fg"], text="■  STOP / RESET",
                command=lambda: self.on_stop and self.on_stop())
        else:
            self.btn_n.configure(fg_color=self.c["btn_next_bg"], hover_color="#2a7ac0",
                text_color=self.c["btn_next_fg"],
                command=lambda: self.on_next and self.on_next())

    def stop_timer(self):
        self.running = False; self.editable = True
        if self._btn_edit: self._btn_edit.grid()   # restore pencil only on full reset
        # Reset to default state
        self.stage = "great"
        self._bar_pct = 0.0
        # Reset background color to normal
        self.configure(fg_color=self.c["zone_bg"])
        # Reset zone label
        self.lbl_zone.configure(text=self.label_text, text_color=self.c["text_sub"])
        # Reset digit colors
        self.lbl_min.configure(text_color=self.c["edit_color"])
        self.lbl_sec_d.configure(text_color=self.c["edit_color"])
        self.lbl_col.configure(text_color=self.c["text_sub"])
        # Hide status text for Speaker Timer when stopped
        if not self.is_top:
            self.lbl_status.configure(text="")
        else:
            self.lbl_status.configure(text="")
        if self.is_top:
            self.btn_s.configure(text="▶  START",
                fg_color=self.c["btn_start_bg"], hover_color="#27a85e",
                text_color=self.c["btn_start_fg"],
                command=lambda: self.on_start and self.on_start())
            self.btn_p.configure(text="■  STOP",
                fg_color="#2a1a1a", hover_color="#2a1a1a",
                text_color="#553333", command=lambda: None)
        else:
            self.btn_n.configure(fg_color="#1a2030", hover_color="#1a2030",
                text_color="#2a3a50", command=lambda: None)

    def reset_speaker(self):
        self.remain_sec = self.total_sec; self.stage = "great"; self._bar_pct = 0.0
        self._refresh_display(); self._apply_stage(); self._draw_bar()

    def tick(self):
        if not self.running or self.remain_sec <= 0: return None
        self.remain_sec -= 1; self._refresh_display()
        return self._check_stage()

    def _refresh_display(self):
        m = self.remain_sec//60; s = self.remain_sec%60
        self.lbl_min.configure(text=f"{m:02d}"); self.lbl_sec_d.configure(text=f"{s:02d}")
        self._bar_pct = 1.0-(self.remain_sec/self.total_sec) if self.total_sec>0 else 0.0
        self._draw_bar()
        # Update status text for Episode Timer based on percentage
        if self.is_top and self.stage == "great":
            self._apply_stage()

    def _check_stage(self):
        pct = self._bar_pct
        new = ("done" if self.remain_sec==0 else
               "red"  if pct>=self.THRESH_RED else
               "yellow" if pct>=self.THRESH_YELLOW else "great")
        if new != self.stage:
            self.stage = new; self._apply_stage(); return new
        return None

    def _apply_stage(self):
        c = self.c; s = self.stage
        pct = self._bar_pct
        
        # Episode Timer has special text behavior and background color changes
        if self.is_top:
            # Background color for Episode Timer zone
            if s == "done":
                self.configure(fg_color=c["bg_red"])
            elif s == "red":
                self.configure(fg_color=c["bg_red"])
            elif s == "yellow":
                self.configure(fg_color=c["bg_yellow"])
            else:
                self.configure(fg_color=c["zone_bg"])
            
            # Status text logic for Episode Timer
            if s == "done":
                status_text = "TIME'S UP"
                status_color = c["red"]
            elif s == "red":
                status_text = "FINALIZE THE EPISODE"
                status_color = c["red"]
            elif s == "yellow":
                status_text = "START SUMMARIZING"
                status_color = c["yellow"]
            elif 0.50 <= pct < 0.55:
                status_text = "HALF WAY THERE"
                status_color = c["green"]
            else:
                status_text = ""
                status_color = c["green"]
        else:
            # Speaker Timer also changes background color
            if s == "done":
                self.configure(fg_color=c["bg_red"])
            elif s == "red":
                self.configure(fg_color=c["bg_red"])
            elif s == "yellow":
                self.configure(fg_color=c["bg_yellow"])
            else:
                self.configure(fg_color=c["zone_bg"])
            
            # Speaker Timer status text
            m = {"great": (c["green"],"DOING GREAT"),
                 "yellow":(c["yellow"],"GET TO THE POINT"),
                 "red":   (c["red"],"WRAP IT UP"),
                 "done":  (c["red"],"TIME'S UP")}[s]
            status_color, status_text = m
        
        # Zone label color
        if s == "done":
            zone_color = c["red"]
            zone_text = "TIME'S UP"
        else:
            zone_color = c["text_sub"]
            zone_text = self.label_text
        
        # Digit colors
        if s == "done":
            digit_color = c["red"]
            colon_color = c["red"]
        else:
            digit_color = c["text"]
            colon_color = c["text_sub"]
        
        self.lbl_status.configure(text=status_text, text_color=status_color)
        self.lbl_zone.configure(text=zone_text, text_color=zone_color)
        self.lbl_min.configure(text_color=digit_color)
        self.lbl_sec_d.configure(text_color=digit_color)
        self.lbl_col.configure(text_color=colon_color)

    def _refresh_digit_color(self):
        c = self.c
        col = c["edit_color"] if self.editable else (c["red"] if self.stage=="done" else c["text"])
        self.lbl_min.configure(text_color=col); self.lbl_sec_d.configure(text_color=col)

    def pulse_tick(self, alpha):
        self._pulse_alpha = alpha
        if self.stage == "red": self._draw_bar(pulse_alpha=alpha)
        # Pulse digit colors when done
        if self.stage == "done":
            # Pulse between red and white
            pulse_color = _blend(self.c["red"], "#ffffff", alpha)
            self.lbl_min.configure(text_color=pulse_color)
            self.lbl_sec_d.configure(text_color=pulse_color)
            self.lbl_col.configure(text_color=pulse_color)

# ─────────────────────────────────────────────────────────────────────────────
# PodcastTimerApp
# ─────────────────────────────────────────────────────────────────────────────
class PodcastTimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self._pulse_val = 0.0; self._pulse_dir = 1
        self._settings_open = False; self._clock_running = False
        self._colon_visible = True
        self._apply_settings(self.settings, first_run=True)

    def _apply_settings(self, s, first_run=False):
        self.settings = s; save_settings(s)
        fs = s["zoom"]; theme = s["theme"]
        try:
            import darkdetect; sys_dark = darkdetect.isDark()
        except Exception: sys_dark = True
        self.c = get_palette(theme, sys_dark)
        ctk.set_appearance_mode("dark" if theme in ("dark","system") else "light")
        if first_run:
            self.title("Podcast Timer"); self.resizable(True, True); self.minsize(400, 500)
        self.attributes("-topmost", s["always_on_top"])
        for w in self.winfo_children(): w.destroy()
        self._settings_open = False
        self._build_ui(fs)
        self.top_zone.set_time(s["top_minutes"], s["top_seconds"])
        self.bot_zone.set_time(s["bot_minutes"], s["bot_seconds"])
        if first_run: self._size_window(fs)

    def _size_window(self, fs):
        self.update_idletasks()
        w = int(560*fs); h = int(565*fs)  # Increased to 565 for full button visibility at 100%
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self, fs):
        c = self.c; self.configure(fg_color=c["bg"])
        tb = ctk.CTkFrame(self, fg_color=c["title_bg"], height=int(38*fs), corner_radius=0)
        tb.pack(fill="x"); tb.pack_propagate(False)
        # Removed the ● ● ● dots
        # Add left padding to balance the Settings button on the right
        ctk.CTkLabel(tb, text="", width=int(80*fs)).pack(side="left")
        ctk.CTkLabel(tb, text="PODCAST  TIMER",
                     font=ctk.CTkFont("Space Mono", int(10*fs), weight="bold"),
                     text_color=c["text_sub"]).pack(side="left", expand=True)
        self.btn_settings = ctk.CTkButton(tb, text="Settings", width=int(80*fs), height=int(28*fs),
                      font=ctk.CTkFont("Space Mono", int(12*fs), weight="bold"),
                      fg_color="transparent", hover_color=c["bar_track"],
                      text_color=c["text_sub"], command=self._toggle_settings)
        self.btn_settings.pack(side="right", padx=8)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=int(16*fs), pady=int(8*fs))
        self.top_zone = TimerZone(self.main_frame, "Episode Timer", fs, True, c,
                                  on_start=self._on_start, on_stop=self._on_reset)
        self.top_zone.on_pause = self._on_pause
        self.top_zone.on_edit  = self._on_edit_both
        self.top_zone.pack(fill="x", pady=(0, int(12*fs)))
        ctk.CTkFrame(self.main_frame, height=1, fg_color=c["bar_track"]).pack(
            fill="x", padx=int(40*fs), pady=int(6*fs))
        self.bot_zone = TimerZone(self.main_frame, "Speaker Timer", fs, False, c, on_next=self._on_next)
        self.bot_zone.pack(fill="x", pady=(int(6*fs), 0))

    def _toggle_settings(self):
        if self._settings_open: self._close_settings()
        else: self._open_settings()

    def _open_settings(self):
        self._settings_open = True
        # Dim START button while settings is open
        self.top_zone.btn_s.configure(fg_color="#1a2e1a", hover_color="#1a2e1a", 
                                     text_color="#2a4a2a", cursor="arrow")
        self.settings_panel = SettingsPanel(self, self.settings, self.c, self.settings["zoom"],
                                            on_apply=self._on_settings_apply, on_cancel=self._close_settings)
        self.settings_panel.place(relx=1.0, rely=0.0, anchor="ne",
                                  x=-int(8*self.settings["zoom"]), y=int(44*self.settings["zoom"]))

    def _close_settings(self):
        self._settings_open = False
        # Re-enable START button when settings closes
        self.top_zone.btn_s.configure(fg_color=self.c["btn_start_bg"], 
                                     hover_color="#27a85e",
                                     text_color=self.c["btn_start_fg"], cursor="hand2")
        if hasattr(self, "settings_panel"): self.settings_panel.destroy()

    def _on_settings_apply(self, ns):
        ns["top_minutes"] = self.top_zone.edit_min; ns["top_seconds"] = self.top_zone.edit_sec
        ns["bot_minutes"] = self.bot_zone.edit_min; ns["bot_seconds"] = self.bot_zone.edit_sec
        zoom_changed = ns["zoom"] != self.settings["zoom"]
        self._apply_settings(ns)
        if zoom_changed: self._size_window(ns["zoom"])

    def _on_edit_both(self):
        self.top_zone._start_edit_local()
        self.bot_zone._start_edit_local()
        # Disable Settings button while editing (consistent with running state)
        self.btn_settings.configure(state="disabled")
        # Redirect top OK to commit both
        self.top_zone._btn_confirm.configure(command=self._on_ok_both)

    def _on_ok_both(self):
        self.top_zone._commit_edit()
        self.bot_zone._commit_edit()
        # Re-enable Settings button after editing
        self.btn_settings.configure(state="normal")
        # Restore top OK to normal
        self.top_zone._btn_confirm.configure(command=self.top_zone._commit_edit)

    def _on_start(self):
        self.settings["top_minutes"] = self.top_zone.edit_min
        self.settings["top_seconds"] = self.top_zone.edit_sec
        self.settings["bot_minutes"] = self.bot_zone.edit_min
        self.settings["bot_seconds"] = self.bot_zone.edit_sec
        save_settings(self.settings)
        self.top_zone.start_timer(); self.bot_zone.start_timer()
        # Disable settings button while running
        self.btn_settings.configure(state="disabled")
        if not self._clock_running:
            self._clock_running = True
            threading.Thread(target=self._clock_loop, daemon=True).start()
        self._pulse_loop(); self._blink_loop()

    def _on_pause(self):
        if self._clock_running:
            # PAUSE
            self._clock_running = False
            self.top_zone.btn_s.configure(text="▶  RESUME",
                fg_color=self.c["btn_start_bg"], hover_color="#27a85e",
                text_color=self.c["btn_start_fg"],
                command=self._on_resume)
            # Dim NEXT/RESET button while paused
            self.bot_zone.btn_n.configure(fg_color="#1a2030", hover_color="#1a2030",
                text_color="#2a3a50", cursor="arrow")
        
    def _on_resume(self):
        self._clock_running = True
        self.top_zone.btn_s.configure(text="⏸  PAUSE",
            fg_color="#e67e22", hover_color="#ca6f1e", text_color="#ffffff",
            command=self._on_pause)
        # Re-enable NEXT/RESET button when resumed
        self.bot_zone.btn_n.configure(fg_color=self.c["btn_next_bg"], hover_color="#2a7ac0",
            text_color=self.c["btn_next_fg"], cursor="hand2")
        threading.Thread(target=self._clock_loop, daemon=True).start()
        self._pulse_loop(); self._blink_loop()

    def _on_reset(self):
        self._clock_running = False
        self.top_zone.stop_timer(); self.bot_zone.stop_timer()
        self.top_zone.remain_sec = self.top_zone.total_sec
        self.bot_zone.remain_sec = self.bot_zone.total_sec
        self.top_zone.stage = "great"; self.bot_zone.stage = "great"
        self.top_zone._bar_pct = 0.0;  self.bot_zone._bar_pct = 0.0
        self.top_zone._refresh_display(); self.bot_zone._refresh_display()
        self.top_zone._apply_stage()
        # Don't call _apply_stage on bot_zone - let stop_timer handle it (clears text)
        self.bot_zone._draw_bar()
        self.configure(fg_color=self.c["bg"])
        # Re-enable settings button
        self.btn_settings.configure(state="normal")
        # rewire stop button back to dimmed (no action)
        self.top_zone.btn_p.configure(text="■  STOP",
            fg_color="#2a1a1a", hover_color="#2a1a1a",
            text_color="#553333", command=lambda: None)

    def _on_next(self):
        self.bot_zone.reset_speaker()
        self._update_bg(self.top_zone.stage)

    def _clock_loop(self):
        while self._clock_running:
            time.sleep(1)
            if not self._clock_running: break
            self.after(0, self._tick)

    def _tick(self):
        if not self._clock_running: return
        top_new = self.top_zone.tick(); bot_new = self.bot_zone.tick()
        if self.settings.get("audio_enabled", True):
            for stage in filter(None, [top_new, bot_new]):
                if stage=="yellow": beep_yellow()
                elif stage=="red":  beep_red()
                elif stage=="done": beep_done()
        self._update_bg(self.top_zone.stage)

    def _update_bg(self, stage):
        # Keep main window background constant - no color changes
        pass

    def _pulse_loop(self):
        if not self._clock_running: return
        self._pulse_val += self._pulse_dir * 0.06
        if self._pulse_val >= 1.0: self._pulse_val = 1.0; self._pulse_dir = -1
        if self._pulse_val <= 0.0: self._pulse_val = 0.0; self._pulse_dir =  1
        a = self._pulse_val
        self.top_zone.pulse_tick(a); self.bot_zone.pulse_tick(a)
        # Pulse the entire panel background when done
        if self.top_zone.stage == "done":
            pulse_bg = _blend(self.c["bg_red"], self.c["zone_bg"], 1.0 - a*0.6)
            self.top_zone.configure(fg_color=pulse_bg)
        if self.bot_zone.stage == "done":
            pulse_bg = _blend(self.c["bg_red"], self.c["zone_bg"], 1.0 - a*0.6)
            self.bot_zone.configure(fg_color=pulse_bg)
        # Removed pulsing background effect - keep window background constant
        self.after(40, self._pulse_loop)

    def _blink_loop(self):
        if not self._clock_running: return
        self._colon_visible = not self._colon_visible
        # Colon blinking disabled - keep it always visible
        # col = self.c["text_sub"] if self._colon_visible else _blend(self.c["text_sub"],self.c["zone_bg"],0.9)
        # for z in (self.top_zone, self.bot_zone):
        #     if z.stage not in ("done",): z.lbl_col.configure(text_color=col)
        self.after(500, self._blink_loop)


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_default_color_theme("blue")
    app = PodcastTimerApp()
    app.mainloop()
