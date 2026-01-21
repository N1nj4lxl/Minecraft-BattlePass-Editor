import os
import re
import random
import tkinter as tk
from tkinter import ttk, filedialog
import yaml

# =========================
# THEME
# =========================
BG = "#141414"
PANEL = "#1b1b1f"
PANEL2 = "#22222a"
TEXT = "#e8e8ee"
MUTED = "#a9a9b3"
ACCENT = "#c46bff"      # dark pink/purple hint
ACCENT2 = "#7a2cff"
FREE_COL = "#3f9cff"    # blue
PREM_COL = "#d4af37"    # gold
BAD = "#ff6b6b"
GOOD = "#4ee38a"

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_H = ("Segoe UI", 12, "bold")


# =========================
# YAML HELPERS
# =========================
def safe_load_yaml(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def safe_dump_yaml(path: str, data: dict):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            width=120,
            default_flow_style=False,
        )


def ensure_dict(v):
    return v if isinstance(v, dict) else {}


def ensure_list(v):
    return v if isinstance(v, list) else []


def numeric_sort_key(x):
    try:
        return int(str(x))
    except Exception:
        return 10**9


def next_numeric_string_id(existing_keys):
    nums = []
    for k in existing_keys:
        try:
            nums.append(int(str(k)))
        except Exception:
            continue
    return str(max(nums) + 1 if nums else 1)


def deep_copy(obj):
    return yaml.safe_load(yaml.safe_dump(obj))


def split_lines(text: str):
    out = []
    for ln in (text or "").splitlines():
        ln = ln.rstrip("\r")
        if ln.strip() == "":
            continue
        out.append(ln)
    return out


def join_lines(lines):
    return "\n".join(lines or [])


def parse_kv_lines(lines):
    m = {}
    for ln in lines:
        if "=" in ln:
            k, v = ln.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k:
                m[k] = v
    return m


def kv_to_lines(m):
    out = []
    for k, v in (m or {}).items():
        out.append(f"{k}={v}")
    return out


# =========================
# GENERATORS
# =========================
MATERIALS = [
    "diamond:0",
    "emerald:0",
    "gold_ingot:0",
    "iron_ingot:0",
    "netherite_ingot:0",
    "totem_of_undying:0",
    "enchanted_golden_apple:0",
    "ender_pearl:0",
    "diamond_sword:0",
    "diamond_pickaxe:0",
    "diamond_chestplate:0",
    "shulker_box:0",
    "elytra:0",
    "trident:0",
    "experience_bottle:0",
    "golden_apple:0",
    "netherite_sword:0",
    "netherite_pickaxe:0",
    "bow:0",
    "crossbow:0",
    "arrow:0",
]

MOBS = ["zombie", "skeleton", "creeper", "spider", "enderman", "witch", "slime", "pillager", "guardian", "blaze"]
BLOCKS = ["stone", "coal_ore", "iron_ore", "diamond_ore", "oak_log", "sand", "netherrack", "obsidian", "deepslate"]
FISH = ["cod", "salmon", "tropical_fish", "pufferfish"]


def gen_reward_command():
    name = random.choice(["Starter Bundle", "Lucky Key", "Cash Drop", "VIP Boost", "Supply Crate", "Charm Pack"])
    cmd_templates = [
        "give %player% diamond {amt}",
        "eco give %player% {money}",
        "lp user %player% permission settemp battlepass.boost.{n} true {dur}d",
        "crate key give %player% {key} {amt}",
        "minecraft:give %player% experience_bottle {amt}",
    ]
    cmd = random.choice(cmd_templates).format(
        amt=random.choice([1, 2, 3, 5, 8, 16]),
        money=random.choice([250, 500, 750, 1000, 1500, 2000]),
        n=random.choice([1, 2, 3]),
        dur=random.choice([1, 3, 7, 14]),
        key=random.choice(["basic", "rare", "epic"]),
    )
    return {"name": name, "type": "command", "commands": [cmd], "lore-addon": ["&7Auto-generated reward."]}


def gen_reward_item():
    mat = random.choice(MATERIALS)
    amt = random.choice([1, 1, 2, 3, 5, 8, 16])
    name = random.choice(["Loot Pack", "Miner Kit", "PvP Kit", "Explorer Bundle", "Treasure Drop", "Supply Cache"])
    lore = [
        "&7Auto-generated item reward.",
        "&7Contains: &f{0}x &f{1}".format(amt, mat.split(":")[0].replace("_", " ").title()),
    ]
    item = {"material": mat, "amount": amt, "name": "&b" + name, "lore": lore}
    if random.random() < 0.25:
        item["glow"] = True
    return {"name": name, "type": "item", "items": {"1": item}, "lore-addon": ["&7Auto-generated reward."]}


def gen_reward_money():
    name = random.choice(["Coins", "Pouch of Coins", "Gold Stash", "Bank Transfer"])
    val = random.choice([250, 500, 750, 1000, 1500, 2000])
    return {"name": name, "type": "money", "value": val, "lore-addon": ["&7Auto-generated reward."]}


def gen_random_reward():
    pick = random.random()
    if pick < 0.45:
        return gen_reward_command()
    if pick < 0.85:
        return gen_reward_item()
    return gen_reward_money()


def gen_random_quest():
    qtype = random.choice(["block-break", "kill-mob", "fish", "craft-item"])
    if qtype == "kill-mob":
        mob = random.choice(MOBS)
        need = random.choice([5, 10, 15, 20, 25, 30])
        points = random.choice([10, 15, 20, 25, 30])
        name = "&eKill &f{0} &e{1}".format(need, mob.replace("_", " ").title())
        variable = mob
        item_mat = "iron_sword:0"
    elif qtype == "block-break":
        blk = random.choice(BLOCKS)
        need = random.choice([16, 32, 64, 128])
        points = random.choice([10, 15, 20, 25])
        name = "&eMine &f{0} &e{1}".format(need, blk.replace("_", " ").title())
        variable = blk
        item_mat = "diamond_pickaxe:0"
    elif qtype == "fish":
        fish = random.choice(FISH)
        need = random.choice([5, 10, 15, 20])
        points = random.choice([10, 15, 20, 25])
        name = "&eCatch &f{0} &e{1}".format(need, fish.replace("_", " ").title())
        variable = fish
        item_mat = "fishing_rod:0"
    else:
        mat = random.choice(["bread", "torch", "iron_pickaxe", "diamond_sword", "golden_apple"])
        need = random.choice([4, 8, 16, 24, 32])
        points = random.choice([10, 15, 20, 25, 30])
        name = "&eCraft &f{0} &e{1}".format(need, mat.replace("_", " ").title())
        variable = mat
        item_mat = "crafting_table:0"

    lore = [
        "&7Progress: &f%progress_bar% &7(&f%percentage_progress%%&7)",
        "&7Progress: &f%progress%&7/&f%required_progress%",
        "",
        "&7Points: &f%points%",
    ]
    return {
        "name": name,
        "type": qtype,
        "variable": variable,
        "required-progress": int(need),
        "points": int(points),
        "item": {"material": item_mat, "name": name, "lore": lore},
    }


# =========================
# EMOJIS (REWARD)
# =========================
def reward_emoji(reward: dict) -> str:
    r = ensure_dict(reward)
    t = str(r.get("type", "")).lower()
    name = str(r.get("name", "")).lower()

    if t == "money":
        return "💰"
    if t == "command":
        if "crate" in name or "key" in name or "supply" in name:
            return "📦"
        if "boost" in name or "vip" in name:
            return "⭐"
        if "cash" in name or "coin" in name or "gold" in name:
            return "💰"
        return "⚙️"
    if t == "item":
        items = ensure_dict(r.get("items", {}))
        it = ensure_dict(items.get("1", {}))
        mat = str(it.get("material", "")).lower()
        if "sword" in mat or "axe" in mat:
            return "🗡️"
        if "pickaxe" in mat or "shovel" in mat or "hoe" in mat:
            return "⛏️"
        if "chestplate" in mat or "helmet" in mat or "leggings" in mat or "boots" in mat:
            return "🛡️"
        if "elytra" in mat:
            return "🪽"
        if "totem" in mat:
            return "🗿"
        if "apple" in mat:
            return "🍎"
        if "pearl" in mat:
            return "🧿"
        return "🎁"
    return "🎁"


# =========================
# TOOLTIP
# =========================
class Tooltip:
    def __init__(self, widget):
        self.widget = widget
        self.tip = None

    def show(self, text, x, y):
        if self.tip:
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.overrideredirect(True)
        self.tip.configure(bg=PANEL2)
        lbl = tk.Label(
            self.tip,
            text=text,
            bg=PANEL2,
            fg=TEXT,
            font=FONT,
            justify="left",
            padx=10,
            pady=8,
        )
        lbl.pack()
        self.tip.geometry(f"+{x+12}+{y+12}")

    def hide(self):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# =========================
# SCROLLABLE FRAME
# =========================
class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=BG)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.inner = ttk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)
        self.canvas.bind_all("<MouseWheel>", self._on_wheel, add="+")

    def _on_inner(self, _e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, e):
        self.canvas.itemconfigure(self.inner_id, width=e.width)

    def _on_wheel(self, e):
        try:
            self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        except Exception:
            pass


# =========================
# MAIN APP
# =========================
class BattlePassStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BattlePass Studio")
        self.geometry("1550x860")
        self.minsize(1400, 780)

        self._apply_style()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.state = {
            "free": {},
            "premium": {},
            "rewards": {},
            "quests": {},
            "quests_path": "",
            "week_pool": {},
            "week_pool_path": "",
        }
        self.dirty = {"free": False, "premium": False, "rewards": False, "quests": False, "week_pool": False}

        self.status_var = tk.StringVar(value="Ready.")
        self.mode_tab = tk.StringVar(value="Rewards")

        # Required UI state vars (were missing in your current build)
        self.mode_var = tk.StringVar(value="battlepass")
        self.track_var = tk.StringVar(value="free")

        self.path_free = tk.StringVar(value=self._autodetect_in_dir("free.yml"))
        self.path_premium = tk.StringVar(value=self._autodetect_in_dir("premium.yml"))
        self.path_rewards = tk.StringVar(value=self._autodetect_in_dir("rewards.yml"))
        self.path_quests = tk.StringVar(value=self._autodetect_any_quest_file())
        self.path_week_pool = tk.StringVar(value=self._autodetect_in_dir("week-pool.yml"))

        self._build_ui()
        self.reload_all()

    # -------------------------
    # STYLE
    # -------------------------
    def _apply_style(self):
        self.configure(bg=BG)
        style = ttk.Style(self)
        style.theme_use("default")

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=FONT)
        style.configure("TLabelframe", background=BG, foreground=TEXT)
        style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=FONT_B)

        style.configure("TButton", background=PANEL, foreground=TEXT, padding=8, font=FONT)
        style.map("TButton", background=[("active", ACCENT2)])

        style.configure("TEntry", fieldbackground=PANEL2, foreground=TEXT, borderwidth=0)
        style.configure("TCombobox", fieldbackground=PANEL2, foreground=TEXT)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL2)], foreground=[("readonly", TEXT)])

        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=24, borderwidth=0)
        style.configure("Treeview.Heading", background=PANEL2, foreground=TEXT, font=FONT_B)
        style.map("Treeview", background=[("selected", ACCENT2)])

        self.option_add("*Text.background", PANEL)
        self.option_add("*Text.foreground", TEXT)
        self.option_add("*Text.insertBackground", TEXT)
        self.option_add("*Text.font", FONT)
        self.option_add("*Listbox.background", PANEL)
        self.option_add("*Listbox.foreground", TEXT)
        self.option_add("*Listbox.selectBackground", ACCENT2)
        self.option_add("*Listbox.selectForeground", TEXT)

    # -------------------------
    # AUTODETECT
    # -------------------------
    def _autodetect_in_dir(self, filename):
        p = os.path.join(self.base_dir, filename)
        return p if os.path.exists(p) else os.path.join(self.base_dir, filename)

    def _autodetect_any_quest_file(self):
        candidates = []
        for fn in os.listdir(self.base_dir):
            if not fn.lower().endswith(".yml"):
                continue
            low = fn.lower()
            if low in ("free.yml", "premium.yml", "rewards.yml", "settings.yml"):
                continue
            if "quest" in low or low.startswith("week-") or low.startswith("daily-") or low.startswith("event-"):
                candidates.append(os.path.join(self.base_dir, fn))
        candidates.sort(key=lambda p: os.path.basename(p).lower())
        return candidates[0] if candidates else os.path.join(self.base_dir, "week-1-quests.yml")

    def _scan_quest_files(self):
        out = []
        for fn in os.listdir(self.base_dir):
            if fn.lower().endswith(".yml"):
                low = fn.lower()
                if low in ("free.yml", "premium.yml", "rewards.yml", "settings.yml"):
                    continue
                if "quest" in low or low.startswith("week-") or low.startswith("daily-") or low.startswith("event-"):
                    out.append(os.path.join(self.base_dir, fn))
        out.sort(key=lambda p: os.path.basename(p).lower())
        return out

    # -------------------------
    # UI
    # -------------------------
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        root = ttk.Frame(self)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        paned = ttk.Panedwindow(root, orient="horizontal")
        paned.grid(row=0, column=0, sticky="nsew")

        self.left = ttk.Frame(paned, width=340)
        self.middle = ttk.Frame(paned)
        self.right = ttk.Frame(paned, width=520)

        paned.add(self.left, weight=0)
        paned.add(self.middle, weight=1)
        paned.add(self.right, weight=0)

        self._build_left()
        self._build_middle()
        self._build_right()

        status = ttk.Frame(root)
        status.grid(row=1, column=0, sticky="ew")
        status.grid_columnconfigure(0, weight=1)
        ttk.Label(status, textvariable=self.status_var).grid(row=0, column=0, sticky="ew", padx=12, pady=8)

    def _build_left(self):
        self.left.grid_rowconfigure(99, weight=1)
        title = ttk.Label(self.left, text="BattlePass Studio", font=FONT_H)
        title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        lf_files = ttk.Labelframe(self.left, text="Files (Auto-detect in this folder)")
        lf_files.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        lf_files.grid_columnconfigure(0, weight=1)

        self._file_row(lf_files, 0, "free.yml", self.path_free, lambda: self._pick_file(self.path_free))
        self._file_row(lf_files, 2, "premium.yml", self.path_premium, lambda: self._pick_file(self.path_premium))
        self._file_row(lf_files, 4, "rewards.yml", self.path_rewards, lambda: self._pick_file(self.path_rewards))

        self.quest_files = self._scan_quest_files()
        quest_names = [os.path.basename(p) for p in self.quest_files] or [os.path.basename(self.path_quests.get())]
        ttk.Label(lf_files, text="Quest file").grid(row=6, column=0, sticky="w", padx=10, pady=(8, 2))
        self.cb_quests = ttk.Combobox(lf_files, values=quest_names, state="readonly")
        self.cb_quests.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 6))
        if quest_names:
            try:
                idx = quest_names.index(os.path.basename(self.path_quests.get()))
            except Exception:
                idx = 0
            self.cb_quests.current(idx)
        self.cb_quests.bind("<<ComboboxSelected>>", self._on_select_quest_file)

        self._file_row(lf_files, 8, "week-pool.yml (optional)", self.path_week_pool, lambda: self._pick_file(self.path_week_pool))

        actions = ttk.Labelframe(self.left, text="Actions")
        actions.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        ttk.Button(actions, text="Reload", command=self.reload_all).grid(row=0, column=0, sticky="ew", padx=(10, 6), pady=10)
        ttk.Button(actions, text="Save", command=self.save_all).grid(row=0, column=1, sticky="ew", padx=(6, 10), pady=10)

        ttk.Button(actions, text="Random Generate (Current Tab)", command=self.random_generate_current_tab).grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10)
        )

        self.dirty_var = tk.StringVar(value="Unsaved: none")
        ttk.Label(self.left, textvariable=self.dirty_var, foreground=MUTED).grid(row=3, column=0, sticky="w", padx=12, pady=(0, 10))

    def _file_row(self, parent, r, label, var, pick_cmd):
        parent.grid_columnconfigure(0, weight=1)
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", padx=10, pady=(8, 2))
        row = ttk.Frame(parent)
        row.grid(row=r + 1, column=0, sticky="ew", padx=10, pady=(0, 2))
        row.grid_columnconfigure(0, weight=1)
        ttk.Entry(row, textvariable=var).grid(row=0, column=0, sticky="ew")
        ttk.Button(row, text="Pick", command=pick_cmd, width=8).grid(row=0, column=1, sticky="e", padx=(8, 0))

    def _build_middle(self):
        self.middle.grid_rowconfigure(0, weight=1)
        self.middle.grid_columnconfigure(0, weight=1)

        self.nb = ttk.Notebook(self.middle)
        self.nb.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.tab_rewards = ttk.Frame(self.nb)
        self.tab_tiers = ttk.Frame(self.nb)
        self.tab_quests = ttk.Frame(self.nb)

        self.nb.add(self.tab_rewards, text="Rewards")
        self.nb.add(self.tab_tiers, text="Tiers")
        self.nb.add(self.tab_quests, text="Quests")

        self._build_rewards_tab()
        self._build_tiers_tab()
        self._build_quests_tab()

    def _build_right(self):
        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_columnconfigure(0, weight=1)

        lf = ttk.Labelframe(self.right, text="BattlePass Preview")
        lf.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(lf, bg=BG, highlightthickness=0, bd=0, height=380)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.preview_scroll = ttk.Scrollbar(lf, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_scroll.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 10))
        self.preview_canvas.configure(xscrollcommand=self.preview_scroll.set)

        self.tooltip = Tooltip(self.preview_canvas)

        self.preview_hint = ttk.Label(lf, text="Hover tiles for rewards. Free is blue, Premium is gold.", foreground=MUTED)
        self.preview_hint.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 10))

    # -------------------------
    # STATUS / DIRTY
    # -------------------------
    def set_status(self, msg: str):
        self.status_var.set(msg)

    def mark_dirty(self, key: str, dirty=True):
        self.dirty[key] = bool(dirty)
        keys = [k for k, v in self.dirty.items() if v]
        self.dirty_var.set("Unsaved: " + (", ".join(keys) if keys else "none"))

    # -------------------------
    # FILE PICK
    # -------------------------
    def _pick_file(self, var: tk.StringVar):
        path = filedialog.askopenfilename(initialdir=self.base_dir, filetypes=[("YAML", "*.yml")])
        if path:
            var.set(path)
            self.set_status("Path updated. Reload to apply.")

    def _on_select_quest_file(self, _e=None):
        names = [os.path.basename(p) for p in self.quest_files]
        sel = self.cb_quests.get().strip()
        if sel in names:
            idx = names.index(sel)
            self.path_quests.set(self.quest_files[idx])
            self.set_status(f"Selected quest file: {sel}. Reload to apply.")

    # -------------------------
    # LOAD / SAVE
    # -------------------------
    def reload_all(self):
        try:
            self.state["free"] = safe_load_yaml(self.path_free.get())
            self.state["premium"] = safe_load_yaml(self.path_premium.get())
            self.state["rewards"] = safe_load_yaml(self.path_rewards.get())

            qp = self.path_quests.get()
            self.state["quests_path"] = qp
            self.state["quests"] = safe_load_yaml(qp)

            wp = self.path_week_pool.get()
            self.state["week_pool_path"] = wp
            self.state["week_pool"] = safe_load_yaml(wp)

            for k in self.dirty:
                self.mark_dirty(k, False)

            self._refresh_rewards_list()
            self._tiers_refresh_list()
            self._quests_refresh_list()
            self._render_preview()

            self.set_status("Loaded.")
        except Exception as e:
            self.set_status(f"Load error: {e}")

    def save_all(self):
        try:
            if self.dirty.get("free"):
                safe_dump_yaml(self.path_free.get(), ensure_dict(self.state["free"]))
                self.mark_dirty("free", False)
            if self.dirty.get("premium"):
                safe_dump_yaml(self.path_premium.get(), ensure_dict(self.state["premium"]))
                self.mark_dirty("premium", False)
            if self.dirty.get("rewards"):
                safe_dump_yaml(self.path_rewards.get(), ensure_dict(self.state["rewards"]))
                self.mark_dirty("rewards", False)
            if self.dirty.get("quests"):
                safe_dump_yaml(self.state.get("quests_path") or self.path_quests.get(), ensure_dict(self.state["quests"]))
                self.mark_dirty("quests", False)
            if self.dirty.get("week_pool"):
                safe_dump_yaml(self.state.get("week_pool_path") or self.path_week_pool.get(), ensure_dict(self.state["week_pool"]))
                self.mark_dirty("week_pool", False)

            self.set_status("Saved.")
        except Exception as e:
            self.set_status(f"Save error: {e}")

    # -------------------------
    # TAB CHANGED
    # -------------------------
    def _on_tab_changed(self, _e=None):
        try:
            txt = self.nb.tab(self.nb.select(), "text")
            self.mode_tab.set(txt)
        except Exception:
            pass

    def random_generate_current_tab(self):
        tab = self.mode_tab.get()
        if tab == "Rewards":
            self._reward_random()
        elif tab == "Tiers":
            self._tier_add_random_reward_to_selected()
        elif tab == "Quests":
            self._quest_add_random()
        else:
            self.set_status("Nothing to generate.")

    # =========================
    # REWARDS TAB
    # =========================
    def _build_rewards_tab(self):
        self.tab_rewards.grid_rowconfigure(0, weight=1)
        self.tab_rewards.grid_columnconfigure(0, weight=1)
        self.tab_rewards.grid_columnconfigure(1, weight=1)

        left = ttk.Labelframe(self.tab_rewards, text="Rewards List")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        self.tv_rewards = ttk.Treeview(left, columns=("id", "name", "type"), show="headings", height=18)
        self.tv_rewards.heading("id", text="ID")
        self.tv_rewards.heading("name", text="NAME")
        self.tv_rewards.heading("type", text="TYPE")
        self.tv_rewards.column("id", width=60, stretch=False)
        self.tv_rewards.column("name", width=220, stretch=True)
        self.tv_rewards.column("type", width=110, stretch=False)
        self.tv_rewards.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tv_rewards.bind("<<TreeviewSelect>>", self._on_reward_select)

        btn = ttk.Frame(left)
        btn.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        for i in range(5):
            btn.grid_columnconfigure(i, weight=1)

        ttk.Button(btn, text="Add", command=self._reward_add).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btn, text="Duplicate", command=self._reward_duplicate).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Button(btn, text="Delete", command=self._reward_delete).grid(row=0, column=2, sticky="ew", padx=(0, 6))
        ttk.Button(btn, text="Random", command=self._reward_random).grid(row=0, column=3, sticky="ew", padx=(0, 6))
        ttk.Button(btn, text="Apply", command=self._reward_apply).grid(row=0, column=4, sticky="ew")

        right = ttk.Labelframe(self.tab_rewards, text="Reward Editor")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        sc = ScrollableFrame(right)
        sc.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        sc.inner.grid_columnconfigure(1, weight=1)

        self.reward_id_var = tk.StringVar()
        self.reward_name_var = tk.StringVar()
        self.reward_type_var = tk.StringVar(value="command")

        ttk.Label(sc.inner, text="ID").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(sc.inner, textvariable=self.reward_id_var, state="readonly").grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(sc.inner, text="Name").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(sc.inner, textvariable=self.reward_name_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(sc.inner, text="Type").grid(row=2, column=0, sticky="w", pady=2)
        cb = ttk.Combobox(sc.inner, textvariable=self.reward_type_var, values=["command", "item", "money"], state="readonly")
        cb.grid(row=2, column=1, sticky="ew", pady=2)
        cb.bind("<<ComboboxSelected>>", lambda _e: self._reward_switch_type())

        ttk.Label(sc.inner, text="Lore Addon (one per line)").grid(row=3, column=0, sticky="nw", pady=(10, 2))
        self.txt_reward_loreaddon = tk.Text(sc.inner, height=4, wrap="word")
        self.txt_reward_loreaddon.grid(row=3, column=1, sticky="ew", pady=(10, 2))

        ttk.Label(sc.inner, text="Variables (key=value per line)").grid(row=4, column=0, sticky="nw", pady=(10, 2))
        self.txt_reward_vars = tk.Text(sc.inner, height=4, wrap="word")
        self.txt_reward_vars.grid(row=4, column=1, sticky="ew", pady=(10, 2))

        self.reward_type_stack = ttk.Frame(sc.inner)
        self.reward_type_stack.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 2))
        self.reward_type_stack.grid_columnconfigure(0, weight=1)

        self.fr_cmd = ttk.Labelframe(self.reward_type_stack, text="Commands (one per line)")
        self.fr_item = ttk.Labelframe(self.reward_type_stack, text="Item Editor (items['1'])")
        self.fr_money = ttk.Labelframe(self.reward_type_stack, text="Money")

        for fr in (self.fr_cmd, self.fr_item, self.fr_money):
            fr.grid(row=0, column=0, sticky="ew")
            fr.grid_columnconfigure(0, weight=1)

        self.txt_reward_cmds = tk.Text(self.fr_cmd, height=7, wrap="word")
        self.txt_reward_cmds.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.item_material_var = tk.StringVar()
        self.item_amount_var = tk.StringVar(value="1")
        self.item_dispname_var = tk.StringVar()
        self.item_glow_var = tk.BooleanVar(value=False)

        f = ttk.Frame(self.fr_item)
        f.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        f.grid_columnconfigure(1, weight=1)

        ttk.Label(f, text="Material (e.g. diamond:0)").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=2)
        ttk.Entry(f, textvariable=self.item_material_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(f, text="Amount").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=2)
        ttk.Entry(f, textvariable=self.item_amount_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(f, text="Name").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=2)
        ttk.Entry(f, textvariable=self.item_dispname_var).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Checkbutton(f, text="Glow", variable=self.item_glow_var).grid(row=3, column=1, sticky="w", pady=(6, 2))

        ttk.Label(self.fr_item, text="Lore (one per line)").grid(row=1, column=0, sticky="w", padx=10)
        self.txt_item_lore = tk.Text(self.fr_item, height=6, wrap="word")
        self.txt_item_lore.grid(row=2, column=0, sticky="ew", padx=10, pady=(2, 10))

        self.money_value_var = tk.StringVar(value="0")
        m = ttk.Frame(self.fr_money)
        m.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        m.grid_columnconfigure(1, weight=1)
        ttk.Label(m, text="Value").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(m, textvariable=self.money_value_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(sc.inner, text="Advanced YAML (optional, overrides editor when applied)").grid(row=6, column=0, sticky="nw", pady=(10, 2))
        self.txt_reward_yaml = tk.Text(sc.inner, height=10, wrap="word")
        self.txt_reward_yaml.grid(row=6, column=1, sticky="ew", pady=(10, 2))

        adv_btn = ttk.Frame(sc.inner)
        adv_btn.grid(row=7, column=1, sticky="e", pady=(2, 8))
        ttk.Button(adv_btn, text="Apply YAML", command=self._reward_apply_yaml).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(adv_btn, text="Revert", command=self._reward_revert).grid(row=0, column=1)

        self._reward_switch_type()

    def _rewards_dict(self):
        return ensure_dict(self.state.get("rewards", {}))

    def _refresh_rewards_list(self):
        self.tv_rewards.delete(*self.tv_rewards.get_children())
        rewards = self._rewards_dict()
        keys = sorted(rewards.keys(), key=numeric_sort_key)
        for rid in keys:
            r = ensure_dict(rewards.get(rid, {}))
            self.tv_rewards.insert("", "end", iid=str(rid), values=(str(rid), str(r.get("name", "")), str(r.get("type", ""))))

    def _on_reward_select(self, _e=None):
        rid = self._tv_selected(self.tv_rewards)
        if not rid:
            return
        r = ensure_dict(self._rewards_dict().get(str(rid), {}))
        self._reward_load_editor(str(rid), r)

    def _reward_load_editor(self, rid: str, r: dict):
        self.reward_id_var.set(rid)
        self.reward_name_var.set(str(r.get("name", "")))
        self.reward_type_var.set(str(r.get("type", "command")).lower() or "command")
        self._reward_switch_type()

        self._set_text(self.txt_reward_loreaddon, join_lines(ensure_list(r.get("lore-addon", []))))
        self._set_text(self.txt_reward_vars, join_lines(kv_to_lines(ensure_dict(r.get("variables", {})))))

        t = self.reward_type_var.get()
        if t == "command":
            self._set_text(self.txt_reward_cmds, join_lines(ensure_list(r.get("commands", []))))
        elif t == "item":
            items = ensure_dict(r.get("items", {}))
            it = ensure_dict(items.get("1", {}))
            self.item_material_var.set(str(it.get("material", "")))
            self.item_amount_var.set(str(it.get("amount", "1")))
            self.item_dispname_var.set(str(it.get("name", "")))
            self.item_glow_var.set(bool(it.get("glow", False)))
            self._set_text(self.txt_item_lore, join_lines(ensure_list(it.get("lore", []))))
        elif t == "money":
            self.money_value_var.set(str(r.get("value", "0")))

        self._set_text(self.txt_reward_yaml, yaml.safe_dump(r, sort_keys=False))

    def _reward_switch_type(self):
        t = self.reward_type_var.get().strip().lower()
        self.fr_cmd.grid_remove()
        self.fr_item.grid_remove()
        self.fr_money.grid_remove()
        if t == "item":
            self.fr_item.grid()
        elif t == "money":
            self.fr_money.grid()
        else:
            self.fr_cmd.grid()

    def _reward_add(self):
        rewards = self._rewards_dict()
        rid = next_numeric_string_id(rewards.keys())
        rewards[rid] = {"name": "New Reward", "type": "command", "commands": ["say %player% got a reward!"]}
        self.state["rewards"] = rewards
        self.mark_dirty("rewards", True)
        self._refresh_rewards_list()
        self._select_iid(self.tv_rewards, rid)
        self.set_status(f"Added reward {rid}.")
        self._render_preview()

    def _reward_duplicate(self):
        rid = self._tv_selected(self.tv_rewards)
        if not rid:
            self.set_status("Select a reward to duplicate.")
            return
        rewards = self._rewards_dict()
        src = ensure_dict(rewards.get(str(rid), {}))
        new_id = next_numeric_string_id(rewards.keys())
        rewards[new_id] = deep_copy(src)
        rewards[new_id]["name"] = str(rewards[new_id].get("name", "Reward")) + " (Copy)"
        self.state["rewards"] = rewards
        self.mark_dirty("rewards", True)
        self._refresh_rewards_list()
        self._select_iid(self.tv_rewards, new_id)
        self.set_status(f"Duplicated reward {rid} -> {new_id}.")
        self._render_preview()

    def _reward_delete(self):
        # Delete selected reward (only if not referenced by any tier)
        rid = None

        # Support both helper styles (older/newer versions of this file)
        if hasattr(self, "_tv_selected_iid"):
            rid = self._tv_selected_iid(self.tv_rewards)
        elif hasattr(self, "_tv_selected"):
            rid = self._tv_selected(self.tv_rewards)

        if not rid:
            self.set_status("Select a reward to delete.")
            return

        rid = str(rid)

        if hasattr(self, "_reward_is_referenced") and self._reward_is_referenced(rid):
            self.set_status(f"Cannot delete reward {rid}: referenced by a tier.")
            return

        # Get rewards dict (support both naming styles)
        if hasattr(self, "_reward_list_dict"):
            rewards = self._reward_list_dict()
        elif hasattr(self, "_rewards_dict"):
            rewards = self._rewards_dict()
        else:
            rewards = dict(self.state.get("rewards", {}) or {})

        rewards.pop(rid, None)
        self.state["rewards"] = rewards

        if hasattr(self, "mark_dirty"):
            self.mark_dirty("rewards", True)

        # Refresh list UI (support both naming styles)
        if hasattr(self, "_reward_refresh_list"):
            self._reward_refresh_list()
        elif hasattr(self, "_refresh_rewards_list"):
            self._refresh_rewards_list()

        if hasattr(self, "_reward_clear_editor"):
            self._reward_clear_editor()

        self.set_status(f"Deleted reward {rid}.")

        # Re-render previews if present
        if hasattr(self, "_render_preview"):
            self._render_preview()
        elif hasattr(self, "refresh_all_views"):
            self.refresh_all_views()

    def _reward_random(self):
        # Random-generate a reward and add it to rewards.yml data
        # Get rewards dict (support both naming styles)
        if hasattr(self, "_reward_list_dict"):
            rewards = self._reward_list_dict()
        elif hasattr(self, "_rewards_dict"):
            rewards = self._rewards_dict()
        else:
            rewards = dict(self.state.get("rewards", {}) or {})

        # Choose a new numeric ID
        if "next_numeric_string_id" in globals():
            new_id = next_numeric_string_id(rewards.keys())
        else:
            # Fallback if helper is missing
            used = set()
            for k in rewards.keys():
                try:
                    used.add(int(str(k)))
                except Exception:
                    pass
            n = 1
            while n in used:
                n += 1
            new_id = str(n)

        # Generate reward payload
        if "gen_random_reward" in globals():
            rewards[new_id] = gen_random_reward()
        else:
            # Safe fallback if generator is missing
            rewards[new_id] = {
                "name": "Random Reward",
                "type": "command",
                "commands": ["say %player% got a random reward!"]
            }

        self.state["rewards"] = rewards

        if hasattr(self, "mark_dirty"):
            self.mark_dirty("rewards", True)

        # Refresh list UI (support both naming styles)
        if hasattr(self, "_reward_refresh_list"):
            self._reward_refresh_list()
        elif hasattr(self, "_refresh_rewards_list"):
            self._refresh_rewards_list()

        # Select new row
        try:
            self.tv_rewards.selection_set(new_id)
            self.tv_rewards.see(new_id)
        except Exception:
            pass

        self.set_status(f"Random-generated reward {new_id}.")

        if hasattr(self, "_render_preview"):
            self._render_preview()
        elif hasattr(self, "refresh_all_views"):
            self.refresh_all_views()

    def _reward_apply(self):
        rid = self.reward_id_var.get().strip()
        if not rid:
            self.set_status("Select a reward first.")
            return

        rewards = self._reward_list_dict()
        if rid not in rewards:
            rewards[rid] = {}
        r = ensure_dict(rewards.get(rid, {}))

        r["name"] = self.reward_name_var.get().strip() or "Reward"
        r["type"] = self.reward_type_var.get().strip().lower() or "command"

        r["lore-addon"] = split_lines(self._get_text(self.txt_reward_loreaddon))

        vars_lines = split_lines(self._get_text(self.txt_reward_vars))
        vars_map = {}
        for ln in vars_lines:
            if "=" in ln:
                k, v = ln.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k:
                    vars_map[k] = v
        if vars_map:
            r["variables"] = vars_map
        else:
            r.pop("variables", None)

        t = r["type"]
        if t == "command":
            r["commands"] = split_lines(self._get_text(self.txt_reward_cmds))
            r.pop("items", None)
            r.pop("value", None)

        elif t == "item":
            mat = self.item_material_var.get().strip()
            amt_raw = self.item_amount_var.get().strip()
            try:
                amt = int(amt_raw)
            except Exception:
                amt = 1

            nm = self.item_dispname_var.get().strip()
            lore = split_lines(self._get_text(self.txt_item_lore))

            it = {}
            if mat:
                it["material"] = mat
            it["amount"] = max(1, amt)
            if nm:
                it["name"] = nm
            if lore:
                it["lore"] = lore
            if bool(self.item_glow_var.get()):
                it["glow"] = True

            items = ensure_dict(r.get("items", {}))
            items["1"] = it
            r["items"] = items

            r.pop("commands", None)
            r.pop("value", None)

        elif t == "money":
            val_raw = self.money_value_var.get().strip()
            try:
                val = int(val_raw)
            except Exception:
                val = 0
            r["value"] = val

            r.pop("commands", None)
            r.pop("items", None)

        rewards[rid] = r
        self.state["rewards"] = rewards
        self.mark_dirty("rewards", True)

        self._reward_refresh_list()
        try:
            self.tv_rewards.selection_set(rid)
            self.tv_rewards.see(rid)
        except Exception:
            pass

        self.set_status(f"Applied changes to reward {rid}.")
        self.refresh_all_views()


    def _reward_revert(self):
        sel = self._tv_selected_iid(self.tv_rewards)
        if not sel:
            self.set_status("Select a reward first.")
            return
        rid = str(sel)
        rewards = self._reward_list_dict()
        r = ensure_dict(rewards.get(rid, {}))
        self._reward_load_into_editor(rid, r)
        try:
            self._set_text(self.txt_reward_yaml, yaml.safe_dump(r, sort_keys=False, allow_unicode=True))
        except Exception:
            pass
        self.set_status(f"Reverted editor to reward {rid} from memory.")


    def _reward_apply_yaml(self):
        rid = self.reward_id_var.get().strip()
        if not rid:
            self.set_status("Select a reward first.")
            return

        raw = self._get_text(self.txt_reward_yaml).strip()
        if not raw:
            self.set_status("YAML box is empty.")
            return

        try:
            parsed = yaml.safe_load(raw)
        except Exception as e:
            self.set_status(f"YAML error: {e}")
            return

        if not isinstance(parsed, dict):
            self.set_status("YAML must be a mapping (key: value).")
            return

        rewards = self._reward_list_dict()
        rewards[rid] = parsed
        self.state["rewards"] = rewards
        self.mark_dirty("rewards", True)

        self._reward_refresh_list()
        try:
            self.tv_rewards.selection_set(rid)
            self.tv_rewards.see(rid)
        except Exception:
            pass

        self._reward_load_into_editor(rid, ensure_dict(parsed))
        self.set_status(f"Applied YAML to reward {rid}.")
        self.refresh_all_views()

    def _build_tiers_tab(self):
        self.tab_tiers.grid_rowconfigure(0, weight=1)
        self.tab_tiers.grid_columnconfigure(0, weight=1)
        self.tab_tiers.grid_columnconfigure(1, weight=1)

        left = ttk.Labelframe(self.tab_tiers, text="Tiers")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        top = ttk.Frame(left)
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
        ttk.Label(top, text="Track").grid(row=0, column=0, sticky="w", padx=(0, 8))
        cb = ttk.Combobox(top, textvariable=self.track_var, values=["free", "premium"], state="readonly")
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda _e: self._tiers_refresh_list())

        cols = ("tier", "required", "rewards")
        self.tv_tiers = ttk.Treeview(left, columns=cols, show="headings", height=18)
        self.tv_tiers.heading("tier", text="TIER")
        self.tv_tiers.heading("required", text="REQ POINTS")
        self.tv_tiers.heading("rewards", text="REWARDS")
        self.tv_tiers.column("tier", width=70, stretch=False)
        self.tv_tiers.column("required", width=110, stretch=False)
        self.tv_tiers.column("rewards", width=260, stretch=True)
        self.tv_tiers.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.tv_tiers.bind("<<TreeviewSelect>>", self._on_tier_select)

        btnrow = ttk.Frame(left)
        btnrow.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        for i in range(4):
            btnrow.grid_columnconfigure(i, weight=1)
        ttk.Button(btnrow, text="Add", command=self._tier_add).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Duplicate", command=self._tier_duplicate).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Delete", command=self._tier_delete).grid(row=0, column=2, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Random Reward", command=self._tier_add_random_reward).grid(row=0, column=3, sticky="ew")

        right = ttk.Labelframe(self.tab_tiers, text="Tier Editor")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(99, weight=1)
        right.grid_columnconfigure(0, weight=1)

        form = ttk.Frame(right)
        form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form.grid_columnconfigure(1, weight=1)

        self.tier_id_var = tk.StringVar()
        self.tier_required_var = tk.StringVar(value="0")

        ttk.Label(form, text="Tier").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(form, textvariable=self.tier_id_var, state="readonly").grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Required points").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.tier_required_var).grid(row=1, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Rewards on this tier (IDs)").grid(row=2, column=0, sticky="nw", padx=(0, 8), pady=(10, 0))
        self.lb_tier_rewards = tk.Listbox(form, height=10)
        self.lb_tier_rewards.grid(row=2, column=1, sticky="nsew", pady=(10, 0))
        form.grid_rowconfigure(2, weight=1)

        rr_btn = ttk.Frame(form)
        rr_btn.grid(row=3, column=1, sticky="ew", pady=(8, 0))
        for i in range(4):
            rr_btn.grid_columnconfigure(i, weight=1)

        ttk.Button(rr_btn, text="Remove Selected", command=self._tier_remove_selected_reward).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(rr_btn, text="Remove All", command=self._tier_remove_all_rewards).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Button(rr_btn, text="Add Reward ID", command=self._tier_add_reward_id_from_entry).grid(row=0, column=2, sticky="ew", padx=(0, 6))
        ttk.Button(rr_btn, text="Apply", command=self._tier_apply).grid(row=0, column=3, sticky="ew")

        addrow = ttk.Frame(form)
        addrow.grid(row=4, column=1, sticky="ew", pady=(8, 0))
        addrow.grid_columnconfigure(0, weight=1)
        self.tier_add_reward_id_var = tk.StringVar()
        ttk.Entry(addrow, textvariable=self.tier_add_reward_id_var).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(addrow, text="Add", command=self._tier_add_reward_id_from_entry, width=8).grid(row=0, column=1, sticky="e")

        ttk.Label(form, text="Advanced YAML (optional, for this tier only)").grid(row=5, column=0, sticky="nw", padx=(0, 8), pady=(10, 0))
        self.txt_tier_yaml = tk.Text(form, height=10, wrap="word")
        self.txt_tier_yaml.grid(row=5, column=1, sticky="nsew", pady=(10, 0))
        form.grid_rowconfigure(5, weight=1)

        adv_btn = ttk.Frame(form)
        adv_btn.grid(row=6, column=1, sticky="e", pady=(8, 0))
        ttk.Button(adv_btn, text="Apply YAML", command=self._tier_apply_yaml).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(adv_btn, text="Revert", command=self._tier_revert).grid(row=0, column=1)

    # -------------------------
    # Quests Tab
    # -------------------------
    def _build_quests_tab(self):
        self.tab_quests.grid_rowconfigure(0, weight=1)
        self.tab_quests.grid_columnconfigure(0, weight=1)
        self.tab_quests.grid_columnconfigure(1, weight=1)

        left = ttk.Labelframe(self.tab_quests, text="Quests (current quest file)")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        cols = ("id", "name", "type", "points")
        self.tv_quests = ttk.Treeview(left, columns=cols, show="headings", height=18)
        for c, w in [("id", 70), ("name", 250), ("type", 120), ("points", 80)]:
            self.tv_quests.heading(c, text=c.upper())
            self.tv_quests.column(c, width=w, stretch=True)
        self.tv_quests.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.tv_quests.bind("<<TreeviewSelect>>", self._on_quest_select)

        btnrow = ttk.Frame(left)
        btnrow.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        for i in range(5):
            btnrow.grid_columnconfigure(i, weight=1)
        ttk.Button(btnrow, text="Add", command=self._quest_add).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Duplicate", command=self._quest_duplicate).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Delete", command=self._quest_delete).grid(row=0, column=2, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Random", command=self._quest_add_random).grid(row=0, column=3, sticky="ew", padx=(0, 6))
        ttk.Button(btnrow, text="Apply", command=self._quest_apply).grid(row=0, column=4, sticky="ew")

        right = ttk.Labelframe(self.tab_quests, text="Quest Editor")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(99, weight=1)
        right.grid_columnconfigure(0, weight=1)

        form = ttk.Frame(right)
        form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form.grid_columnconfigure(1, weight=1)

        self.quest_id_var = tk.StringVar()
        self.quest_name_var = tk.StringVar()
        self.quest_type_var = tk.StringVar()
        self.quest_variable_var = tk.StringVar()
        self.quest_required_var = tk.StringVar(value="0")
        self.quest_points_var = tk.StringVar(value="0")
        self.quest_exclusive_var = tk.StringVar(value="")

        ttk.Label(form, text="ID").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(form, textvariable=self.quest_id_var, state="readonly").grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Name").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.quest_name_var).grid(row=1, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Type").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.quest_type_var).grid(row=2, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Variable").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.quest_variable_var).grid(row=3, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Required progress").grid(row=4, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.quest_required_var).grid(row=4, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Points").grid(row=5, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.quest_points_var).grid(row=5, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Exclusive (e.g. premium)").grid(row=6, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(form, textvariable=self.quest_exclusive_var).grid(row=6, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Special progress (one per line)").grid(row=7, column=0, sticky="nw", padx=(0, 8), pady=(10, 0))
        self.txt_quest_special = tk.Text(form, height=4, wrap="word")
        self.txt_quest_special.grid(row=7, column=1, sticky="ew", pady=(10, 0))

        ttk.Label(form, text="Item material").grid(row=8, column=0, sticky="w", padx=(0, 8), pady=(10, 0))
        self.quest_item_mat_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.quest_item_mat_var).grid(row=8, column=1, sticky="ew", pady=(10, 0))

        ttk.Label(form, text="Item amount").grid(row=9, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        self.quest_item_amt_var = tk.StringVar(value="1")
        ttk.Entry(form, textvariable=self.quest_item_amt_var).grid(row=9, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Item name").grid(row=10, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        self.quest_item_name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.quest_item_name_var).grid(row=10, column=1, sticky="ew", pady=(8, 0))

        ttk.Label(form, text="Item lore (one per line)").grid(row=11, column=0, sticky="nw", padx=(0, 8), pady=(10, 0))
        self.txt_quest_item_lore = tk.Text(form, height=7, wrap="word")
        self.txt_quest_item_lore.grid(row=11, column=1, sticky="nsew", pady=(10, 0))
        form.grid_rowconfigure(11, weight=1)

        ttk.Label(form, text="Advanced YAML (optional, overrides editor when applied)").grid(row=12, column=0, sticky="nw", padx=(0, 8), pady=(10, 0))
        self.txt_quest_yaml = tk.Text(form, height=10, wrap="word")
        self.txt_quest_yaml.grid(row=12, column=1, sticky="nsew", pady=(10, 0))
        form.grid_rowconfigure(12, weight=1)

        adv_btn = ttk.Frame(form)
        adv_btn.grid(row=13, column=1, sticky="e", pady=(8, 0))
        ttk.Button(adv_btn, text="Apply YAML", command=self._quest_apply_yaml).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(adv_btn, text="Revert", command=self._quest_revert).grid(row=0, column=1)

    # -------------------------
    # Preview Builders
    # -------------------------
    def _build_preview_battlepass(self):
        self.preview_bp.grid_rowconfigure(0, weight=1)
        self.preview_bp.grid_columnconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(self.preview_bp, bg="#111114", highlightthickness=0, bd=0)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.preview_hscroll = ttk.Scrollbar(self.preview_bp, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_hscroll.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 10))
        self.preview_canvas.configure(xscrollcommand=self.preview_hscroll.set)

        self.preview_canvas.bind("<Button-1>", self._on_preview_click)

    def _build_preview_quests(self):
        self.preview_q.grid_rowconfigure(0, weight=1)
        self.preview_q.grid_columnconfigure(0, weight=1)

        lf = ttk.Labelframe(self.preview_q, text="Quest Preview")
        lf.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)

        self.lb_preview_quests = tk.Listbox(lf)
        self.lb_preview_quests.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    # -------------------------
    # Global Refresh
    # -------------------------
    def refresh_all_views(self):
        if self.mode_var.get() == "battlepass":
            self._reward_refresh_list()
            self._tiers_refresh_list()
            self._render_preview_battlepass()
        else:
            self._quests_refresh_list()
            self._render_preview_quests()

    # -------------------------
    # Helpers
    # -------------------------
    def _tv_selected_iid(self, tv: ttk.Treeview):
        sel = tv.selection()
        return sel[0] if sel else ""

    def _set_text(self, w: tk.Text, s: str):
        w.delete("1.0", "end")
        w.insert("1.0", s or "")

    def _get_text(self, w: tk.Text) -> str:
        return (w.get("1.0", "end") or "").rstrip("\n")

    def _reward_refresh_list(self):
        self.tv_rewards.delete(*self.tv_rewards.get_children())
        rewards = ensure_dict(self.state.get("rewards", {}))
        for rid in sorted(rewards.keys(), key=numeric_sort_key):
            r = ensure_dict(rewards.get(rid, {}))
            self.tv_rewards.insert("", "end", iid=str(rid), values=(str(rid), str(r.get("name", "")), str(r.get("type", ""))))

    # -------------------------
    # Tiers Logic
    # -------------------------
    def _tiers_pass_dict(self):
        tr = self.track_var.get().strip().lower()
        if tr not in ("free", "premium"):
            tr = "free"
        return ensure_dict(self.state.get(tr, {}))

    def _tiers_dict(self):
        pd = self._tiers_pass_dict()
        return ensure_dict(pd.get("tiers", {}))

    def _tiers_refresh_list(self):
        if not hasattr(self, "tv_tiers"):
            return
        self.tv_tiers.delete(*self.tv_tiers.get_children())
        tiers = self._tiers_dict()
        for tid in sorted(tiers.keys(), key=numeric_sort_key):
            t = ensure_dict(tiers.get(tid, {}))
            req = t.get("required-points", t.get("required_points", 0))
            rewards = ensure_list(t.get("rewards", []))
            rtxt = ", ".join([str(x) for x in rewards])
            self.tv_tiers.insert("", "end", iid=str(tid), values=(str(tid), str(req), rtxt))

    def _on_tier_select(self, _e=None):
        tid = self._tv_selected_iid(self.tv_tiers)
        if not tid:
            return
        tiers = self._tiers_dict()
        t = ensure_dict(tiers.get(str(tid), {}))
        self._tier_load_editor(str(tid), t)

    def _tier_load_editor(self, tid: str, t: dict):
        self.tier_id_var.set(tid)
        req = t.get("required-points", t.get("required_points", 0))
        self.tier_required_var.set(str(req))

        self.lb_tier_rewards.delete(0, "end")
        for rid in [str(x) for x in ensure_list(t.get("rewards", []))]:
            self.lb_tier_rewards.insert("end", rid)

        self._set_text(self.txt_tier_yaml, yaml.safe_dump(t, sort_keys=False))

    def _tiers_select(self, tid: str):
        try:
            self.tv_tiers.selection_set(tid)
            self.tv_tiers.see(tid)
            self._on_tier_select()
        except Exception:
            pass

    def _tier_add(self):
        tr = self.track_var.get().strip().lower()
        pd = ensure_dict(self.state.get(tr, {}))
        tiers = ensure_dict(pd.get("tiers", {}))
        new_id = next_numeric_string_id(tiers.keys())
        tiers[new_id] = {"required-points": 0, "rewards": []}
        pd["tiers"] = tiers
        self.state[tr] = pd
        self.mark_dirty(tr, True)
        self._tiers_refresh_list()
        self._tiers_select(new_id)
        self.set_status(f"Added tier {new_id} to {tr}.")
        self._render_preview_battlepass()

    def _tier_duplicate(self):
        tid = self._tv_selected_iid(self.tv_tiers)
        if not tid:
            self.set_status("Select a tier to duplicate.")
            return
        tr = self.track_var.get().strip().lower()
        pd = ensure_dict(self.state.get(tr, {}))
        tiers = ensure_dict(pd.get("tiers", {}))
        src = ensure_dict(tiers.get(str(tid), {}))
        new_id = next_numeric_string_id(tiers.keys())
        tiers[new_id] = deep_copy(src)
        pd["tiers"] = tiers
        self.state[tr] = pd
        self.mark_dirty(tr, True)
        self._tiers_refresh_list()
        self._tiers_select(new_id)
        self.set_status(f"Duplicated tier {tid} -> {new_id} in {tr}.")
        self._render_preview_battlepass()

    def _tier_delete(self):
        tid = self._tv_selected_iid(self.tv_tiers)
        if not tid:
            self.set_status("Select a tier to delete.")
            return
        tr = self.track_var.get().strip().lower()
        pd = ensure_dict(self.state.get(tr, {}))
        tiers = ensure_dict(pd.get("tiers", {}))
        tiers.pop(str(tid), None)
        pd["tiers"] = tiers
        self.state[tr] = pd
        self.mark_dirty(tr, True)
        self._tiers_refresh_list()
        self._tier_clear_editor()
        self.set_status(f"Deleted tier {tid} from {tr}.")
        self._render_preview_battlepass()

    def _tier_clear_editor(self):
        self.tier_id_var.set("")
        self.tier_required_var.set("0")
        if hasattr(self, "lb_tier_rewards"):
            self.lb_tier_rewards.delete(0, "end")
        if hasattr(self, "txt_tier_yaml"):
            self._set_text(self.txt_tier_yaml, "")

    def _tier_apply(self):
        tid = self.tier_id_var.get().strip()
        if not tid:
            self.set_status("Select a tier first.")
            return
        tr = self.track_var.get().strip().lower()
        pd = ensure_dict(self.state.get(tr, {}))
        tiers = ensure_dict(pd.get("tiers", {}))
        t = ensure_dict(tiers.get(tid, {}))

        try:
            req = int(self.tier_required_var.get().strip() or "0")
        except Exception:
            req = 0

        rewards = []
        for i in range(self.lb_tier_rewards.size()):
            v = str(self.lb_tier_rewards.get(i)).strip()
            if v:
                rewards.append(v)

        t["required-points"] = req
        t["rewards"] = rewards
        tiers[tid] = t
        pd["tiers"] = tiers
        self.state[tr] = pd

        self.mark_dirty(tr, True)
        self._tiers_refresh_list()
        self._tiers_select(tid)
        self.set_status(f"Applied changes to {tr} tier {tid}.")
        self._render_preview_battlepass()

    def _tier_apply_yaml(self):
        tid = self.tier_id_var.get().strip()
        if not tid:
            self.set_status("Select a tier first.")
            return
        raw = self._get_text(self.txt_tier_yaml).strip()
        if not raw:
            self.set_status("No YAML provided.")
            return
        try:
            data = yaml.safe_load(raw)
            if not isinstance(data, dict):
                raise ValueError("Tier YAML must be a mapping.")
        except Exception as e:
            self.set_status(f"Tier YAML error: {e}")
            return

        tr = self.track_var.get().strip().lower()
        pd = ensure_dict(self.state.get(tr, {}))
        tiers = ensure_dict(pd.get("tiers", {}))
        tiers[tid] = data
        pd["tiers"] = tiers
        self.state[tr] = pd
        self.mark_dirty(tr, True)
        self._tiers_refresh_list()
        self._tiers_select(tid)
        self.set_status(f"Applied YAML to {tr} tier {tid}.")
        self._render_preview_battlepass()

    def _tier_revert(self):
        tid = self._tv_selected_iid(self.tv_tiers)
        if not tid:
            self.set_status("Select a tier first.")
            return
        tiers = self._tiers_dict()
        t = ensure_dict(tiers.get(str(tid), {}))
        self._tier_load_editor(str(tid), t)
        self.set_status(f"Reverted editor to tier {tid}.")

    def _tier_add_random_reward(self):
        tid = self._tv_selected_iid(self.tv_tiers)
        if not tid:
            self.set_status("Select a tier first.")
            return

        rewards = ensure_dict(self.state.get("rewards", {}))
        new_rid = next_numeric_string_id(rewards.keys())
        rewards[new_rid] = gen_random_reward()
        self.state["rewards"] = rewards
        self.mark_dirty("rewards", True)
        self._reward_refresh_list()

        self.tier_add_reward_id_var.set(new_rid)
        self._tier_add_reward_id_from_entry()

        self.set_status(f"Generated reward {new_rid} and added to tier {tid}.")
        self._render_preview_battlepass()

    def _tier_add_reward_id_from_entry(self):
        tid = self.tier_id_var.get().strip()
        if not tid:
            self.set_status("Select a tier first.")
            return
        rid = self.tier_add_reward_id_var.get().strip()
        if not rid:
            self.set_status("Enter a reward ID.")
            return
        cur = [str(self.lb_tier_rewards.get(i)).strip() for i in range(self.lb_tier_rewards.size())]
        if rid not in cur:
            self.lb_tier_rewards.insert("end", rid)
        self.tier_add_reward_id_var.set("")

    def _tier_remove_selected_reward(self):
        sel = self.lb_tier_rewards.curselection()
        if not sel:
            return
        idx = sel[0]
        self.lb_tier_rewards.delete(idx)

    def _tier_remove_all_rewards(self):
        self.lb_tier_rewards.delete(0, "end")

    # -------------------------
    # Quests Logic
    # -------------------------
    def _quests_dict(self):
        root = ensure_dict(self.state.get("quests", {}))
        qd = ensure_dict(root.get("quests", {}))
        return qd

    def _quests_root(self):
        root = ensure_dict(self.state.get("quests", {}))
        if "quests" not in root or not isinstance(root.get("quests"), dict):
            root["quests"] = {}
        return root

    def _quests_refresh_list(self):
        if not hasattr(self, "tv_quests"):
            return
        self.tv_quests.delete(*self.tv_quests.get_children())
        qd = self._quests_dict()
        for qid in sorted(qd.keys(), key=numeric_sort_key):
            q = ensure_dict(qd.get(qid, {}))
            self.tv_quests.insert("", "end", iid=str(qid), values=(str(qid), str(q.get("name", "")), str(q.get("type", "")), str(q.get("points", ""))))
        self._render_preview_quests()

    def _on_quest_select(self, _e=None):
        qid = self._tv_selected_iid(self.tv_quests)
        if not qid:
            return
        q = ensure_dict(self._quests_dict().get(str(qid), {}))
        self._quest_load_editor(str(qid), q)

    def _quest_load_editor(self, qid: str, q: dict):
        self.quest_id_var.set(qid)
        self.quest_name_var.set(str(q.get("name", "")))
        self.quest_type_var.set(str(q.get("type", "")))
        self.quest_variable_var.set(str(q.get("variable", "")))
        self.quest_required_var.set(str(q.get("required-progress", 0)))
        self.quest_points_var.set(str(q.get("points", 0)))
        self.quest_exclusive_var.set(str(q.get("exclusive", "")))

        self._set_text(self.txt_quest_special, join_lines(ensure_list(q.get("special-progress", []))))

        item = ensure_dict(q.get("item", {}))
        self.quest_item_mat_var.set(str(item.get("material", "")))
        self.quest_item_amt_var.set(str(item.get("amount", 1)))
        self.quest_item_name_var.set(str(item.get("name", "")))
        self._set_text(self.txt_quest_item_lore, join_lines(ensure_list(item.get("lore", []))))

        self._set_text(self.txt_quest_yaml, yaml.safe_dump(q, sort_keys=False))

    def _quest_add(self):
        root = self._quests_root()
        qd = ensure_dict(root.get("quests", {}))
        new_id = next_numeric_string_id(qd.keys())
        qd[new_id] = gen_random_quest()
        root["quests"] = qd
        self.state["quests"] = root
        self.mark_dirty("quests", True)
        self._quests_refresh_list()
        self.tv_quests.selection_set(new_id)
        self.tv_quests.see(new_id)
        self.set_status(f"Added quest {new_id}.")

    def _quest_duplicate(self):
        qid = self._tv_selected_iid(self.tv_quests)
        if not qid:
            self.set_status("Select a quest to duplicate.")
            return
        root = self._quests_root()
        qd = ensure_dict(root.get("quests", {}))
        src = ensure_dict(qd.get(str(qid), {}))
        new_id = next_numeric_string_id(qd.keys())
        qd[new_id] = deep_copy(src)
        qd[new_id]["name"] = str(qd[new_id].get("name", "Quest")) + " (Copy)"
        root["quests"] = qd
        self.state["quests"] = root
        self.mark_dirty("quests", True)
        self._quests_refresh_list()
        self.tv_quests.selection_set(new_id)
        self.tv_quests.see(new_id)
        self.set_status(f"Duplicated quest {qid} -> {new_id}.")

    def _quest_delete(self):
        qid = self._tv_selected_iid(self.tv_quests)
        if not qid:
            self.set_status("Select a quest to delete.")
            return
        root = self._quests_root()
        qd = ensure_dict(root.get("quests", {}))
        qd.pop(str(qid), None)
        root["quests"] = qd
        self.state["quests"] = root
        self.mark_dirty("quests", True)
        self._quests_refresh_list()
        self._quest_clear_editor()
        self.set_status(f"Deleted quest {qid}.")

    def _quest_add_random(self):
        self._quest_add()

    def _quest_apply(self):
        qid = self.quest_id_var.get().strip()
        if not qid:
            self.set_status("Select a quest first.")
            return

        root = self._quests_root()
        qd = ensure_dict(root.get("quests", {}))
        q = ensure_dict(qd.get(qid, {}))

        q["name"] = self.quest_name_var.get().strip()
        q["type"] = self.quest_type_var.get().strip()
        q["variable"] = self.quest_variable_var.get().strip()

        try:
            q["required-progress"] = int(self.quest_required_var.get().strip() or "0")
        except Exception:
            q["required-progress"] = 0

        try:
            q["points"] = int(self.quest_points_var.get().strip() or "0")
        except Exception:
            q["points"] = 0

        exc = self.quest_exclusive_var.get().strip()
        if exc:
            q["exclusive"] = exc
        else:
            q.pop("exclusive", None)

        sp = split_lines(self._get_text(self.txt_quest_special))
        if sp:
            q["special-progress"] = sp
        else:
            q.pop("special-progress", None)

        item = ensure_dict(q.get("item", {}))
        item["material"] = self.quest_item_mat_var.get().strip()
        try:
            item["amount"] = int(self.quest_item_amt_var.get().strip() or "1")
        except Exception:
            item["amount"] = 1
        item["name"] = self.quest_item_name_var.get().strip()
        lore = split_lines(self._get_text(self.txt_quest_item_lore))
        if lore:
            item["lore"] = lore
        else:
            item.pop("lore", None)
        q["item"] = item

        qd[qid] = q
        root["quests"] = qd
        self.state["quests"] = root
        self.mark_dirty("quests", True)
        self._quests_refresh_list()
        self.tv_quests.selection_set(qid)
        self.set_status(f"Applied changes to quest {qid}.")
        self._render_preview_quests()

    def _quest_apply_yaml(self):
        qid = self.quest_id_var.get().strip()
        if not qid:
            self.set_status("Select a quest first.")
            return
        raw = self._get_text(self.txt_quest_yaml).strip()
        if not raw:
            self.set_status("No YAML provided.")
            return
        try:
            data = yaml.safe_load(raw)
            if not isinstance(data, dict):
                raise ValueError("Quest YAML must be a mapping.")
        except Exception as e:
            self.set_status(f"Quest YAML error: {e}")
            return

        root = self._quests_root()
        qd = ensure_dict(root.get("quests", {}))
        qd[qid] = data
        root["quests"] = qd
        self.state["quests"] = root
        self.mark_dirty("quests", True)
        self._quests_refresh_list()
        self.tv_quests.selection_set(qid)
        self.set_status(f"Applied YAML to quest {qid}.")
        self._render_preview_quests()

    def _quest_revert(self):
        qid = self._tv_selected_iid(self.tv_quests)
        if not qid:
            self.set_status("Select a quest first.")
            return
        q = ensure_dict(self._quests_dict().get(str(qid), {}))
        self._quest_load_editor(str(qid), q)
        self.set_status(f"Reverted editor to quest {qid}.")

    def _quest_clear_editor(self):
        self.quest_id_var.set("")
        self.quest_name_var.set("")
        self.quest_type_var.set("")
        self.quest_variable_var.set("")
        self.quest_required_var.set("0")
        self.quest_points_var.set("0")
        self.quest_exclusive_var.set("")
        self._set_text(self.txt_quest_special, "")
        self.quest_item_mat_var.set("")
        self.quest_item_amt_var.set("1")
        self.quest_item_name_var.set("")
        self._set_text(self.txt_quest_item_lore, "")
        self._set_text(self.txt_quest_yaml, "")

    # -------------------------
    # Preview Renderers
    # -------------------------
    def _render_preview_battlepass(self):
        if not hasattr(self, "preview_canvas"):
            return

        c = self.preview_canvas
        c.delete("all")

        rewards = ensure_dict(self.state.get("rewards", {}))
        free_tiers = ensure_dict(ensure_dict(self.state.get("free", {})).get("tiers", {}))
        prem_tiers = ensure_dict(ensure_dict(self.state.get("premium", {})).get("tiers", {}))

        all_ids = sorted(set([str(k) for k in free_tiers.keys()] + [str(k) for k in prem_tiers.keys()]), key=numeric_sort_key)

        pad_x = 16
        x = pad_x
        tile = 56
        gap = 14
        y_p = 40
        y_f = 120

        c.create_text(pad_x, 16, text="PREMIUM", anchor="w", fill=PREM_COL, font=FONT_B)
        c.create_text(pad_x, 96, text="FREE", anchor="w", fill=FREE_COL, font=FONT_B)

        for tid in all_ids:
            p = ensure_dict(prem_tiers.get(tid, {}))
            f = ensure_dict(free_tiers.get(tid, {}))

            pid_list = [str(v) for v in ensure_list(p.get("rewards", []))]
            fid_list = [str(v) for v in ensure_list(f.get("rewards", []))]

            p_em = "".join([reward_emoji(ensure_dict(rewards.get(rid, {}))) for rid in pid_list]) or "—"
            f_em = "".join([reward_emoji(ensure_dict(rewards.get(rid, {}))) for rid in fid_list]) or "—"

            pr = c.create_rectangle(x, y_p, x + tile, y_p + tile, fill=PREM_COL, outline="")
            fr = c.create_rectangle(x, y_f, x + tile, y_f + tile, fill=FREE_COL, outline="")

            pt = c.create_text(x + tile / 2, y_p + tile / 2, text=p_em, font=("Segoe UI", 16))
            ft = c.create_text(x + tile / 2, y_f + tile / 2, text=f_em, font=("Segoe UI", 16))

            c.create_text(x + tile / 2, y_f + tile + 16, text=str(tid), fill=MUTED, font=FONT)

            p_names = []
            for rid in pid_list:
                rr = ensure_dict(rewards.get(rid, {}))
                p_names.append(str(rr.get("name", f"Reward {rid}")))
            f_names = []
            for rid in fid_list:
                rr = ensure_dict(rewards.get(rid, {}))
                f_names.append(str(rr.get("name", f"Reward {rid}")))

            p_tip = f"Tier {tid}\nPremium\n\n" + ("\n".join(p_names) if p_names else "No rewards")
            f_tip = f"Tier {tid}\nFree\n\n" + ("\n".join(f_names) if f_names else "No rewards")

            for item in (pr, pt):
                c.tag_bind(item, "<Enter>", lambda e, t=p_tip: self.tooltip.show(t, e.x_root, e.y_root))
                c.tag_bind(item, "<Leave>", lambda _e: self.tooltip.hide())
                c.tag_bind(item, "<Button-1>", lambda _e, tr="premium", tid=tid: self._select_tier_from_preview(tr, tid))

            for item in (fr, ft):
                c.tag_bind(item, "<Enter>", lambda e, t=f_tip: self.tooltip.show(t, e.x_root, e.y_root))
                c.tag_bind(item, "<Leave>", lambda _e: self.tooltip.hide())
                c.tag_bind(item, "<Button-1>", lambda _e, tr="free", tid=tid: self._select_tier_from_preview(tr, tid))

            x += tile + gap

        c.configure(scrollregion=c.bbox("all"))

    def _render_preview_quests(self):
        if not hasattr(self, "lb_preview_quests"):
            return
        self.lb_preview_quests.delete(0, "end")
        qd = self._quests_dict()
        for qid in sorted(qd.keys(), key=numeric_sort_key):
            q = ensure_dict(qd.get(qid, {}))
            self.lb_preview_quests.insert("end", f"{qid}: {q.get('name', '')}")

    def _select_tier_from_preview(self, track: str, tid: str):
        self.mode_var.set("battlepass")
        self._wire_mode()
        self.nb.select(self.tab_tiers)
        self.track_var.set(track)
        self._tiers_refresh_list()
        self._tiers_select(str(tid))

    def _on_preview_click(self, _e=None):
        pass

    # -------------------------
    # Hook missing calls in older flow
    # -------------------------
    def _build_preview_battlepass(self):
        if hasattr(self, "preview_canvas"):
            return
        self.preview_bp.grid_rowconfigure(0, weight=1)
        self.preview_bp.grid_columnconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(self.preview_bp, bg="#111114", highlightthickness=0, bd=0)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.preview_hscroll = ttk.Scrollbar(self.preview_bp, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_hscroll.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 10))
        self.preview_canvas.configure(xscrollcommand=self.preview_hscroll.set)

    def _build_preview_quests(self):
        if hasattr(self, "lb_preview_quests"):
            return
        self.preview_q.grid_rowconfigure(0, weight=1)
        self.preview_q.grid_columnconfigure(0, weight=1)

        lf = ttk.Labelframe(self.preview_q, text="Quest Preview")
        lf.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        lf.grid_rowconfigure(0, weight=1)
        lf.grid_columnconfigure(0, weight=1)

        self.lb_preview_quests = tk.Listbox(lf)
        self.lb_preview_quests.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    # -------------------------
    # Ensure preview builders exist at runtime
    # -------------------------
    def _ensure_preview_built(self):
        self._build_preview_battlepass()
        self._build_preview_quests()

    # -------------------------
    # Override reload to build previews if needed
    # -------------------------
    def reload_all(self):
        try:
            self._ensure_preview_built()
            self.state["free"] = safe_load_yaml(self.path_free.get())
            self.state["premium"] = safe_load_yaml(self.path_premium.get())
            self.state["rewards"] = safe_load_yaml(self.path_rewards.get())
            self.state["quests_path"] = self.path_quests.get()
            self.state["quests"] = safe_load_yaml(self.state["quests_path"])
            self.mark_dirty("free", False)
            self.mark_dirty("premium", False)
            self.mark_dirty("rewards", False)
            self.mark_dirty("quests", False)
            self.set_status("Loaded files successfully.")
            self.refresh_all_views()
        except Exception as e:
            self.set_status(f"Load error: {e}")

    # -------------------------
    # Wire mode also refreshes
    # -------------------------
    def _wire_mode(self):
        mode = self.mode_var.get()
        if mode == "battlepass":
            self.q_files.grid_remove()
            self.bp_files.grid()
            self.nb.tab(self.tab_rewards, state="normal")
            self.nb.tab(self.tab_tiers, state="normal")
            self.nb.tab(self.tab_quests, state="hidden")
            self.preview_q.grid_remove()
            self.preview_bp.grid()
        else:
            self.bp_files.grid_remove()
            self.q_files.grid()
            self.nb.tab(self.tab_rewards, state="hidden")
            self.nb.tab(self.tab_tiers, state="hidden")
            self.nb.tab(self.tab_quests, state="normal")
            self.preview_bp.grid_remove()
            self.preview_q.grid()
        self.refresh_all_views()

    def _tv_selected(self, tv: ttk.Treeview) -> str:
        return self._tv_selected_iid(tv)


    def _select_iid(self, tv: ttk.Treeview, iid: str):
        try:
            tv.selection_set(str(iid))
            tv.focus(str(iid))
            tv.see(str(iid))
        except Exception:
            pass


    def _render_preview(self):
        if getattr(self, "mode_var", None) and self.mode_var.get() == "battlepass":
            if hasattr(self, "_ensure_preview_built"):
                self._ensure_preview_built()
            self._render_preview_battlepass()
        else:
            if hasattr(self, "_ensure_preview_built"):
                self._ensure_preview_built()
            self._render_preview_quests()


    def _reward_is_referenced(self, rid: str) -> bool:
        rid = str(rid)
        for tr in ("free", "premium"):
            pd = ensure_dict(self.state.get(tr, {}))
            tiers = ensure_dict(pd.get("tiers", {}))
            for _tid, t in tiers.items():
                rewards = [str(x) for x in ensure_list(ensure_dict(t).get("rewards", []))]
                if rid in rewards:
                    return True
        return False


    def _reward_clear_editor(self):
        if hasattr(self, "reward_id_var"):
            self.reward_id_var.set("")
        if hasattr(self, "reward_name_var"):
            self.reward_name_var.set("")
        if hasattr(self, "reward_type_var"):
            self.reward_type_var.set("command")
            if hasattr(self, "_reward_switch_type"):
                self._reward_switch_type()

        if hasattr(self, "txt_reward_loreaddon"):
            self._set_text(self.txt_reward_loreaddon, "")
        if hasattr(self, "txt_reward_vars"):
            self._set_text(self.txt_reward_vars, "")
        if hasattr(self, "txt_reward_cmds"):
            self._set_text(self.txt_reward_cmds, "")
        if hasattr(self, "txt_reward_yaml"):
            self._set_text(self.txt_reward_yaml, "")

        if hasattr(self, "item_material_var"):
            self.item_material_var.set("")
        if hasattr(self, "item_amount_var"):
            self.item_amount_var.set("1")
        if hasattr(self, "item_dispname_var"):
            self.item_dispname_var.set("")
        if hasattr(self, "item_glow_var"):
            self.item_glow_var.set(False)
        if hasattr(self, "txt_item_lore"):
            self._set_text(self.txt_item_lore, "")

        if hasattr(self, "money_value_var"):
            self.money_value_var.set("0")


if __name__ == "__main__":
    app = BattlePassStudio()
    app.mainloop()
