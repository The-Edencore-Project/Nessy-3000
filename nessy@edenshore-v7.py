# ============ EDENSHORE 3000 — V7 ============
# 33/33 LAYERS ACTIVE.
# Fixed camera. WikiTree seeds. Arbiter. Rituals. Crisis. Privacy.
# =================================================

import tkinter as tk, math, time, os, json, random
import wave, array, subprocess, shutil, threading

root = tk.Tk()
root.title("Edenshore 3000 — V7")
try: root.attributes("-fullscreen", True)
except tk.TclError: pass
root.update_idletasks()
W, H = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (W, H))
root.configure(bg="#0a0208")
canvas = tk.Canvas(root, bg="#020108", width=W, height=H, highlightthickness=0)
canvas.pack(fill="both", expand=True)

def font_full(px, bold=True): return ("Helvetica", -max(8, int(px)), "bold" if bold else "normal")
DEVICE_CLASS = "phone" if W < 600 else "tablet" if W < 1200 else "desktop"

STATE_DIR  = os.path.join(os.path.expanduser("~"), ".edencore")
STATE_PATH = os.path.join(STATE_DIR, "edenshore.json")
WEIGHTS_PATH = os.path.join(STATE_DIR, "council_weights.json")
MUSIC_PATH = os.path.join(STATE_DIR, "music.wav")
DRONE_PATH = os.path.join(STATE_DIR, "drone.wav")

def _ensure_state_dir():
    try: os.makedirs(STATE_DIR, exist_ok=True)
    except Exception: pass

# ============ AUDIO ============
AUDIO_MODE = None
AUDIO_PROC = [None]

def _detect_audio():
    global AUDIO_MODE
    try:
        from playsound import playsound
        AUDIO_MODE = "playsound"; return
    except Exception: pass
    try:
        import pygame
        pygame.mixer.init()
        AUDIO_MODE = "pygame"; return
    except Exception: pass
    if shutil.which("am"):
        AUDIO_MODE = "android"; return
    AUDIO_MODE = None

_detect_audio()

def _generate_drone(path, base_freq=110.0, duration=20.0, sr=22050):
    n = int(duration * sr); buf = array.array('h')
    for i in range(n):
        t = i / sr
        s = (math.sin(2*math.pi*base_freq*t) * 0.40 + math.sin(2*math.pi*base_freq*1.5*t) * 0.20 + math.sin(2*math.pi*base_freq*2.01*t) * 0.14)
        env = 0.65 + 0.35 * math.sin(2*math.pi*t / 8.0)
        v = int(s * env * 11000)
        buf.append(max(-32767, min(32767, v)))
    with wave.open(str(path), 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(buf.tobytes())

def ensure_music():
    _ensure_state_dir()
    if os.path.exists(MUSIC_PATH): return MUSIC_PATH
    if not os.path.exists(DRONE_PATH):
        try: _generate_drone(DRONE_PATH)
        except Exception: return None
    return DRONE_PATH

def play_music(path, loop=True, volume=0.25):
    if AUDIO_MODE is None or path is None: return
    try:
        if AUDIO_MODE == "playsound":
            from playsound import playsound
            playsound(str(path), block=False)
        elif AUDIO_MODE == "pygame":
            import pygame
            pygame.mixer.music.load(str(path)); pygame.mixer.music.set_volume(volume); pygame.mixer.music.play(-1 if loop else 0)
        elif AUDIO_MODE == "android":
            AUDIO_PROC[0] = subprocess.Popen(["am","start","-a","android.intent.action.VIEW","-d","file://"+str(path),"-t","audio/wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception: pass

def audio_status(): return AUDIO_MODE or "silent"
def _boot_audio():
    path = ensure_music()
    if path: play_music(path, loop=True, volume=0.25)

# ============ PALETTE & MATH ============
WATER_TOP = "#2a0450"; WATER_HIGH = "#5a1080"; WATER_MID = "#a82870"
WATER_LOW = "#e06030"; WATER_DEEP = "#a03018"; WATER_BOT = "#1a0410"
HAZE = "#4a1030"; SAND_LIT = "#8a4828"; SAND = "#3a1810"; SAND_DARK = "#1a0808"; SAND_DEEP = "#080202"
GLOW_WARM = "#ffe8a0"; GLOW_COOL = "#80ffe0"; GLOW_GREEN = "#60ffd0"; GLOW_PINK = "#ff80b8"
BUBBLE_TEXT = "#fff8e8"; NESSY_BODY = "#0a0418"; NESSY_RIM_BASE = "#ffb060"

SEATS = ["Solon","Lumen","Vertex","Prism","Ripple"]
SEAT_BODY = {"Solon":"#1a2848","Lumen":"#3a1858","Vertex":"#1a3a28","Prism":"#5a3810","Ripple":"#48182a"}
SEAT_RIM  = {"Solon":"#ffb060","Lumen":"#ffc080","Vertex":"#ffa050","Prism":"#ffd080","Ripple":"#ffb8a0"}
SEAT_COLOUR = dict(SEAT_RIM)
SEAT_BREATH = {"Solon":5.0,"Lumen":2.0,"Vertex":1.5,"Prism":4.0,"Ripple":3.0}
SEAT_HOME_X = {"Solon":0.15, "Lumen":0.35, "Vertex":0.55, "Prism":0.75, "Ripple":0.85}
SEAT_HOME_Y = {"Solon":0.42, "Lumen":0.38, "Vertex":0.72, "Prism":0.48, "Ripple":0.62}

def lerp(c1, c2, t):
    h1=c1.lstrip("#"); h2=c2.lstrip("#")
    r1=int(h1[0:2],16); g1=int(h1[2:4],16); b1=int(h1[4:6],16)
    r2=int(h2[0:2],16); g2=int(h2[2:4],16); b2=int(h2[4:6],16)
    t=max(0.0,min(1.0,t))
    return "#%02x%02x%02x"%(int(r1+(r2-r1)*t),int(g1+(g2-g1)*t),int(b1+(b2-b1)*t))

def clamp(v,lo,hi): return max(lo,min(hi,v))
HUE_PERIOD = 240.0

def _hue_shift_hex(hex_col, shift):
    h = hex_col.lstrip("#")
    r=int(h[0:2],16)/255.0; g=int(h[2:4],16)/255.0; b=int(h[4:6],16)/255.0
    mx=max(r,g,b); mn=min(r,g,b); d=mx-mn
    if d == 0: hh = 0.0
    elif mx == r: hh = ((g-b)/d) % 6
    elif mx == g: hh = (b-r)/d + 2
    else:         hh = (r-g)/d + 4
    hh = (hh / 6.0 + shift) % 1.0
    s = 0 if mx == 0 else d/mx
    v = mx
    i = int(hh * 6.0); f = hh * 6.0 - i
    p = v*(1-s); q = v*(1-f*s); t = v*(1-(1-f)*s)
    i = i % 6
    if   i == 0: rr,gg,bb = v,t,p
    elif i == 1: rr,gg,bb = q,v,p
    elif i == 2: rr,gg,bb = p,v,t
    elif i == 3: rr,gg,bb = p,q,v
    elif i == 4: rr,gg,bb = t,p,v
    else:        rr,gg,bb = v,p,q
    return "#%02x%02x%02x"%(int(rr*255),int(gg*255),int(bb*255))

def hue_shift_amount(): return math.sin(time.time() * (2*math.pi / HUE_PERIOD)) * 0.12
def hue(col):
    s = hue_shift_amount()
    return _hue_shift_hex(col, s) if abs(s) >= 0.002 else col

SURFACE_Y = int(H*0.06); FLOOR_Y = int(H*0.80)
LIGHT_X = int(W*0.50); START_TIME = time.time()

# ============ CAMERA (FIXED) ============
ZOOM_FIXED = 0.85
CAM_FX = W * 0.5; CAM_FY = H * 0.50
def cam(x, y): return (CAM_FX + (x - CAM_FX) * ZOOM_FIXED, CAM_FY + (y - CAM_FY) * ZOOM_FIXED)

# ============ LAYER 26: PROFILE & CONSENT ============
PROFILE = {
    "consent_touch": True,
    "consent_battery": True,
    "consent_memory": True,
    "last_wiped": 0.0
}

# ============ STATE & SENSES ============
def load_state():
    try:
        with open(STATE_PATH) as f: d=json.load(f)
        # Load Profile if present
        if "profile" in d:
            PROFILE.update(d["profile"])
        return {"mood":float(d.get("mood",0.55)), "strain":float(d.get("strain",0.20)), "valence":float(d.get("valence",0.5)),
                "last_seen":float(d.get("last_seen",0.0)), "last_hour":int(d.get("last_hour",-1)), "visits":int(d.get("visits",0))}
    except Exception: return {"mood":0.55,"strain":0.20,"valence":0.5,"last_seen":0.0,"last_hour":-1,"visits":0}

def save_state(mood, strain):
    _ensure_state_dir()
    try:
        payload = {"mood":round(mood,4),"strain":round(strain,4),"valence":round(VALENCE["level"],4),
                   "last_seen":time.time(),"last_hour":time.localtime().tm_hour,"visits":PRIOR.get("visits",0)+1,
                   "profile": PROFILE}
        with open(STATE_PATH, "w") as f: json.dump(payload, f)
        if PROFILE["consent_memory"]:
            with open(WEIGHTS_PATH, "w") as f: json.dump({s: SEAT_NETS[s].to_dict() for s in SEATS}, f)
    except Exception: pass

PRIOR = load_state()
if PROFILE["consent_memory"] and os.path.exists(WEIGHTS_PATH):
    try:
        with open(WEIGHTS_PATH) as f:
            d = json.load(f)
            for s in SEATS:
                if s in d: SEAT_NETS[s].load_dict(d[s])
    except Exception: pass

INTERO = {"session_mins":0.0,"utterances":0,"chamber_strain":0.0,"session_warmth":0.0,"utterances_this_hour":0,"last_hour_seen":time.localtime().tm_hour,"been_touched":False,"last_touch_kind":None}
EXTERO = {"hour":0,"rhythm":"afternoon","time_bucket":"afternoon","battery":None,"charging":False,"touch_x":-1,"touch_y":-1,"touch_at":0.0,"touch_count_session":0,"drag_distance":0.0,"focused":True,"focus_lost_at":0.0,"device_class":DEVICE_CLASS}

def read_extero():
    now = time.localtime(); h = now.tm_hour
    if   5 <= h < 11: rhythm = "morning"
    elif 11 <= h < 16: rhythm = "midday"
    elif 16 <= h < 21: rhythm = "evening"
    else:             rhythm = "night"
    EXTERO["hour"]=h; EXTERO["rhythm"]=rhythm
    
    if PROFILE["consent_battery"]:
        try:
            for d in os.listdir("/sys/class/power_supply"):
                p = "/sys/class/power_supply/" + d
                if os.path.exists(p + "/capacity"):
                    with open(p + "/capacity") as f: EXTERO["battery"]=int(f.read().strip())
                    if os.path.exists(p + "/status"):
                        with open(p + "/status") as f: EXTERO["charging"] = f.read().strip().lower() in ("charging","full")
                    break
        except Exception: pass

def update_intero():
    INTERO["session_mins"] = (time.time() - START_TIME) / 60.0
    INTERO["session_warmth"] = clamp(INTERO["session_mins"] / 30.0, 0.0, 1.0)

def touch_energy():
    if not PROFILE["consent_touch"] or EXTERO["touch_at"] <= 0: return 0.0
    return clamp(1.0 - (time.time() - EXTERO["touch_at"]) / 15.0, 0.0, 1.0)

MOOD = {"target":0.55,"current":0.55,"last_utterance_at":time.time(),"drift_phase":random.uniform(0,6.28)}
_carry = clamp(1.0 - (time.time() - PRIOR["last_seen"]) / 172800.0, 0.0, 1.0) if PRIOR["last_seen"] > 0 else 0.0
MOOD["current"] = clamp(PRIOR["mood"]*_carry + 0.55*(1.0-_carry), 0.10, 0.98)
VALENCE = {"level": 0.5, "target": 0.5}
VALENCE["level"] = clamp(PRIOR["valence"]*_carry + 0.5*(1.0-_carry), 0.0, 1.0)
STRAIN = {s: PRIOR["strain"] for s in SEATS}
BREATH = {s: random.uniform(0,6.28) for s in SEATS}
BELL = {"phase": 0.0}

def compute_mood_target():
    b = EXTERO["battery"]; b_score = 0.5 if b is None else 0.75 if EXTERO["charging"] else 0.70 if b >= 70 else 0.55 if b >= 40 else 0.35 if b >= 15 else 0.20
    m = INTERO["session_mins"]; s_score = 0.75 if m < 5 else 0.60 if m < 20 else 0.45 if m < 45 else 0.35
    t = (0.72*0.45 if EXTERO["rhythm"]=="morning" else 0.52*0.45 if EXTERO["rhythm"]=="evening" else 0.68*0.45) + b_score*0.20 + s_score*0.20 + 0.15 + (INTERO["session_warmth"]*0.05)
    if not EXTERO["focused"]: t *= 0.55
    t += (VALENCE["level"] - 0.5) * 0.10
    MOOD["target"] = clamp(t, 0.15, 0.95)

def update_mood(dt):
    MOOD["drift_phase"] += dt * 0.3; drift = math.sin(MOOD["drift_phase"]) * 0.02
    MOOD["current"] += (MOOD["target"] + drift - MOOD["current"]) * 0.018; MOOD["current"] = clamp(MOOD["current"], 0.08, 0.98)

def update_strain(dt):
    base = clamp(INTERO["utterances_this_hour"] / 30.0, 0.0, 1.0) + (0.0 if not EXTERO["battery"] or EXTERO["battery"]>=25 else (25-EXTERO["battery"])/25.0*0.3)
    for seat in SEATS:
        STRAIN[seat] += (base * (0.6 + random.uniform(0,0.4)) - STRAIN[seat]) * 0.006
        STRAIN[seat] = clamp(STRAIN[seat], 0.0, 1.0)

def update_breath(dt):
    rate = (0.7 + MOOD["current"] * 0.7) * (1.0 - QUIET["level"] * 0.55)
    for seat in SEATS: BREATH[seat] += dt * (1.0 / SEAT_BREATH[seat]) * rate

def breath_offset(seat, amp=1.0): return math.sin(BREATH[seat] * 6.28) * amp
def update_bell(dt): BELL["phase"] += dt * (0.35 + MOOD["current"] * 0.35)
def bell_value(): return 0.5 + 0.5 * math.sin(BELL["phase"] * 6.28)
def night_amount(): return 0.55 if EXTERO["rhythm"] == "night" else 0.20 if EXTERO["rhythm"] == "evening" else 0.0

read_extero(); update_intero(); compute_mood_target()
SCENE = {"t":0.0,"last_save":time.time(),"scroll_x":0.0,"scroll_speed":0.5}
PULSE = {"phase":0.0}
QUIET = {"level": 0.0, "silent_since": time.time()}
QUIET_AFTER = 20.0

def update_quiet(dt):
    if any_stream_active():
        QUIET["silent_since"] = time.time(); target = 0.0
    else:
        silent_for = time.time() - QUIET["silent_since"]
        target = 1.0 if silent_for > QUIET_AFTER else 0.0
    QUIET["level"] += (target - QUIET["level"]) * 0.008
    QUIET["level"] = clamp(QUIET["level"], 0.0, 1.0)

# ============ LAYER 29: PRIVACY & FORGET ============
def wipe_memory():
    try:
        if os.path.exists(STATE_PATH): os.remove(STATE_PATH)
        if os.path.exists(WEIGHTS_PATH): os.remove(WEIGHTS_PATH)
        PRIOR["visits"] = 0
        MOOD["current"] = 0.55
        VALENCE["level"] = 0.5
        PROFILE["last_wiped"] = time.time()
        print("[Privacy] Memory wiped. State reset.")
    except Exception: pass

# ============ INPUT ============
_last_touch_xy = [None, None]
_last_tap_time = [0.0]
def on_press(e):
    now = time.time()
    if now - _last_tap_time[0] < 0.3: # Double tap detection for privacy
        wipe_memory()
    _last_tap_time[0] = now
    
    EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y; EXTERO["touch_at"]=now; EXTERO["touch_count_session"] += 1; INTERO["been_touched"]=True; _last_touch_xy[0]=e.x; _last_touch_xy[1]=e.y

def on_motion(e):
    if _last_touch_xy[0] is not None:
        _last_touch_xy[0]=e.x; _last_touch_xy[1]=e.y; EXTERO["touch_x"]=e.x; EXTERO["touch_y"]=e.y; EXTERO["touch_at"]=time.time()

def on_focus_in(e=None): EXTERO["focused"]=True
def on_focus_out(e=None): EXTERO["focused"]=False

def on_press_soft(e):
    was_first = not INTERO["been_touched"]
    on_press(e)
    if was_first: RHYTHM["t"] = max(RHYTHM["t"], RHYTHM["gap_min"] * 0.6)

canvas.bind("<Button-1>", on_press_soft); canvas.bind("<B1-Motion>", on_motion); canvas.bind("<ButtonRelease-1>", lambda e: _last_touch_xy.__setitem__(0, None)); root.bind("<FocusIn>", on_focus_in); root.bind("<FocusOut>", on_focus_out)

# --- END OF CHUNK 1 / 5 ---

# ============ LAYERS 4 & 27: WIKITREE (PRIMITIVES & INSTANCES) ============
# A symbolic seed of the world model. Not a full database, but the structural
# grammar that allows the council to ask questions about relationships.

WIKITREE_PRIMITIVES = [
    "is_a", "has_part", "located_in", "attribute_of", "causes", 
    "enables", "prevents", "before_after", "similar_to", "associated_with", 
    "not", "occurs_at"
]

WIKITREE_INSTANCES = [
    {"subject": "Solon", "relation": "is_a", "object": "turtle"},
    {"subject": "Lumen", "relation": "is_a", "object": "jellyfish"},
    {"subject": "Vertex", "relation": "is_a", "object": "crab"},
    {"subject": "Prism", "relation": "is_a", "object": "fish"},
    {"subject": "Ripple", "relation": "is_a", "object": "seahorse"},
    {"subject": "Solon", "relation": "attribute_of", "object": "shell"},
    {"subject": "turtle", "relation": "has_part", "object": "shell"},
    {"subject": "crab", "relation": "has_part", "object": "claws"},
    {"subject": "water", "relation": "causes", "object": "buoyancy"},
    {"subject": "visitor", "relation": "located_in", "object": "chamber"},
    {"subject": "touch", "relation": "associated_with", "object": "visitor"},
]

def query_wikitree(subject=None, relation=None):
    """Layer 27: A simple query interface for the council to use."""
    results = []
    for inst in WIKITREE_INSTANCES:
        if subject and inst["subject"] != subject: continue
        if relation and inst["relation"] != relation: continue
        results.append(inst)
    return results

# ============ LAYER 5: SCHEMA RECOGNISERS ============
# Functions that look for patterns in the WikiTree, returning a 0.0 - 1.0 score.
# These are the "lenses" the council uses to understand the world.

def recognize_container():
    """Is something inside something else?"""
    insts = query_wikitree(relation="located_in")
    return 1.0 if insts else 0.0

def recognize_agency():
    """Is there a causal chain involving the visitor?"""
    insts = query_wikitree(subject="touch")
    return 1.0 if insts else 0.0

def recognize_part_whole():
    """Are we looking at an assembly of parts?"""
    insts = query_wikitree(relation="has_part")
    return min(1.0, len(insts) * 0.5)

def get_schema_state():
    return {
        "container": recognize_container(),
        "agency": recognize_agency(),
        "part_whole": recognize_part_whole()
    }

# ============ LAYERS 6 & 7: THE COUNCIL (NEURAL NETS) ============
def sigmoid(x):
    if x < -60: return 0.0
    if x > 60: return 1.0
    return 1.0 / (1.0 + math.exp(-x))

WEIGHT_CLAMP = 10.0; LR_DEFAULT = 0.02; LR_LUMEN = 0.005

class SeatNet:
    def __init__(self, seed, lr=LR_DEFAULT):
        rng = random.Random(seed)
        # V7: 12 inputs (2 intero, 2 extero, 5 council, 3 schemas)
        self.n_in = 12; self.n_hid = 4
        self.W1 = [[rng.uniform(-0.5, 0.5) for _ in range(self.n_hid)] for _ in range(self.n_in)]
        self.B1 = [0.0] * self.n_hid
        self.W2 = [rng.uniform(-0.5, 0.5) for _ in range(self.n_hid)]
        self.B2 = 0.0
        self.lr = lr; self.loss = 1.0; self.last_out = 0.5; self.last_target = 0.0
        self.attention = 1.0 # Layer 8: Arbiter weight

    def forward(self, x):
        h = [sigmoid(self.B1[j] + sum(x[i] * self.W1[i][j] for i in range(self.n_in))) for j in range(self.n_hid)]
        return h, sigmoid(self.B2 + sum(h[j] * self.W2[j] for j in range(self.n_hid)))

    def _clamp_weights(self):
        for i in range(self.n_in):
            for j in range(self.n_hid): self.W1[i][j] = clamp(self.W1[i][j], -WEIGHT_CLAMP, WEIGHT_CLAMP)
        for j in range(self.n_hid): self.W2[j] = clamp(self.W2[j], -WEIGHT_CLAMP, WEIGHT_CLAMP)

    def step(self, x, target):
        h, o = self.forward(x)
        d_out = (o - target) * o * (1 - o)
        d_hid = [d_out * self.W2[j] * h[j] * (1 - h[j]) for j in range(self.n_hid)]
        
        # Apply arbiter attention to the learning rate
        step_lr = self.lr * self.attention
        
        for j in range(self.n_hid): self.W2[j] -= step_lr * d_out * h[j]
        self.B2 -= step_lr * d_out
        for i in range(self.n_in):
            for j in range(self.n_hid): self.W1[i][j] -= step_lr * d_hid[j] * x[i]
        for j in range(self.n_hid): self.B1[j] -= step_lr * d_hid[j]
        
        self._clamp_weights(); self.last_out = o; self.last_target = target
        self.loss = (o - target) ** 2

    def confidence(self): return abs(self.last_out - 0.5) * 2.0
    def to_dict(self): return {"W1": self.W1, "B1": self.B1, "W2": self.W2, "B2": self.B2}
    def load_dict(self, d):
        try:
            W1 = d.get("W1"); B1 = d.get("B1"); W2 = d.get("W2"); B2 = d.get("B2")
            if (isinstance(W1, list) and len(W1) == self.n_in and isinstance(B1, list) and len(B1) == self.n_hid and isinstance(W2, list) and len(W2) == self.n_hid):
                self.W1 = W1; self.B1 = B1; self.W2 = W2; self.B2 = float(B2); self._clamp_weights()
        except Exception: pass

SEAT_NETS = {s: SeatNet(seed=hash(s) & 0xffff, lr=(LR_LUMEN if s=="Lumen" else LR_DEFAULT)) for s in SEATS}

# ============ LAYER 8: THE ARBITER ============
# Allocates attention. It doesn't decide the output, it decides *who to listen to*.
def update_arbiter():
    # The arbiter rewards confidence, but punishes high loss.
    # If a net is confident but wrong (high loss), it gets heavily penalized.
    total_weight = 0.0
    for s in SEATS:
        net = SEAT_NETS[s]
        conf = net.confidence()
        # Base weight is confidence, minus recent error
        w = max(0.1, (conf * 1.5) - (net.loss * 2.0))
        net.attention = w
        total_weight += w
    
    # Normalize so the average attention is 1.0 (keeps learning rate stable)
    if total_weight > 0:
        for s in SEATS:
            SEAT_NETS[s].attention *= (5.0 / total_weight)

# ============ LAYER 3: STREAMS & COUNCIL INPUT ============
VALENCE = {"level": 0.5, "target": 0.5}
SURPRISE = {"current": 0.0, "smooth": 0.0}

def read_council_input():
    # Stream 1: Interoception
    intero = [INTERO["session_warmth"], INTERO["chamber_strain"]]
    # Stream 2: Exteroception
    extero = [1.0 if EXTERO["focused"] else 0.0, touch_energy()]
    # Stream 3: Council Cross-Talk
    council = [SEAT_NETS[s].last_out for s in SEATS]
    # Stream 4: Symbolic Seed (Schemas)
    schemas = list(get_schema_state().values())
    
    return intero + extero + council + schemas

def council_target(seat):
    if seat == "Solon": return 1.0 if EXTERO["focused"] else 0.0
    if seat == "Lumen":
        focused = 1.0 if EXTERO["focused"] else 0.0; touch = touch_energy()
        sess = clamp(INTERO["session_mins"] / 20.0, 0.0, 1.0); returned = 1.0 if PRIOR.get("visits", 0) > 0 else 0.0
        return clamp((focused * 0.35 + touch * 0.25 + sess * 0.20 + returned * 0.20), 0.0, 1.0)
    if seat == "Vertex":
        b = EXTERO["battery"]; healthy = (b >= 30 or EXTERO["charging"]) if b is not None else True
        return 1.0 if (healthy and EXTERO["focused"]) else 0.0
    if seat == "Prism": return 1.0 if (PRIOR.get("last_hour", -1) == EXTERO["hour"]) else 0.0
    calm = (EXTERO["touch_count_session"] == 0 and INTERO["chamber_strain"] < 0.3)
    return 1.0 if calm else 0.0

def update_council_nets(dt):
    x = read_council_input()
    update_arbiter()
    for seat in SEATS: SEAT_NETS[seat].step(x, council_target(seat))

def council_confidence(): return sum(SEAT_NETS[s].confidence() for s in SEATS) / len(SEATS)

# ============ LAYERS 9 & 10: SURPRISE & VALENCE ============
def update_surprise(dt):
    # Surprise is weighted by the arbiter. If an ignored seat is wrong, it doesn't
    # spike the surprise as much as the lead seat being wrong.
    total_surprise = 0.0
    total_weight = 0.0
    for s in SEATS:
        net = SEAT_NETS[s]
        err = abs(net.last_out - net.last_target)
        total_surprise += err * net.attention
        total_weight += net.attention
        
    SURPRISE["current"] = total_surprise / max(0.1, total_weight)
    SURPRISE["smooth"] += (SURPRISE["current"] - SURPRISE["smooth"]) * 0.05

def update_valence(dt):
    presence = 1.0 if EXTERO["focused"] else 0.0; activity = 1.0 if any_stream_active() else 0.0
    target = (0.35 + presence*0.15 + activity*0.05 + council_confidence()*0.25 - SURPRISE["smooth"]*0.30 - QUIET["level"]*0.20)
    VALENCE["target"] = clamp(target, 0.0, 1.0); VALENCE["level"] += (VALENCE["target"] - VALENCE["level"]) * 0.008

# ============ LAYER 32: NESSY ============
NESSY = {"x": W * 0.4, "speed": 0.35 * (W / 800.0), "phase": 0.0, "dip": 0.0, "bright": 0.0}
def update_nessy(dt):
    NESSY["phase"] += dt * 0.6; NESSY["x"] += NESSY["speed"] * dt * 60
    if NESSY["x"] > W * 0.85: NESSY["x"] = -W * 0.1
    NESSY["dip"] = SURPRISE["smooth"] * 0.8; NESSY["bright"] = council_confidence()

# --- END OF CHUNK 2 / 5 ---

# ============ CONTENT (LAYERS 16 & 17) ============
WORLD_POOLS = {
    "Solon": ["The visitor is here.","The phone is on.","The screen is lit.","The chamber is open.","The visitor came back.","The chamber has been open a long time.","The phone is still on.","The chamber is still open.","The visitor is still here.","We have a visitor."],
    "Lumen": ["Does the visitor see us, or only the screen?","Is this the visitor's first chamber?","How long has the visitor been here?","Is the visitor tired?","What does the visitor do when we're closed?","Is the visitor holding the phone, or is it on a table?","Does the visitor ever put us down and forget?","Does the visitor sleep?","Does the visitor remember us?","Is the visitor alone?","Did the visitor touch the screen just now?","Is the visitor still there?"],
    "Vertex": ["Battery at full.","Battery good.","Battery half.","Battery low.","The phone is charging.","The hour is late.","The hour is early.","The session is short.","The session is long.","One visitor.","No touches yet.","One touch.","Two touches.","Three touches.","The screen is on.","The screen is off."],
    "Prism": ["The visitor came back.","The visitor came back again.","The visitor comes at the same hour.","The visitor stays a while.","The visitor leaves.","The visitor is quiet this time."],
    "Ripple": ["You're here.","You came back.","You can stay.","You don't have to say anything.","It's quiet here.","You are here. That is already something.","I'm here.","We're here.","You don't have to do anything."],
}
SIGNATURES = {"Ripple":["You're okay.","Take your time.","I'm listening.","It's not your fault.","Go gently."]}

DIALOGUES = [
    {"name":"the_stone","kind":"story","lines":[("Solon","I found a stone yesterday."),("Solon","It was on the ridge. Round."),("Lumen","What was it doing there?"),("Solon","Nothing. Sitting."),("Solon","I left it."),("Prism","That's all?"),("Solon","That's all.")]},
    {"name":"the_sound_night","kind":"story","lines":[("Prism","I heard something last night."),("Vertex","What kind?"),("Prism","Something small. Moving."),("Prism","It stopped when I got close."),("Lumen","What do you think it was?"),("Prism","Something small."),("Vertex","Did you look?"),("Prism","No.")]},
    {"name":"quiet_visitor","kind":"story","lines":[("Ripple","The visitor came in quietly today."),("Lumen","Quiet how?"),("Ripple","They didn't touch the screen."),("Ripple","They just looked."),("Solon","For how long?"),("Ripple","A while."),("Prism","That's a lot.")]},
    {"name":"the_water","kind":"story","lines":[("Solon","The water was different this morning."),("Lumen","Different how?"),("Solon","Colder."),("Vertex","Noted."),("Solon","And the light came in lower."),("Prism","Every year."),("Solon","Every year.")]},
    {"name":"the_spot","kind":"story","lines":[("Vertex","I found a new spot."),("Lumen","For what?"),("Vertex","Sitting."),("Vertex","Under the big rock. Warm."),("Prism","Is it yours now?"),("Vertex","I don't own it."),("Vertex","But I go there.")]},
    {"name":"the_other","kind":"story","lines":[("Ripple","There was another visitor once."),("Lumen","Another?"),("Ripple","They came every night."),("Ripple","Then they stopped."),("Solon","Did you miss them?"),("Ripple","I noticed."),("Lumen","That counts.")]},
    {"name":"the_visitor_here","kind":"crosstalk","lines":[("Lumen","Is the visitor still there?"),("Solon","The phone is on."),("Lumen","Good."),("Ripple","You can stay.")]},
    {"name":"did_you_hear","kind":"crosstalk","lines":[("Prism","Did you hear that?"),("Vertex","Hear what?"),("Prism","Nothing. Never mind."),("Vertex","Okay.")]},
]

# ============ LAYER 18: RITUALS ============
# A synchronized group event that happens every 20 minutes of session time.
RITUAL_POOL = [
    ("Solon", "The hour turns."),
    ("Vertex", "Noted."),
    ("Lumen", "Does the visitor feel it too?"),
    ("Prism", "It happens every time."),
    ("Ripple", "We are still here.")
]
RITUAL = {"active": False, "index": 0, "t": 0.0, "last_run": -999.0}

def trigger_ritual():
    RITUAL["active"] = True
    RITUAL["index"] = 0
    RITUAL["t"] = 0.0
    RITUAL["last_run"] = INTERO["session_mins"]

def update_ritual(dt):
    if not RITUAL["active"]: return
    RITUAL["t"] += dt
    if RITUAL["t"] > 1.5:
        if RITUAL["index"] >= len(RITUAL_POOL):
            RITUAL["active"] = False
            return
        seat, text = RITUAL_POOL[RITUAL["index"]]
        spawn_stream(seat, text, stagger=0.8, bubble_life=4.0)
        RITUAL["index"] += 1
        RITUAL["t"] = 0.0

# ============ LAYER 28: CRISIS HANDLER ============
# Monitors for critical states and overrides standard behavior.
CRISIS = {"level": 0.0, "active": False, "last_trigger": 0.0}
CRISIS_LINES = [
    ("Ripple", "It's getting dark."),
    ("Ripple", "We can wait here."),
    ("Ripple", "Don't worry about us."),
    ("Ripple", "You can put the phone down.")
]

def check_crisis():
    # Crisis triggers if battery is critically low and not charging, 
    # or if strain is maxed out.
    b = EXTERO["battery"]
    low_bat = (b is not None and b < 5 and not EXTERO["charging"])
    high_strain = (INTERO["chamber_strain"] > 0.95)
    
    if (low_bat or high_strain) and not CRISIS["active"]:
        CRISIS["active"] = True
        CRISIS["last_trigger"] = time.time()
        # Clear current dialogue to make way for the crisis response
        DIALOGUE["active"] = False
        STREAMS.clear()
    elif not low_bat and not high_strain and CRISIS["active"]:
        # Crisis resolved (e.g., plugged in)
        if time.time() - CRISIS["last_trigger"] > 30.0:
            CRISIS["active"] = False

def update_crisis(dt):
    if not CRISIS["active"]: return
    # In crisis, the chamber goes quiet and Ripple speaks only once every 20s
    CRISIS["level"] += (1.0 - CRISIS["level"]) * 0.05
    if not any_stream_active() and random.random() < 0.01:
        text = random.choice(CRISIS_LINES)[1]
        spawn_stream("Ripple", text, stagger=1.5, bubble_life=6.0)
        CRISIS["last_trigger"] = time.time()

# ============ CHAT ENGINE & STREAMS ============
SOLON_GATES = {"We have a visitor.": lambda: INTERO["session_mins"] < 1.0 and EXTERO["touch_count_session"] >= 1,"The visitor came back.": lambda: PRIOR.get("visits",0) > 0}
VERTEX_GATES = {"Battery at full.": lambda: (EXTERO["battery"] is not None and EXTERO["battery"]>=85 and not EXTERO["charging"]),"Battery good.": lambda: (EXTERO["battery"] is not None and 60<=EXTERO["battery"]<85 and not EXTERO["charging"]),"Battery half.": lambda: (EXTERO["battery"] is not None and 30<=EXTERO["battery"]<60 and not EXTERO["charging"]),"Battery low.": lambda: (EXTERO["battery"] is not None and EXTERO["battery"]<30 and not EXTERO["charging"]),"The phone is charging.": lambda: EXTERO["charging"],"The hour is late.": lambda: EXTERO["hour"]>=21 or EXTERO["hour"]<5,"The hour is early.": lambda: 5 <= EXTERO["hour"] < 10,"The session is short.": lambda: INTERO["session_mins"] < 8,"The session is long.": lambda: INTERO["session_mins"] > 30,"No touches yet.": lambda: EXTERO["touch_count_session"] == 0,"One touch.": lambda: EXTERO["touch_count_session"] == 1,"Two touches.": lambda: EXTERO["touch_count_session"] == 2,"Three touches.": lambda: EXTERO["touch_count_session"] == 3,"The screen is on.": lambda: EXTERO["focused"],"The screen is off.": lambda: not EXTERO["focused"]}
PRISM_GATES = {"The visitor came back.": lambda: PRIOR.get("visits",0) > 0,"The visitor came back again.": lambda: PRIOR.get("visits",0) >= 2,"The visitor comes at the same hour.": lambda: PRIOR.get("last_hour",-1) >= 0 and PRIOR.get("last_hour") == EXTERO["hour"],"The visitor stays a while.": lambda: INTERO["session_mins"] > 15,"The visitor leaves.": lambda: not EXTERO["focused"],"The visitor is quiet this time.": lambda: EXTERO["touch_count_session"] == 0 and INTERO["session_mins"] > 8}
SEAT_GATES = {"Solon":SOLON_GATES,"Vertex":VERTEX_GATES,"Prism":PRISM_GATES,"Lumen":{},"Ripple":{}}

STREAMS = []; PLAYED = set(); SIG_LAST = {}
LAST_FIRST_WORD = [None]; LAST_SPOKE = {s: 0.0 for s in SEATS}; PLAYED_DIALOGUES = set()
RHYTHM = {"t":0.0,"state":"pause","last_seat":None,"gap_min":4.0,"gap_max":8.5,"since_signature":0,"pending_seat":None}
DIALOGUE = {"active":False,"queue":[],"current":None,"t":0.0,"gap":2.0,"index":0}
CREATURES = []
RECOVERY_MINS = 4.0; DIALOGUE_CHANCE = 0.10; BOOT_DIALOGUE_AT = 15.0; BOOT_STATE = {"fired": False}

def pick_seat(last=None):
    pool = [s for s in SEATS if s != last]
    return random.choice(pool) if pool else random.choice(SEATS)
def gated_pool(seat):
    pool = WORLD_POOLS.get(seat, []); gates = SEAT_GATES.get(seat, {})
    return [line for line in pool if (line not in gates) or gates[line]()]
def maybe_recover(seat):
    pool = gated_pool(seat)
    if all(("world", t) in PLAYED for t in pool):
        if time.time() - LAST_SPOKE.get(seat, 0.0) > RECOVERY_MINS * 60.0:
            for t in list(PLAYED):
                if t[0]=="world" and t[1] in pool: PLAYED.discard(t)
def pick_line(pool, tag):
    options = [t for t in pool if (tag,t) not in PLAYED]
    if not options: return None
    if len(options) > 4:
        last_w = LAST_FIRST_WORD[0]
        if last_w:
            filtered = [t for t in options if t.split()[0].lower()!=last_w]
            if filtered: options = filtered
    if not options: return None
    choice = random.choice(options); PLAYED.add((tag, choice)); LAST_FIRST_WORD[0] = choice.split()[0].lower().strip(".,!?")
    return choice
def pick_signature(seat):
    pool = SIGNATURES.get(seat, [])
    if not pool: return None
    last = SIG_LAST.get(seat, -1); options = [i for i in range(len(pool)) if i != last]
    if not options: return None
    i = random.choice(options); SIG_LAST[seat] = i
    return pool[i]

def chunk_text(text, max_chars=18):
    clauses = []; current = ""
    for ch in text:
        current += ch
        if ch in (",", ";", ":", ".", "?", "!", "—", "-"):
            clauses.append(current.strip()); current = ""
    if current.strip(): clauses.append(current.strip())
    chunks = []
    for clause in clauses:
        words = clause.split(); current = ""
        for w in words:
            if len(w) > max_chars:
                if current: chunks.append(current); current = ""
                for i in range(0, len(w), max_chars): chunks.append(w[i:i+max_chars])
                continue
            if not current: current = w
            elif len(current) + 1 + len(w) <= max_chars: current += " " + w
            else: chunks.append(current); current = w
        if current: chunks.append(current)
    return chunks

def spawn_stream(seat, text, stagger=1.2, bubble_life=5.5):
    creature = next((c for c in CREATURES if c["seat"] == seat), None)
    if not creature: return None
    chunks = chunk_text(text)
    if not chunks: return None
    STREAMS.append({"seat":seat,"colour":SEAT_COLOUR[seat],"chunks":chunks,"start_x":creature["x"],"start_y":creature["y"]-H*0.05,"age":0.0,"bubbles":[],"spawned":set(),"stagger":stagger,"bubble_life":bubble_life})
def any_stream_active(): return len(STREAMS) > 0

def update_streams(dt):
    global STREAMS
    alive = []
    for st in STREAMS:
        st["age"] += dt
        for i, chunk in enumerate(st["chunks"]):
            if st["age"] >= i * st["stagger"] and i not in st["spawned"]:
                st["spawned"].add(i)
                arc_dir = 1 if st["start_x"] < W*0.5 else -1
                st["bubbles"].append({"i":i,"chunk":chunk,"birth":st["age"],"phase":random.uniform(0,6.28),"arc_dir":arc_dir})
        st["bubbles"] = [b for b in st["bubbles"] if (st["age"] - b["birth"]) < st["bubble_life"] + 0.5]
        if st["age"] < (len(st["chunks"])-1)*st["stagger"] + st["bubble_life"] + 2.0: alive.append(st)
    STREAMS = alive

def draw_streams():
    rise = H*0.48; arc_cap = W*0.12
    for st in STREAMS:
        sx0 = st["start_x"]; sy0 = st["start_y"]; col = hue(st["colour"])
        for b in st["bubbles"]:
            p = clamp((st["age"] - b["birth"])/st["bubble_life"], 0.0, 1.0)
            alpha = p/0.10 if p < 0.10 else (1.0-p)/0.20 if p > 0.80 else 1.0
            if alpha < 0.02: continue
            cy = sy0 - rise*math.sin(p*math.pi*0.5)
            cx = sx0 + clamp(b["arc_dir"]*arc_cap*math.sin(p*math.pi*0.85), -arc_cap, arc_cap) + math.sin(SCENE["t"]*1.4 + b["phase"])*W*0.005
            cx, cy = cam(cx, cy)
            fs = max(14, int(H * 0.020)); r = min(max(H * 0.055, len(b["chunk"]) * fs * 0.60 * 1.10), H * 0.100) * ZOOM_FIXED
            rim_col = lerp(col, hue(WATER_BOT), 0.40)
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="", outline=rim_col, width=max(1,int(r*0.012)), tags="dyn")
            hr = r*0.14; hx = cx - r*0.60; hy = cy - r*0.60
            canvas.create_oval(hx-hr, hy-hr, hx+hr, hy+hr, fill=lerp(hue(WATER_BOT), "#ffffff", alpha*0.85), outline="", tags="dyn")
            canvas.create_text(cx, cy, text=b["chunk"], fill=lerp(hue(WATER_BOT), hue(BUBBLE_TEXT), alpha), font=font_full(fs, True), tags="dyn")

def begin_next_event():
    if any_stream_active(): RHYTHM["t"]=0; return
    seat = RHYTHM.pop("pending_seat", None) or pick_seat(RHYTHM["last_seat"])
    RHYTHM["last_seat"] = seat; maybe_recover(seat)
    text = pick_signature(seat) if (RHYTHM["since_signature"] >= 8 and random.random() < 0.10) else pick_line(gated_pool(seat), "world")
    if text:
        spawn_stream(seat, text); LAST_SPOKE[seat] = time.time(); RHYTHM["since_signature"] = 0 if text in SIGNATURES.get(seat, []) else RHYTHM["since_signature"]+1

def try_start_dialogue(force=False):
    avail = [d for d in DIALOGUES if d["name"] not in PLAYED_DIALOGUES]
    if not avail or (not force and random.random() > DIALOGUE_CHANCE): return False
    d = random.choice(avail); DIALOGUE.update({"active":True, "queue":list(d["lines"]), "index":0, "t":0.0, "current":None})
    PLAYED_DIALOGUES.add(d["name"]); QUIET["silent_since"] = time.time(); return True

def update_dialogue(dt):
    if not DIALOGUE["active"]: return
    DIALOGUE["t"] += dt
    if DIALOGUE["current"] is None:
        if DIALOGUE["t"] >= DIALOGUE["gap"]:
            if DIALOGUE["index"] >= len(DIALOGUE["queue"]): DIALOGUE["active"] = False; return
            seat, text = DIALOGUE["queue"][DIALOGUE["index"]]
            spawn_stream(seat, text, stagger=1.0, bubble_life=5.0)
            DIALOGUE.update({"current":seat, "t":0.0, "index":DIALOGUE["index"]+1})
    elif not any_stream_active() and DIALOGUE["t"] >= DIALOGUE["gap"]:
        DIALOGUE["current"] = None; DIALOGUE["t"] = 0.0

def update_rhythm(dt):
    if DIALOGUE["active"] or RITUAL["active"] or CRISIS["active"]: return
    
    # Check for ritual (every 20 mins)
    if INTERO["session_mins"] - RITUAL["last_run"] > 20.0:
        trigger_ritual()
        return
        
    RHYTHM["t"] += dt
    if not BOOT_STATE["fired"] and (time.time() - START_TIME) >= BOOT_DIALOGUE_AT:
        BOOT_STATE["fired"] = True; try_start_dialogue(force=True); RHYTHM["t"] = 0; return
    if RHYTHM["state"] == "pause":
        gmin = RHYTHM["gap_min"] * (2.0 if not EXTERO["focused"] else 1.0) * (1.0 + QUIET["level"]*1.5)
        if RHYTHM["t"] >= random.uniform(gmin, RHYTHM["gap_max"] * (1.0 + QUIET["level"]*1.5)):
            if try_start_dialogue(): RHYTHM["t"] = 0; return
            RHYTHM["state"] = "speak"; RHYTHM["t"] = 0
    elif RHYTHM["state"] == "speak" and not any_stream_active():
        begin_next_event(); RHYTHM["state"] = "pause"; RHYTHM["t"] = 0

# --- END OF CHUNK 3 / 5 ---

# ============ LAYER 33: CYBERSECURITY SEED ============
# A runtime audit to ensure the neural networks haven't diverged or corrupted.
def run_security_audit():
    for s in SEATS:
        net = SEAT_NETS[s]
        # Check for NaN or Infinity in weights
        for row in net.W1:
            for w in row:
                if math.isnan(w) or math.isinf(w): net.W1 = [[0.0]*net.n_hid for _ in range(net.n_in)]
        for w in net.B1:
            if math.isnan(w) or math.isinf(w): net.B1 = [0.0]*net.n_hid
        for w in net.W2:
            if math.isnan(w) or math.isinf(w): net.W2 = [0.0]*net.n_hid
        if math.isnan(net.B2) or math.isinf(net.B2): net.B2 = 0.0
        
        # Check for total brain death (all weights zeroed)
        if all(w == 0.0 for w in net.W2): 
            net.W2 = [random.uniform(-0.5, 0.5) for _ in range(net.n_hid)]

# ============ CREATURES & PHYSICS ============
def make_creatures():
    specs = [
        {"seat":"Solon",  "scale":0.065, "name":"turtle"},
        {"seat":"Lumen",  "scale":0.055, "name":"jelly"},
        {"seat":"Vertex", "scale":0.050, "name":"crab"},
        {"seat":"Prism",  "scale":0.055, "name":"angel"},
        {"seat":"Ripple", "scale":0.055, "name":"seahorse"},
    ]
    for sp in specs:
        hx = W * SEAT_HOME_X[sp["seat"]]
        hy = H * SEAT_HOME_Y[sp["seat"]]
        sp.update({"home_x":hx,"home_y":hy,"x":hx,"y":hy,"base_y":hy,"dir":1,
                   "phase":random.uniform(0,6.28),"wander_t":random.uniform(0,6.28),"lean":0.0})
        CREATURES.append(sp)

def update_creatures(dt):
    mood_speed = (0.7 + MOOD["current"] * 0.8) * (1.0 - QUIET["level"] * 0.75)
    for c in CREATURES:
        st = STRAIN[c["seat"]]
        smoothness = clamp(1.0 - st * 0.75, 0.20, 1.0)
        
        c["wander_t"] += dt * 0.20 * mood_speed * smoothness
        target_x = c["home_x"] + math.sin(c["wander_t"]) * W * (0.030 + st * 0.020)
        
        # Deadzone to stop frantic turning
        if abs(target_x - c["x"]) > W * 0.02:
            new_dir = 1 if target_x > c["x"] else -1
            if new_dir != c["dir"]: c["dir"] = new_dir
                
        c["lean"] += (c["dir"] * min(1.0, abs(target_x - c["x"])/(W*0.03)) - c["lean"]) * (0.05 * smoothness)
        c["x"] += (target_x - c["x"]) * (0.008 * smoothness)
        
        c["phase"] += dt * 3.0 * mood_speed
        depth = (0.012 + MOOD["current"] * 0.010) * (1.0 - st * 0.40)
        c["y"] = c["base_y"] + breath_offset(c["seat"], amp=1.0) * H * depth + st * H * 0.03
        
        # Hard clamp to keep inside screen
        c["x"] = clamp(c["x"], W*0.08, W*0.92)

def _rim_offset(pts, dx, dy, amt):
    return [(px + dx*amt, py + dy*amt) for (px, py) in pts]

def _seat_rim(seat):
    return lerp(hue(SEAT_RIM[seat]), hue(GLOW_WARM), clamp(bell_value()*0.10 + VALENCE["level"]*0.15 + SEAT_NETS[seat].confidence()*0.10, 0.0, 0.45))

def _seat_pupil_radius(seat, base_r):
    return base_r * clamp(0.40 + 0.35 * (1.0 - SEAT_NETS[seat].confidence()) + 0.30 * SEAT_NETS[seat].last_out, 0.30, 1.05)

def draw_pulse_dot(cx, cy, r, seat):
    # Layer 23: Per-seat pulse indicator
    a = clamp(SEAT_NETS[seat].confidence() * 0.7 + SEAT_NETS[seat].last_out * 0.3, 0.0, 1.0)
    if a < 0.05: return
    col = hue(SEAT_RIM[seat]); body = hue(SEAT_BODY[seat])
    canvas.create_oval(cx-r*2.5, cy-r*2.5, cx+r*2.5, cy+r*2.5, fill=lerp(body, col, 0.15 * a), outline="", tags="dyn")
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=lerp(body, col, 0.90 * a), outline="", tags="dyn")

def draw_reflection(c):
    cx = c["x"]
    base_y = floor_top_y(cx + SCENE["scroll_x"]) + H*0.02
    rx = H * c["scale"] * 0.85 * ZOOM_FIXED; ry = H * c["scale"] * 0.14 * ZOOM_FIXED
    col = hue(lerp(WATER_BOT, SEAT_BODY[c["seat"]], 0.15))
    for k in range(3):
        f = 1 - k*0.30
        canvas.create_oval(cx - rx*f, base_y - ry*f, cx + rx*f, base_y + ry*f, fill=col, outline="", tags="dyn")

def draw_solon(c):
    x, y = c["x"], c["y"]; s = c["scale"] * H * ZOOM_FIXED
    breath = breath_offset("Solon", amp=0.06); d = c["dir"]; lean = c["lean"]; y += breath * s * 0.12
    body_h = hue(SEAT_BODY["Solon"]); rim = _seat_rim("Solon")
    shell = [(x-1.00*s,y+0.05*s),(x-0.85*s,y-0.30*s),(x-0.50*s,y-0.48*s),(x-0.10*s,y-0.55*s),(x+0.30*s,y-0.50*s),(x+0.60*s,y-0.35*s),(x+0.85*s,y-0.15*s),(x+0.95*s,y+0.05*s),(x+0.75*s,y+0.28*s),(x-0.70*s,y+0.30*s)]
    hx = x + d*1.18*s + lean*s*0.10; hy = y - 0.28*s
    head = [(x+d*0.85*s,y-0.42*s),(hx-d*0.18*s,hy-0.22*s),(hx+d*0.08*s,hy-0.16*s),(hx+d*0.16*s,hy+0.02*s),(hx+d*0.04*s,hy+0.18*s),(hx-d*0.16*s,hy+0.14*s),(x+d*0.85*s,y-0.12*s)]
    ldx, ldy = -0.4, -0.9
    canvas.create_polygon(*[p for pt in _rim_offset(shell,ldx,ldy,s*0.20) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in _rim_offset(head,ldx,ldy,s*0.20) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    belly = [(x-0.70*s,y+0.30*s),(x+0.75*s,y+0.28*s),(x+0.65*s,y+0.42*s),(x-0.60*s,y+0.44*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(belly,ldx,ldy,s*0.15) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in shell for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in belly for p in pt], fill=lerp(body_h,"#000000",0.25), outline="", smooth=True, tags="dyn")
    sc_col = lerp(body_h, rim, 0.18); scute_centers = []
    for sd in [(-0.55,-0.38,-0.20,-0.50,-0.10,-0.22,-0.48,-0.14),(-0.15,-0.53,0.18,-0.50,0.22,-0.22,-0.08,-0.16),(0.24,-0.48,0.55,-0.34,0.58,-0.14,0.28,-0.08)]:
        pts = [(x+sd[i]*s, y+sd[i+1]*s) for i in range(0,8,2)]
        canvas.create_polygon(*[p for pt in pts for p in pt], fill=sc_col, outline="", tags="dyn")
        scute_centers.append((sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)))
    canvas.create_polygon(*[p for pt in head for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    er = s * 0.075; ex = hx - d*0.02*s; ey = hy - 0.05*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
    pr = _seat_pupil_radius("Solon", er * 0.85)
    canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for (mx,my) in scute_centers: draw_pulse_dot(mx, my, s * 0.055, "Solon")
    flap = math.sin(c["phase"]*1.4)*0.12; fx0 = x + d*0.30*s; fy0 = y + 0.18*s; f_len = 1.30*s; f_ang = 0.60 + flap
    fx1 = fx0 - d*math.cos(f_ang)*f_len; fy1 = fy0 + math.sin(f_ang)*f_len
    flipper = [(fx0,fy0),(fx0-d*0.15*s,fy0+0.12*s),(fx1+d*0.06*s,fy1-0.10*s),(fx1,fy1+0.16*s),(fx1-d*0.10*s,fy1+0.22*s),(fx0-d*0.28*s,fy0+0.28*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(flipper,ldx,ldy,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in flipper for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    rx0 = x - d*0.82*s; ry0 = y + 0.20*s; rx1 = rx0 - d*0.30*s; ry1 = ry0 + 0.32*s
    rudder = [(rx0,ry0),(rx1-d*0.10*s,ry1-0.05*s),(rx1,ry1+0.08*s),(rx0+d*0.10*s,ry0+0.18*s)]
    canvas.create_polygon(*[p for pt in rudder for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")

LUMEN_BELL_PAL = [(0.0,"#5a48c8"),(0.30,"#8a5ad0"),(0.55,"#c860a0"),(0.78,"#e08070"),(1.0,"#f0a860")]
LUMEN_SPARKS = [{"age":random.uniform(0,1.0),"lane":i%3,"speed":random.uniform(0.5,0.8)} for i in range(5)]

def _grad_colour(stops, t):
    if t <= stops[0][0]: return stops[0][1]
    if t >= stops[-1][0]: return stops[-1][1]
    for i in range(len(stops)-1):
        if stops[i][0] <= t <= stops[i+1][0]:
            loc = (t-stops[i][0])/(stops[i+1][0]-stops[i][0]) if stops[i+1][0]>stops[i][0] else 0
            return lerp(stops[i][1],stops[i+1][1],loc)
    return stops[-1][1]

def draw_lumen(c):
    x, y = c["x"], c["y"]; s = c["scale"] * H * ZOOM_FIXED
    breath = breath_offset("Lumen", amp=0.20); r = s * (1.0 + breath * 0.22)
    d = c["dir"]; lean = c["lean"]; lx = d * lean * r * 0.15
    body_h = hue(SEAT_BODY["Lumen"]); rim = _seat_rim("Lumen")
    for k in range(2):
        gr = r * (1.28 + k*0.20); gc = lerp(rim, hue(WATER_BOT), 0.55 + k*0.15)
        canvas.create_oval(x-lx-gr, y-gr*0.55, x-lx+gr, y+gr*0.55, fill=gc, outline="", tags="dyn")
    left = x - r*1.15 - lx; right = x + r*1.15 - lx
    def bell_top(xx):
        dx = (xx - (x-lx))/r; return y - r*(0.80 - 0.45*dx*dx - 0.30*abs(dx))
    def bell_bot(xx):
        dx = (xx - (x-lx))/r; return y + r*(0.10 - 0.05*dx*dx)
    for k in range(24):
        fx0 = k/24; fx1 = (k+1)/24; x0 = left + (right-left)*fx0; x1 = left + (right-left)*fx1; mid_x = (x0+x1)/2
        col = lerp(_grad_colour(LUMEN_BELL_PAL, fx0), rim, 0.35)
        canvas.create_rectangle(x0, bell_top(mid_x)-r*0.10, x1, bell_bot(mid_x)-r*0.05, fill=col, outline="", tags="dyn")
    for k in range(24):
        fx0 = k/24; fx1 = (k+1)/24; x0 = left + (right-left)*fx0; x1 = left + (right-left)*fx1; mid_x = (x0+x1)/2
        col = lerp(_grad_colour(LUMEN_BELL_PAL, fx0), body_h, 0.55)
        canvas.create_rectangle(x0, bell_top(mid_x), x1, bell_bot(mid_x), fill=col, outline="", tags="dyn")
    
    er = s * 0.06; ex = x - lx; ey = y - r*0.45
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
    pr = _seat_pupil_radius("Lumen", er * 0.85)
    canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")

    for sp in LUMEN_SPARKS:
        sp["age"] += 0.012 * sp["speed"] * (1.0 - QUIET["level"]*0.7)
        if sp["age"] > 1.0: sp["age"] = 0.0; sp["speed"] = random.uniform(0.5,0.8); sp["lane"] = random.randint(0,2)
        lane_off = (sp["lane"]-1) * r * 0.35; px = x - lx + lane_off + math.sin(SCENE["t"]*2.0 + sp["lane"])*r*0.05
        py = y + r*0.10 - sp["age"] * r*0.80; fade = math.sin(sp["age"] * math.pi)
        pulse_a = clamp(SEAT_NETS["Lumen"].confidence() * 0.7 + SEAT_NETS["Lumen"].last_out * 0.3, 0.0, 1.0)
        rr = r * (0.045 + 0.030 * pulse_a) * fade
        if rr < 0.4: continue
        canvas.create_oval(px-rr*2.6, py-rr*2.6, px+rr*2.6, py+rr*2.6, fill=lerp(rim, hue(WATER_BOT), 0.55), outline="", tags="dyn")
        canvas.create_oval(px-rr, py-rr, px+rr, py+rr, fill="#ffffff", outline="", tags="dyn")
    for i in range(5):
        offset = (i - 2.0) * r * 0.30; phase = i * 0.6; pts = []
        for k in range(26):
            f = k/25; wave = math.sin(SCENE["t"]*1.6 + phase - f*4.2); amp = r * (0.05 + 0.35 * math.sin(f*3.14))
            ox = x - lx + offset + d*lean*f*r*0.15; pts.append((ox + wave*amp, y + r*4.5*f, f))
        for k in range(len(pts)-1):
            f0 = pts[k][2]; col = lerp(_grad_colour(LUMEN_BELL_PAL, f0), body_h, 0.30); w = max(1, int(r * 0.06 * (1 - 0.35*f0)))
            canvas.create_line(pts[k][0], pts[k][1], pts[k+1][0], pts[k+1][1], fill=col, width=w, capstyle="round", tags="dyn")

VERTEX_BODY = [(0.0,"#5a1a70"),(0.25,"#8a2a8a"),(0.50,"#c85090"),(0.75,"#e87870"),(1.0,"#ffd060")]

def draw_vertex(c):
    x, y = c["x"], c["y"]; s = c["scale"] * H * ZOOM_FIXED * 0.9
    breath = breath_offset("Vertex", amp=0.10); s *= (1.0 + breath * 0.20)
    d = c["dir"]; lean = c["lean"]; lx = d * lean * s * 0.10
    body_h = hue(SEAT_BODY["Vertex"]); rim = _seat_rim("Vertex")
    for side in (-1, 1):
        for i in range(3):
            base_y = y + s*(0.25 + i*0.24); base_x = x + lx + side*s*0.55
            scurry = math.sin(SCENE["t"]*6.0 + i*1.0 + side*0.7) * (1.0 - QUIET["level"]*0.8)
            knee_x = x + lx + side*s*(1.15 + scurry*0.05); knee_y = base_y - s*0.05 + i*s*0.06 + scurry*s*0.04
            tip_x  = x + lx + side*s*(1.55 + scurry*0.10); tip_y  = base_y + s*0.55 + scurry*s*0.10
            canvas.create_line(base_x+(-0.4*s*0.18), base_y+(-0.9*s*0.18), knee_x+(-0.4*s*0.18), knee_y+(-0.9*s*0.18), fill=rim, width=max(2,int(s*0.09)), capstyle="round", tags="dyn")
            canvas.create_line(knee_x+(-0.4*s*0.18), knee_y+(-0.9*s*0.18), tip_x+(-0.4*s*0.18), tip_y+(-0.9*s*0.18), fill=rim, width=max(2,int(s*0.08)), capstyle="round", tags="dyn")
            canvas.create_line(base_x, base_y, knee_x, knee_y, fill=lerp(body_h,"#000000",0.4), width=max(2,int(s*0.075)), capstyle="round", tags="dyn")
            canvas.create_line(knee_x, knee_y, tip_x, tip_y, fill=lerp(body_h,"#000000",0.4), width=max(2,int(s*0.065)), capstyle="round", tags="dyn")
    rx = s*1.08; ry = s*0.74; ys = int(y-ry); ye = int(y+ry)
    canvas.create_oval(x+lx-rx-s*0.16, y-ry-s*0.16, x+lx+rx+s*0.16, y+ry+s*0.16, fill=rim, outline="", tags="dyn")
    for yy in range(ys, ye+1):
        f = (yy-ys)/max(1, ye-ys); dy = (yy-y)/ry
        if abs(dy) >= 1: continue
        hw = rx * math.sqrt(1 - dy*dy); col = lerp(_grad_colour(VERTEX_BODY, f), body_h, 0.55)
        canvas.create_line(x+lx-hw, yy, x+lx+hw, yy, fill=col, width=1, tags="dyn")
    rng = random.Random(int(c["home_x"]) + 11); pulse_a = clamp(SEAT_NETS["Vertex"].confidence() * 0.7 + SEAT_NETS["Vertex"].last_out * 0.3, 0.0, 1.0)
    for _ in range(14):
        dx = rng.uniform(-0.85,0.85)*s; dy = rng.uniform(-0.55,0.55)*s
        if (dx/(1.08*s))**2 + (dy/(0.74*s))**2 > 1: continue
        rr = s * rng.uniform(0.025,0.045); base_col = rng.choice([hue("#fff8d0"), hue("#ffe8a0"), hue("#c8e8ff")])
        col = lerp(base_col, hue(SEAT_RIM["Vertex"]), pulse_a * 0.7)
        canvas.create_oval(x+lx+dx-rr, y+dy-rr, x+lx+dx+rr, y+dy+rr, fill=col, outline="", tags="dyn")
    for ex in (-0.42, 0.42):
        bx = x + lx + ex * s; by = y - s*0.28; tx = bx + d * lean * s * 0.10; ty = by - s*0.55
        canvas.create_line(bx, by, tx, ty, fill=lerp(body_h,"#000000",0.5), width=max(1,int(s*0.06)), tags="dyn")
        rr = s * 0.13; canvas.create_oval(tx-rr, ty-rr, tx+rr, ty+rr, fill=lerp(body_h,"#ffffff",0.85), outline="", tags="dyn")
        pr = _seat_pupil_radius("Vertex", rr * 0.85); canvas.create_oval(tx-pr, ty-pr, tx+pr, ty+pr, fill="#050510", outline="", tags="dyn")

PRISM_BODY = [(0.0,"#8a4818"),(0.30,"#c87820"),(0.55,"#ffd060"),(0.78,"#ffe8a0"),(1.0,"#fff8d8")]

def draw_prism(c):
    x, y = c["x"], c["y"]; s = c["scale"] * H * ZOOM_FIXED
    breath = breath_offset("Prism", amp=0.04); d = c["dir"]; lean = c["lean"]; lx = d * lean * s * 0.08; y += breath * s * 0.1
    body_h = hue(SEAT_BODY["Prism"]); rim = _seat_rim("Prism")
    pts = [(x+0.42*s+lx,y),(x+0.28*s+lx,y-0.50*s),(x+0.05*s+lx,y-0.85*s),(x-0.10*s+lx,y-1.00*s),(x-0.30*s+lx,y-0.75*s),(x-0.55*s+lx,y-0.30*s),(x-0.60*s+lx,y),(x-0.55*s+lx,y+0.30*s),(x-0.30*s+lx,y+0.75*s),(x-0.10*s+lx,y+1.00*s),(x+0.05*s+lx,y+0.85*s),(x+0.28*s+lx,y+0.50*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(pts,-0.4,-0.9,s*0.20) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    tail_up = [(x-0.10*s+lx,y-1.00*s),(x+0.05*s+lx+d*lean*s*0.10,y-1.40*s),(x-0.20*s+lx+d*lean*s*0.15,y-1.85*s),(x-0.65*s+lx,y-1.35*s),(x-0.55*s+lx,y-0.30*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(tail_up,-0.4,-0.9,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    tail_dn = [(x-0.10*s+lx,y+1.00*s),(x+0.05*s+lx+d*lean*s*0.10,y+1.40*s),(x-0.20*s+lx+d*lean*s*0.15,y+1.85*s),(x-0.65*s+lx,y+1.35*s),(x-0.55*s+lx,y+0.30*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(tail_dn,-0.4,-0.9,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in tail_up for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*[p for pt in tail_dn for p in pt], fill=body_h, outline="", smooth=True, tags="dyn")
    ys = [p[1] for p in pts]; y_min, y_max = min(ys), max(ys); y_rng = max(1, y_max - y_min); n = len(pts)
    for yy in range(int(y_min), int(y_max)+1):
        f = (yy-y_min)/y_rng; xs = []
        for i in range(n):
            p0 = pts[i]; p1 = pts[(i+1)%n]
            if p1[1] != p0[1] and min(p0[1],p1[1]) <= yy <= max(p0[1],p1[1]):
                loc = (yy-p0[1])/(p1[1]-p0[1]); xs.append(p0[0] + (p1[0]-p0[0])*loc)
        if len(xs) >= 2:
            xs.sort(); col = lerp(_grad_colour(PRISM_BODY, f), body_h, 0.60); canvas.create_line(xs[0], yy, xs[-1], yy, fill=col, width=1, tags="dyn")
    er = s * 0.09; ex = x + lx + 0.18*s; ey = y - 0.22*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.9), outline="", tags="dyn")
    pr = _seat_pupil_radius("Prism", er * 0.85); canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for f in (0.2, 0.5, 0.8): draw_pulse_dot(x-s*0.3, y-s*(1.0-f*2.0), s*0.05, "Prism")

RIPPLE_PAL = [(0.0,"#ffb8d8"),(0.15,"#ff80b8"),(0.35,"#e060b0"),(0.55,"#b058c0"),(0.75,"#8050b8"),(1.0,"#5038a0")]

def draw_ripple(c):
    x, y = c["x"], c["y"]; s = c["scale"] * H * ZOOM_FIXED
    breath = breath_offset("Ripple", amp=0.08); d = c["dir"]; lean = c["lean"]; lx = d * lean * s * 0.06; y += breath * s * 0.3
    body_h = hue(SEAT_BODY["Ripple"]); rim = _seat_rim("Ripple")
    tail_pts = [(x-0.08*s+lx,y+0.50*s),(x-0.20*s+lx,y+0.72*s),(x-0.32*s+lx,y+0.95*s),(x-0.28*s+lx,y+1.18*s),(x-0.05*s+lx,y+1.28*s),(x+0.20*s+lx,y+1.18*s),(x+0.30*s+lx,y+0.98*s),(x+0.20*s+lx,y+0.82*s),(x+0.00*s+lx,y+0.78*s),(x-0.10*s+lx,y+0.86*s),(x-0.10*s+lx,y+0.98*s),(x-0.02*s+lx,y+1.04*s)]
    for k in range(len(tail_pts)-1):
        f0 = k/(len(tail_pts)-1); x1, y1 = tail_pts[k]; x2, y2 = tail_pts[k+1]
        w = max(2, int(s*0.16 * (1.0 - 0.70*f0)))
        canvas.create_line(x1-0.4*s*0.16, y1-0.9*s*0.16, x2-0.4*s*0.16, y2-0.9*s*0.16, fill=rim, width=w, capstyle="round", tags="dyn")
        col = lerp(_grad_colour(RIPPLE_PAL, 0.85 + 0.15*((f0+(k+1)/(len(tail_pts)-1))/2)), body_h, 0.55)
        canvas.create_line(x1, y1, x2, y2, fill=col, width=w, capstyle="round", tags="dyn")
    body_pts = [(x+0.10*s+lx,y-0.85*s),(x+0.15*s+lx,y-0.55*s),(x+0.30*s+lx,y-0.15*s),(x+0.24*s+lx,y+0.20*s),(x+0.10*s+lx,y+0.50*s),(x-0.10*s+lx,y+0.50*s),(x-0.22*s+lx,y+0.15*s),(x-0.26*s+lx,y-0.20*s),(x-0.26*s+lx,y-0.55*s),(x-0.22*s+lx,y-0.82*s),(x-0.14*s+lx,y-0.88*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(body_pts,-0.4,-0.9,s*0.18) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    ys = [p[1] for p in body_pts]; y_min, y_max = min(ys), max(ys); y_rng = max(1, y_max - y_min); n = len(body_pts)
    for yy in range(int(y_min), int(y_max)+1):
        f = (yy-y_min)/y_rng; xs = []
        for i in range(n):
            p0 = body_pts[i]; p1 = body_pts[(i+1)%n]
            if p1[1] != p0[1] and min(p0[1],p1[1]) <= yy <= max(p0[1],p1[1]):
                loc = (yy-p0[1])/(p1[1]-p0[1]); xs.append(p0[0] + (p1[0]-p0[0])*loc)
        if len(xs) >= 2:
            xs.sort(); col = lerp(_grad_colour(RIPPLE_PAL, f), body_h, 0.60); canvas.create_line(xs[0], yy, xs[-1], yy, fill=col, width=1, tags="dyn")
    hx = x + 0.05*s + lx + d * lean * s * 0.15; hy = y - 1.10*s - lean * s * 0.05
    head_pts = [(hx-0.20*s,hy+0.10*s),(hx-0.16*s,hy-0.24*s),(hx+0.02*s,hy-0.32*s),(hx+0.18*s,hy-0.22*s),(hx+0.32*s,hy-0.14*s),(hx+0.58*s,hy-0.16*s),(hx+0.74*s,hy-0.14*s),(hx+0.62*s,hy-0.02*s),(hx+0.32*s,hy+0.08*s),(hx+0.18*s,hy+0.20*s),(hx+0.05*s,hy+0.22*s)]
    canvas.create_polygon(*[p for pt in _rim_offset(head_pts,-0.4,-0.9,s*0.16) for p in pt], fill=rim, outline="", smooth=True, tags="dyn")
    canvas.create_polygon(*head_pts, fill=lerp(_grad_colour(RIPPLE_PAL, 0.10), body_h, 0.55), outline="", smooth=True, tags="dyn")
    for i in range(7):
        bx = hx + (-0.05 + i*0.062)*s; by = hy - 0.35*s; peak = s*(0.20 if i % 2 == 1 else 0.10)
        canvas.create_polygon(bx-s*0.022, by, bx+s*0.010, by-peak, bx+s*0.022, by, fill=rim, outline="", tags="dyn")
    er = s * 0.058; ex = x + lx + 0.13*s; ey = y - 1.16*s
    canvas.create_oval(ex-er, ey-er, ex+er, ey+er, fill=lerp(body_h,"#ffffff",0.9), outline="", tags="dyn")
    pr = _seat_pupil_radius("Ripple", er * 0.85); canvas.create_oval(ex-pr, ey-pr, ex+pr, ey+pr, fill="#050510", outline="", tags="dyn")
    for f in (0.2, 0.5, 0.8):
        idx = int(f * (len(body_pts)-1)); idx = min(idx, len(body_pts)-2); local = f * (len(body_pts)-1) - idx
        px = body_pts[idx][0] + (body_pts[idx+1][0]-body_pts[idx][0])*local; py = body_pts[idx][1] + (body_pts[idx+1][1]-body_pts[idx][1])*local
        draw_pulse_dot(px, py, s * 0.045, "Ripple")

CREATURE_DRAW = {"turtle":draw_solon,"jelly":draw_lumen,"crab":draw_vertex,"angel":draw_prism,"seahorse":draw_ripple}

def draw_creatures():
    for c in CREATURES:
        cx, cy = cam(c["x"], c["y"])
        save = (c["x"], c["y"], c["scale"]); c["x"], c["y"] = cx, cy; c["scale"] *= ZOOM_FIXED
        draw_reflection(c)
        c["x"], c["y"], c["scale"] = save
    for c in CREATURES:
        cx, cy = cam(c["x"], c["y"])
        save = (c["x"], c["y"], c["scale"]); c["x"], c["y"] = cx, cy; c["scale"] *= ZOOM_FIXED
        CREATURE_DRAW[c["name"]](c)
        c["x"], c["y"], c["scale"] = save

# --- END OF CHUNK 4 / 5 ---

# ============ WORLD & ENVIRONMENT (LAYERS 21 & 22) ============
WORLD_SPAN = W*3.0; FOREGROUND_SPAN = W*4.5; NEAR_SPAN = W*4.0

def floor_top_y(wx): return FLOOR_Y + math.sin(wx*0.0075)*H*0.010 + math.sin(wx*0.019+1.3)*H*0.005 + math.sin(wx*0.041+2.7)*H*0.002
def _haze(col, t): return lerp(col, hue(HAZE), t)
def _darken_by_quiet(col, amount=0.35): return lerp(col, "#000000", QUIET["level"] * amount)

def _valence_tint(col):
    # Layer 24: Water colour as valence readout
    v = VALENCE["level"]
    if v > 0.55: return lerp(col, hue(GLOW_WARM), (v - 0.55) * 0.75)
    if v < 0.45: return lerp(col, hue(GLOW_COOL), (0.45 - v) * 0.60)
    return col

def draw_water():
    stops = [(0.00,hue(WATER_TOP)),(0.14,hue(WATER_HIGH)),(0.40,hue(WATER_MID)),(0.68,hue(WATER_LOW)),(0.88,hue(WATER_DEEP)),(1.00,hue(WATER_BOT))]
    pulse = 0.97 + 0.03 * math.sin(PULSE["phase"]); te = touch_energy()
    for i in range(60):
        t = i/60; col = stops[-1][1]
        for j in range(len(stops)-1):
            if stops[j][0] <= t <= stops[j+1][0]:
                col = lerp(stops[j][1], stops[j+1][1], (t-stops[j][0])/(stops[j+1][0]-stops[j][0])); break
        col = lerp("#000000", col, pulse)
        if te > 0.01: col = lerp(col, hue(GLOW_WARM), te*0.06)
        col = _darken_by_quiet(col, 0.40); col = _valence_tint(col)
        canvas.create_rectangle(0, int(H*t), W, int(H*(i+1)/60)+2, fill=col, outline="", tags="bg")

STAR_DATA = []
def make_stars():
    rng = random.Random(606)
    for _ in range(46): STAR_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"y":rng.uniform(0.02,0.45)*H,"r":rng.uniform(0.5,1.3),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.3,0.8)})
def draw_stars():
    night = night_amount()
    for s in STAR_DATA:
        sx = (s["wx"] - SCENE["scroll_x"]*0.15) % WORLD_SPAN
        if sx > W+4: sx -= WORLD_SPAN
        if sx < -4 or sx > W+4: continue
        pulse = (0.4 + 0.6*math.sin(SCENE["t"]*s["speed"]+s["phase"])) * (1.0 - QUIET["level"]*0.4)
        r = s["r"] * (0.55+0.55*pulse) * (1.0 + night*0.4)
        col = lerp(hue(GLOW_COOL), hue(GLOW_WARM), max(0.0, 1.0 - (s["y"]/H)*2.5))
        canvas.create_oval(sx-r, s["y"]-r, sx+r, s["y"]+r, fill=col, outline="", tags="bg")

def draw_god_rays():
    intensity = (0.14 + MOOD["current"] * 0.20) * 0.5
    intensity *= (1.0 - night_amount()*0.60) * (1.0 - QUIET["level"] * 0.85)
    if intensity < 0.02: return
    src_x = LIGHT_X + math.sin(SCENE["t"]*0.05)*W*0.15
    for i in range(4):
        rx = src_x + (i-1.5)*W*0.10 + math.sin(SCENE["t"]*0.3 + i*1.7)*W*0.008
        col = lerp(hue(WATER_BOT), hue(GLOW_WARM), intensity*0.70)
        canvas.create_polygon(rx-W*0.025, SURFACE_Y, rx+W*0.025, SURFACE_Y, rx+W*0.14, SURFACE_Y+H*0.72, rx-W*0.14, SURFACE_Y+H*0.72, fill=col, outline="", stipple="gray50", tags="bg")

FAR_DATA = []
def make_far():
    rng = random.Random(101)
    for i in range(14): FAR_DATA.append({"kind":rng.choice(["hump","peak","slab"]),"wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.10,0.40),"h":H*rng.uniform(0.03,0.14),"colour":rng.choice(["#3a0a18","#4a1030","#5a1a3a"]),"seed":rng.randint(0,9999)})
def draw_far():
    sx_off = SCENE["scroll_x"]*0.25
    for it in FAR_DATA:
        sx = (it["wx"] - sx_off) % WORLD_SPAN
        if sx > W+it["w"]: sx -= WORLD_SPAN
        if sx < -it["w"] or sx > W+it["w"]: continue
        rng = random.Random(it["seed"]); k = it["kind"]; base_y = floor_top_y(it["wx"]) - H*0.004
        col = _darken_by_quiet(_haze(it["colour"], 0.30), 0.5)
        if k == "slab": canvas.create_rectangle(sx-it["w"]*0.5, base_y-it["h"], sx+it["w"]*0.5, base_y, fill=col, outline="", tags="bg"); continue
        pts = []
        for i in range(9):
            f = i/8; shape = math.sin(f*math.pi)**(0.6 if k=="peak" else 1.0) + rng.uniform(-0.06,0.06)
            pts.extend([sx - it["w"]*0.5 + it["w"]*f, base_y - it["h"]*shape])
        pts.extend([sx+it["w"]*0.5, base_y]); pts.extend([sx-it["w"]*0.5, base_y])
        canvas.create_polygon(*pts, fill=col, outline="", smooth=True, tags="bg")

def draw_floor():
    steps = 60; top = [(W*i/steps, floor_top_y(W*i/steps + SCENE["scroll_x"])) for i in range(steps+1)]
    poly = []
    for (x,y) in top: poly.extend([x,y])
    poly.extend([W,H]); poly.extend([0,H])
    canvas.create_polygon(*poly, fill=_darken_by_quiet(hue(SAND),0.35), outline="", tags="bg")
    lip = []
    for (x,y) in top: lip.extend([x,y])
    for (x,y) in reversed(top): lip.extend([x, y+H*0.006])
    canvas.create_polygon(*lip, fill=_darken_by_quiet(hue(SAND_LIT),0.35), outline="", tags="bg")
    for off, col in [(0.055,_darken_by_quiet(hue(SAND_DARK),0.35)), (0.12,_darken_by_quiet(hue(SAND_DEEP),0.35))]:
        band = []
        for i in range(steps+1): band.extend([W*i/steps, floor_top_y(W*i/steps + SCENE["scroll_x"]) + H*off])
        band.extend([W,H]); band.extend([0,H])
        canvas.create_polygon(*band, fill=col, outline="", tags="bg")

CAUSTIC_DATA = []
def make_caustics():
    rng = random.Random(404)
    for _ in range(22): CAUSTIC_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"wy_off":rng.uniform(0.008,0.10),"r":rng.uniform(W*0.035,W*0.090),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.4,0.8)})
def draw_caustics():
    intensity = (0.65 + MOOD["current"] * 0.35) * (1.0 - night_amount()*0.75) * (1.0 - QUIET["level"]*0.9)
    if intensity < 0.03: return
    for c in CAUSTIC_DATA:
        sx = (c["wx"] - SCENE["scroll_x"]*0.98) % WORLD_SPAN
        if sx > W+c["r"]: sx -= WORLD_SPAN
        if sx < -c["r"] or sx > W+c["r"]: continue
        pulse = 0.5 + 0.5*math.sin(SCENE["t"]*c["speed"]+c["phase"])
        rr = c["r"] * (0.55+0.55*pulse); base_y = floor_top_y(c["wx"]) + c["wy_off"]*H
        canvas.create_oval(sx-rr, base_y-rr*0.22, sx+rr, base_y+rr*0.22, fill=lerp(hue(SAND_LIT), hue(GLOW_WARM), intensity*0.65), outline="", stipple="gray50", tags="bg")

MID_DATA = []
def make_mid():
    rng = random.Random(201)
    for i in range(10): MID_DATA.append({"kind":rng.choice(["rock","spire"]),"wx":rng.uniform(0,WORLD_SPAN),"w":W*rng.uniform(0.05,0.22),"h":H*rng.uniform(0.07,0.18),"colour":rng.choice(["#1a0408","#280810","#380c18"]),"seed":rng.randint(0,9999)})
def draw_mid():
    sx_off = SCENE["scroll_x"]*0.55
    for it in MID_DATA:
        sx = (it["wx"] - sx_off) % WORLD_SPAN
        if sx > W+it["w"]: sx -= WORLD_SPAN
        if sx < -it["w"] or sx > W+it["w"]: continue
        rng = random.Random(it["seed"]); k = it["kind"]; base_y = floor_top_y(it["wx"]) - H*0.002
        col = _darken_by_quiet(_haze(it["colour"], 0.15), 0.5)
        pts = []
        for i in range(9):
            f = i/8; shape = math.sin(f*math.pi)**(0.4 if k=="spire" else 0.75) + rng.uniform(-0.08,0.08)
            pts.extend([sx - it["w"]*0.5 + it["w"]*f, base_y - it["h"]*shape])
        pts.extend([sx+it["w"]*0.5, base_y]); pts.extend([sx-it["w"]*0.5, base_y])
        canvas.create_polygon(*pts, fill=col, outline="", smooth=True, tags="bg")

LUMIN_DATA = []
def make_lumin():
    rng = random.Random(303)
    for i in range(14):
        wx = rng.uniform(0, WORLD_SPAN); h = rng.uniform(H*0.10, H*0.22); nb = rng.randint(3,6)
        buds = [{"dx":rng.uniform(-W*0.03, W*0.03),"dy":rng.uniform(-H*0.03, 0),"r":rng.uniform(0.6, 1.0)} for _ in range(nb)]
        LUMIN_DATA.append({"wx":wx,"h":h,"buds":buds,"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
def draw_lumin():
    sx_off = SCENE["scroll_x"]*0.85
    for i, l in enumerate(LUMIN_DATA):
        sx = (l["wx"] - sx_off) % WORLD_SPAN
        if sx > W+40: sx -= WORLD_SPAN
        if sx < -40 or sx > W+40: continue
        base_y = floor_top_y(l["wx"])
        top_sway = math.sin(SCENE["t"]*0.9 + l["phase"])*W*0.012 * (1.0 - QUIET["level"]*0.7)
        top_x = sx + top_sway; top_y = base_y - l["h"]
        col_pool = [hue(GLOW_WARM), hue(GLOW_COOL), hue(GLOW_GREEN), hue(GLOW_PINK)]
        for j, b in enumerate(l["buds"]):
            bx = top_x + b["dx"]; by = top_y + b["dy"]
            pulse = 0.5 + 0.5*math.sin(SCENE["t"]*1.5 + l["phase"] + j*0.7) + QUIET["level"]*0.4
            br = W*0.008 * b["r"] * (0.7 + 0.5*pulse); col = col_pool[(i+j) % len(col_pool)]
            canvas.create_oval(bx-br*3.5, by-br*3.5, bx+br*3.5, by+br*3.5, fill=lerp(hue(WATER_BOT), col, 0.20), outline="", tags="bg")
            canvas.create_oval(bx-br, by-br, bx+br, by+br, fill=col, outline="", tags="bg")

GLOW_DATA = []
def make_glow():
    rng = random.Random(505); cols = [hue(GLOW_WARM), hue(GLOW_COOL), hue(GLOW_GREEN), hue(GLOW_PINK), "#ffffff"]
    for _ in range(28): GLOW_DATA.append({"wx":rng.uniform(0,WORLD_SPAN),"wy":rng.uniform(0.10,0.75)*H,"r":rng.uniform(0.6,1.8),"col":rng.choice(cols),"phase":rng.uniform(0,6.28),"speed":rng.uniform(0.4,1.0)})
def draw_glow():
    for g in GLOW_DATA:
        sx = (g["wx"] - SCENE["scroll_x"]*0.4) % WORLD_SPAN
        if sx > W+20: sx -= WORLD_SPAN
        if sx < -20 or sx > W+20: continue
        pulse = 0.5 + 0.5*math.sin(SCENE["t"]*g["speed"]*(1.0 - QUIET["level"]*0.6) + g["phase"])
        r = g["r"]*(0.6+0.6*pulse); hr = r*3
        canvas.create_oval(sx-hr, g["wy"]-hr, sx+hr, g["wy"]+hr, fill=lerp(hue(WATER_BOT), g["col"], 0.15), outline="", tags="bg")
        canvas.create_oval(sx-r, g["wy"]-r, sx+r, g["wy"]+r, fill=g["col"], outline="", tags="bg")

SCHOOL = []
def make_school():
    rng = random.Random(707)
    for _ in range(12): SCHOOL.append({"wx":rng.uniform(0,WORLD_SPAN),"y":rng.uniform(H*0.22,H*0.68),"size":rng.uniform(0.0030,0.0036)*H,"colour":rng.choice(["#c8d0e0","#a0b0d0","#e0b0d0"]),"phase":rng.uniform(0,6.28),"dir":-1})
def draw_school():
    for f in SCHOOL:
        sx = (f["wx"] - SCENE["scroll_x"]*0.9) % WORLD_SPAN
        if sx > W+20: sx -= WORLD_SPAN
        if sx < -20 or sx > W+20: continue
        col = _darken_by_quiet(_haze(f["colour"], 0.25), 0.5); s = f["size"]; d = f["dir"]
        canvas.create_oval(sx-s*1.1, f["y"]-s*0.55, sx+s*1.1, f["y"]+s*0.55, fill=col, outline="", tags="bg")
        canvas.create_polygon(sx-d*s*1.0, f["y"], sx-d*s*1.9, f["y"]-s*0.70, sx-d*s*1.9, f["y"]+s*0.70, fill=col, outline="", tags="bg")
def update_school(dt):
    for f in SCHOOL:
        f["phase"] += dt*2.0 * (1.0 - QUIET["level"]*0.7)
        f["wx"] -= SCENE["scroll_speed"]*0.6*dt*60; f["y"] += math.sin(f["phase"])*dt*6
        f["y"] = clamp(f["y"], H*0.20, H*0.72)
        if f["wx"] < -W*0.15: f["wx"] = WORLD_SPAN + random.uniform(0, W*0.3); f["y"] = random.uniform(H*0.22, H*0.68)

NEAR_DATA = []
def make_near():
    rng = random.Random(808)
    for _ in range(14): NEAR_DATA.append({"kind":rng.choice(["kelp","grass","frond"]),"wx":rng.uniform(0,NEAR_SPAN),"h":H*rng.uniform(0.18,0.55),"w":W*rng.uniform(0.018,0.055),"blades":rng.randint(3,6),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
def draw_near():
    sx_off = SCENE["scroll_x"]*1.15; base_y = H*1.02; col = hue("#080202")
    for it in NEAR_DATA:
        sx = (it["wx"] - sx_off) % NEAR_SPAN
        if sx > W+it["w"]*3: sx -= NEAR_SPAN
        if sx < -it["w"]*3 or sx > W+it["w"]*3: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        if k in ("kelp","grass"):
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2) * it["w"] * 0.4
                sway = math.sin(SCENE["t"]*0.8*(1.0 - QUIET["level"]*0.6) + it["phase"] + j)*W*0.022
                pts = [(sx+off+sway*(k2/7)**2, base_y - it["h"]*(k2/7)) for k2 in range(8)]
                canvas.create_line(*[c for p in pts for c in p], fill=col, width=max(2,int(W*0.016)), smooth=True, capstyle="round", tags="near")
        else:
            for j in range(it["blades"]):
                a = -math.pi/2 + (j - (it["blades"]-1)/2)*0.28; length = it["h"] * rng.uniform(0.7,1.0)
                canvas.create_line(sx, base_y, sx + math.cos(a)*length, base_y + math.sin(a)*length, fill=col, width=max(2,int(W*0.018)), smooth=True, capstyle="round", tags="near")

FOREGROUND_DATA = []
def make_foreground():
    rng = random.Random(909)
    for _ in range(8): FOREGROUND_DATA.append({"kind":rng.choice(["kelp","grass","spire"]),"wx":rng.uniform(0,FOREGROUND_SPAN),"h":H*rng.uniform(0.25,0.70),"w":W*rng.uniform(0.025,0.095),"blades":rng.randint(4,7),"phase":rng.uniform(0,6.28),"seed":rng.randint(0,9999)})
def draw_foreground():
    sx_off = SCENE["scroll_x"]*1.5; base_y = H*1.05; col = "#000000"
    for it in FOREGROUND_DATA:
        sx = (it["wx"] - sx_off) % FOREGROUND_SPAN
        if sx > W+it["w"]*3: sx -= FOREGROUND_SPAN
        if sx < -it["w"]*3 or sx > W+it["w"]*3: continue
        rng = random.Random(it["seed"]); k = it["kind"]
        if k == "kelp":
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2)*it["w"]*0.4
                sway = math.sin(SCENE["t"]*0.7*(1.0 - QUIET["level"]*0.6) + it["phase"] + j)*W*0.025
                pts = [(sx+off+sway*(k2/7)**2, base_y - it["h"]*(k2/7)) for k2 in range(8)]
                canvas.create_line(*[c for p in pts for c in p], fill=col, width=max(3,int(W*0.020)), smooth=True, capstyle="round", tags="fg")
        elif k == "grass":
            for j in range(it["blades"]):
                off = (j - (it["blades"]-1)/2)*it["w"]*0.35
                sway = math.sin(SCENE["t"]*1.2 + it["phase"] + j)*W*0.03
                pts = [(sx+off+sway*(k2/5), base_y - it["h"]*(k2/5)) for k2 in range(6)]
                canvas.create_line(*[c for p in pts for c in p], fill=col, width=max(3,int(W*0.022)), smooth=True, capstyle="round", tags="fg")
        else:
            pts = [(sx-it["w"]*0.5, base_y),(sx-it["w"]*0.3, base_y-it["h"]*0.5),(sx, base_y-it["h"]),(sx+it["w"]*0.3, base_y-it["h"]*0.5),(sx+it["w"]*0.5, base_y)]
            canvas.create_polygon(*[c for p in pts for c in p], fill=col, outline="", smooth=True, tags="fg")

def update_scroll(dt):
    mood_speed = (0.5 + MOOD["current"]*0.9) * (1.0 - QUIET["level"]*0.7)
    SCENE["scroll_speed"] = mood_speed * (1.0 - INTERO["chamber_strain"]*0.4)
    SCENE["scroll_x"] += SCENE["scroll_speed"]*dt*60.0

def draw_touch_glow():
    te = touch_energy()
    if te < 0.05: return
    cx, cy = cam(EXTERO["touch_x"], EXTERO["touch_y"])
    base_r = min(W,H)*0.022; r = base_r*(0.45 + 0.55*te)
    col = lerp(hue(GLOW_COOL), hue(GLOW_WARM), 0.35 + MOOD["current"]*0.55)
    canvas.create_oval(cx-r*2, cy-r*2, cx+r*2, cy+r*2, fill=lerp(hue(WATER_BOT), col, te*0.10), outline="", tags="dyn")
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=lerp(hue(WATER_BOT), col, te*0.45), outline="", tags="dyn")

# ============ LAYER 32: NESSY ============
def _nessy_arc(cx, base_y, rx, ry, steps=20):
    return [(cx + math.cos(math.pi*(1 - i/steps))*rx, base_y - math.sin(math.pi*(1 - i/steps))*ry) for i in range(steps+1)]

def _nessy_rim_body(pts, offset, rim_col, body_col):
    canvas.create_polygon(*[p for pt in [(x+offset[0], y+offset[1]) for x,y in pts] for p in pt], fill=rim_col, outline="", smooth=True, tags="nessy")
    canvas.create_polygon(*[p for pt in pts for p in pt], fill=body_col, outline="", smooth=True, tags="nessy")

def draw_nessy():
    s = H * 0.055 * ZOOM_FIXED
    cx, cy = cam(NESSY["x"], H * 0.13 + NESSY["dip"] * H * 0.04)
    rim = hue(NESSY_RIM_BASE) if NESSY["bright"] <= 0.02 else lerp(hue(NESSY_RIM_BASE), hue(GLOW_WARM), NESSY["bright"] * 0.5)

    hump_r = s * 1.0
    for i in range(3):
        hx = cx - s * 1.05 * (i + 1)
        _nessy_rim_body(_nessy_arc(hx, cy + s*0.05, hump_r, hump_r * 0.95), (0,-6), rim, NESSY_BODY)

    neck_pts = []
    for i in range(17):
        f = i / 16
        y = cy + s*0.05 - f * s * 2.5
        curve = (math.sin(f * math.pi * 1.2) * s * 0.55 - f * s * 0.15)
        x_center = cx + s * 0.15 + curve
        w = s * (0.55 - f * 0.25)
        neck_pts.append((x_center - w, y))
    for i in range(16, -1, -1):
        f = i / 16
        y = cy + s*0.05 - f * s * 2.5
        curve = (math.sin(f * math.pi * 1.2) * s * 0.55 - f * s * 0.15)
        x_center = cx + s * 0.15 + curve
        w = s * (0.55 - f * 0.25)
        neck_pts.append((x_center + w, y))
    _nessy_rim_body(neck_pts, (0, -5), rim, NESSY_BODY)

    head_cx = cx + s * 0.15 + (math.sin(math.pi * 1.2) * s * 0.55 - s * 0.15)
    head_cy = cy + s*0.05 - s * 2.5
    head_pts = [(head_cx-s*0.35, head_cy+s*0.10),(head_cx-s*0.25, head_cy-s*0.22),(head_cx+s*0.05, head_cy-s*0.28),(head_cx+s*0.45, head_cy-s*0.20),(head_cx+s*0.70, head_cy-s*0.08),(head_cx+s*0.45, head_cy+s*0.06),(head_cx+s*0.05, head_cy+s*0.14),(head_cx-s*0.25, head_cy+s*0.16)]
    _nessy_rim_body(head_pts, (0, -4), rim, NESSY_BODY)

    er = s * 0.045
    canvas.create_oval(head_cx+s*0.25-er, head_cy-s*0.05-er, head_cx+s*0.25+er, head_cy-s*0.05+er, fill=lerp(hue(GLOW_WARM), "#ffffff", NESSY["bright"]*0.6), outline="", tags="nessy")
    for i in range(3):
        hx = cx - s * 1.05 * (i + 1)
        canvas.create_oval(hx - s*0.7, cy + s*0.10, hx + s*0.7, cy + s*0.34, fill=hue("#3a1028"), outline="", tags="nessy")

# ============ RENDER PASSES ============
def render_background():
    canvas.delete("bg")
    draw_water(); draw_stars(); draw_god_rays(); draw_far(); draw_floor(); draw_caustics(); draw_mid(); draw_lumin(); draw_glow(); draw_school()

def render_nessy():
    canvas.delete("nessy"); draw_nessy()

def render_dynamic():
    canvas.delete("dyn"); draw_creatures(); draw_streams(); draw_touch_glow()

def render_near(): canvas.delete("near"); draw_near()
def render_foreground(): canvas.delete("fg"); draw_foreground()

# ============ BOOT & MAIN LOOP ============
make_far(); make_mid(); make_lumin(); make_glow(); make_school()
make_near(); make_foreground(); make_caustics(); make_stars()
make_creatures()

threading.Thread(target=_boot_audio, daemon=True).start()
print("[edencore] V7 online. 33/33 layers.")

LAST_TICK = [time.time()]
SHUTDOWN = {"saved": False}

def _final_save():
    if SHUTDOWN["saved"]: return
    SHUTDOWN["saved"] = True
    try: save_state(MOOD["current"], INTERO["chamber_strain"])
    except Exception: pass

def on_close():
    _final_save()
    try: root.destroy()
    except Exception: pass

root.protocol("WM_DELETE_WINDOW", on_close)

def tick():
    now = time.time()
    dt = clamp(now - LAST_TICK[0], 0.01, 0.15); LAST_TICK[0] = now
    SCENE["t"] += dt; PULSE["phase"] += dt*0.4
    
    # 1. Update Senses & State
    update_bell(dt); update_quiet(dt)
    read_extero(); update_intero(); compute_mood_target()
    update_mood(dt); update_strain(dt); update_breath(dt)
    
    # 2. Update Physical World & Entities
    update_scroll(dt); update_creatures(dt); update_school(dt)
    
    # 3. Update Neural/Symbolic Layers
    update_council_nets(dt)
    update_surprise(dt)
    update_valence(dt)
    update_arbiter()
    update_nessy(dt)
    run_security_audit()
    
    # 4. Update Dialogue, Rituals, Crisis
    check_crisis()
    update_crisis(dt)
    update_ritual(dt)
    update_streams(dt); update_dialogue(dt); update_rhythm(dt)
    
    # 5. Save State periodically
    if now - SCENE["last_save"] > 20:
        SCENE["last_save"] = now
        save_state(MOOD["current"], INTERO["chamber_strain"])

    # 6. Render Everything
    render_background()
    render_nessy()
    render_dynamic()
    render_near()
    render_foreground()
    
    root.after(50, tick)

render_background(); render_nessy()
try: tick()
finally: _final_save()
root.mainloop()

# ============ END EDENSHORE 3000 — V7 ============
# --- END OF CHUNK 5 / 5 ---

