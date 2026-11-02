"""Render del episodio infantil. Uso:
  python3 kids_render.py long [f0 f1 out.mp4]      -> 1920x1080
  python3 kids_render.py short T0 T1 out.mp4       -> 1080x1920 (tramo T0..T1 en segundos)
  --frames=t1,t2  guarda JPG de control"""
import sys, json, math, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 25
TL = json.load(open("kids_timeline.json")); EV = TL["events"]; TOTAL = TL["duration"]
from script import OBJS, WORDS
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(size, w="InterDisplay-Black.otf"):
    size = max(1, int(size)); k = (w, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + w, int(size))
    return _fc[k]

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def elastic(x):
    x = clamp(x)
    if x >= 1: return 1.0
    return 1 - math.cos(x * math.pi * 3.2) * math.exp(-5.2 * x)

COL = dict(sky1=(118, 197, 247), sky2=(214, 241, 255), hill1=(126, 206, 96), hill2=(92, 180, 74), dark=(40, 40, 60),
           yellow=(255, 211, 51), orange=(255, 150, 40), red=(240, 70, 70), green=(98, 196, 84), purple=(160, 100, 230),
           pink=(255, 130, 190), cyan=(110, 205, 250), blue=(60, 120, 240), white=(255, 255, 255), brown=(140, 90, 50))
RAINBOW = [COL[c] for c in ("red", "orange", "yellow", "green", "cyan", "blue", "purple", "pink", "red", "orange")]

# ---------- estado a partir de la línea de tiempo ----------
def build_blocks():
    blocks = []; cur = None
    for e in EV:
        for a in e["do"]:
            if a[0] == "scene":
                cur = dict(kind=a[1], args=list(a[2:]), start=e["start"], pops=[], numeral=None, q=[], rpops=[],
                           confetti=None, cd=[], launch=None, sa=None, sb=None, sc=None, reveal=None, popall=None, dancing=None, fill=None)
                blocks.append(cur)
            elif cur is not None:
                k = a[0]; t = e["start"]
                if k == "pop": cur["pops"].append((a[1], t))
                elif k == "numeral": cur["numeral"] = (a[1], t)
                elif k == "qmark": cur["q"].append((a[1], t))
                elif k == "rpop": cur["rpops"].append((a[1], t))
                elif k == "cd": cur["cd"].append((a[1], t))
                elif k in ("confetti", "launch", "sa", "sb", "sc", "reveal", "popall", "dancing", "fill"): cur[k] = t
    for i, b in enumerate(blocks):
        b["end"] = blocks[i + 1]["start"] if i + 1 < len(blocks) else TOTAL
    return blocks
BLOCKS = build_blocks()
SPEECH = [e for e in EV if e.get("text")]

def block_at(t):
    b = BLOCKS[0]
    for x in BLOCKS:
        if x["start"] <= t: b = x
        else: break
    return b

def speaking(t):
    for e in SPEECH:
        if e["start"] <= t < e["end"]:
            i = int((t - e["start"]) * FPS); env = e["env"]
            return e["who"], env[min(i, len(env) - 1)]
    return None, 0.0

def q_on(b, t):
    on = False
    for v, tt in b["q"]:
        if tt <= t: on = bool(v)
    return on

# ---------- sprites de objetos (supermuestreo 4x) ----------
def star_pts(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2; a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def heart(d, cx, cy, r, col):
    d.ellipse([cx - r, cy - r * 0.8, cx, cy + r * 0.2], fill=col)
    d.ellipse([cx, cy - r * 0.8, cx + r, cy + r * 0.2], fill=col)
    d.polygon([(cx - r * 0.97, cy - r * 0.15), (cx + r * 0.97, cy - r * 0.15), (cx, cy + r * 1.0)], fill=col)

def obj_sprite(kind, size=220, color=None, gray=False):
    S = 4; W = size * S; im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = W / 2; r = W * 0.36
    def C(name): return (205, 205, 215) if gray else (color or COL[name])
    ol = (0, 0, 0, 0)
    if kind == "sol":
        for i in range(12):
            a = math.radians(i * 30)
            d.polygon([(c + r * 1.05 * math.cos(a - 0.12), c + r * 1.05 * math.sin(a - 0.12)), (c + r * 1.38 * math.cos(a), c + r * 1.38 * math.sin(a)),
                       (c + r * 1.05 * math.cos(a + 0.12), c + r * 1.05 * math.sin(a + 0.12))], fill=C("orange"))
        d.ellipse([c - r, c - r, c + r, c + r], fill=C("yellow"))
    elif kind == "pez":
        d.polygon([(c + r * 0.55, c), (c + r * 1.25, c - r * 0.6), (c + r * 1.25, c + r * 0.6)], fill=C("orange"))
        d.ellipse([c - r * 1.1, c - r * 0.7, c + r * 0.8, c + r * 0.7], fill=C("orange"))
        d.polygon([(c - r * 0.1, c - r * 0.6), (c + r * 0.35, c - r * 1.05), (c + r * 0.45, c - r * 0.5)], fill=C("orange"))
        d.ellipse([c - r * 0.75, c - r * 0.3, c - r * 0.45, c], fill=(255, 255, 255)); d.ellipse([c - r * 0.66, c - r * 0.22, c - r * 0.5, c - r * 0.06], fill=COL["dark"])
    elif kind == "globo":
        d.line([(c, c + r * 1.0), (c - r * 0.15, c + r * 1.35), (c + r * 0.1, c + r * 1.7)], fill=(120, 120, 130), width=int(W * 0.012))
        d.polygon([(c - r * 0.12, c + r * 1.05), (c + r * 0.12, c + r * 1.05), (c, c + r * 0.88)], fill=C("red"))
        d.ellipse([c - r * 0.82, c - r * 1.15, c + r * 0.82, c + r * 0.98], fill=C("red"))
        d.ellipse([c - r * 0.5, c - r * 0.85, c - r * 0.2, c - r * 0.4], fill=(255, 255, 255, 150))
    elif kind == "manzana":
        d.line([(c, c - r * 0.7), (c + r * 0.1, c - r * 1.1)], fill=COL["brown"], width=int(W * 0.03))
        d.ellipse([c + r * 0.08, c - r * 1.15, c + r * 0.6, c - r * 0.8], fill=(70, 160, 60) if not gray else (180, 180, 190))
        d.ellipse([c - r * 0.95, c - r * 0.75, c + r * 0.15, c + r * 0.95], fill=C("green"))
        d.ellipse([c - r * 0.15, c - r * 0.75, c + r * 0.95, c + r * 0.95], fill=C("green"))
        d.ellipse([c - r * 0.6, c - r * 0.45, c - r * 0.3, c - r * 0.05], fill=(255, 255, 255, 140))
    elif kind == "estrella":
        d.polygon(star_pts(c, c + r * 0.05, r * 1.15, r * 0.5), fill=C("purple"))
        d.ellipse([c - r * 0.3, c - r * 0.1, c - r * 0.12, c + r * 0.1], fill=COL["dark"]); d.ellipse([c + r * 0.12, c - r * 0.1, c + r * 0.3, c + r * 0.1], fill=COL["dark"])
    elif kind == "flor":
        d.rectangle([c - W * 0.012, c + r * 0.3, c + W * 0.012, c + r * 1.4], fill=(70, 160, 60))
        for i in range(6):
            a = math.radians(i * 60); px, py = c + r * 0.55 * math.cos(a), c - r * 0.1 + r * 0.55 * math.sin(a)
            d.ellipse([px - r * 0.42, py - r * 0.42, px + r * 0.42, py + r * 0.42], fill=C("pink"))
        d.ellipse([c - r * 0.35, c - r * 0.45, c + r * 0.35, c + r * 0.25], fill=COL["yellow"] if not gray else (230, 230, 235))
    elif kind == "burbuja":
        col = C("cyan")
        d.ellipse([c - r, c - r, c + r, c + r], fill=col + (90,), outline=col + (255,), width=int(W * 0.025))
        d.arc([c - r * 0.7, c - r * 0.7, c + r * 0.7, c + r * 0.7], 200, 260, fill=(255, 255, 255, 230), width=int(W * 0.03))
    elif kind == "pelota":
        d.ellipse([c - r, c - r, c + r, c + r], fill=C("blue"))
        d.arc([c - r * 1.6, c - r * 0.35, c + r * 0.4, c + r * 2.4], 270, 360, fill=(255, 255, 255), width=int(W * 0.04))
        d.arc([c - r * 0.4, c - r * 2.4, c + r * 1.6, c + r * 0.35], 90, 180, fill=(255, 255, 255), width=int(W * 0.04))
    elif kind == "nube":
        col = (250, 250, 255) if not gray else (205, 205, 215)
        for (x, y, rr) in ((-0.55, 0.15, 0.5), (0, -0.2, 0.62), (0.55, 0.12, 0.5), (0.25, 0.3, 0.42), (-0.25, 0.32, 0.42)):
            d.ellipse([c + r * x - r * rr, c + r * y - r * rr, c + r * x + r * rr, c + r * y + r * rr], fill=col)
    elif kind == "corazon":
        heart(d, c, c, r * 1.05, C("red"))
        d.ellipse([c - r * 0.65, c - r * 0.6, c - r * 0.35, c - r * 0.3], fill=(255, 255, 255, 150))
    elif kind == "cohete":
        d.polygon([(c, c - r * 1.4), (c - r * 0.45, c - r * 0.5), (c + r * 0.45, c - r * 0.5)], fill=COL["red"])
        d.rounded_rectangle([c - r * 0.45, c - r * 0.6, c + r * 0.45, c + r * 0.9], radius=int(r * 0.2), fill=(240, 240, 248))
        d.ellipse([c - r * 0.22, c - r * 0.3, c + r * 0.22, c + r * 0.14], fill=COL["cyan"], outline=COL["blue"], width=int(W * 0.015))
        d.polygon([(c - r * 0.45, c + r * 0.3), (c - r * 0.85, c + r * 1.0), (c - r * 0.45, c + r * 0.9)], fill=COL["red"])
        d.polygon([(c + r * 0.45, c + r * 0.3), (c + r * 0.85, c + r * 1.0), (c + r * 0.45, c + r * 0.9)], fill=COL["red"])
    return im.resize((size, size), Image.LANCZOS)

KIND = {n: OBJS[n][0] for n in OBJS}
KIND_NAMES = {"sol", "pez", "globo", "manzana", "estrella", "flor", "burbuja", "pelota", "nube", "corazon"}
_sp = {}
def sprite(kind, size, color=None, gray=False):
    k = (kind, size, color, gray)
    if k not in _sp: _sp[k] = obj_sprite(kind, size, color, gray)
    return _sp[k]

# ---------- personajes ----------
def blink(t, seed):
    ph = (t + seed) % 3.4
    return ph < 0.13

def eye(d, x, y, rw, rh, lookx, closed):
    if closed:
        d.arc([x - rw, y - rh * 0.3, x + rw, y + rh * 0.9], 200, 340, fill=COL["dark"], width=int(rw * 0.28)); return
    d.ellipse([x - rw, y - rh, x + rw, y + rh], fill=(255, 255, 255), outline=COL["dark"], width=int(rw * 0.12))
    px = x + lookx * rw * 0.35
    d.ellipse([px - rw * 0.55, y - rh * 0.45, px + rw * 0.55, y + rh * 0.55], fill=COL["dark"])
    d.ellipse([px - rw * 0.15, y - rh * 0.35, px + rw * 0.18, y - rh * 0.02], fill=(255, 255, 255))

def draw_tula(t, talk, dance=0.0):
    S = 2; W, H = 760 * S, 560 * S; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bob = math.sin(t * 2.2) * 6 * S + (abs(math.sin(t * 7)) * -40 * S * dance)
    cx, cy = 330 * S, 420 * S + bob
    # patas
    for lx in (-170, -70, 60, 150):
        step = math.sin(t * 9 + lx) * 10 * S * dance
        d.rounded_rectangle([cx + lx * S - 32 * S, cy - 10 * S + step, cx + lx * S + 32 * S, cy + 70 * S], radius=26 * S, fill=(128, 200, 90), outline=(80, 150, 60), width=5 * S)
    # cabeza y cuello
    hb = math.sin(t * 3) * 4 * S + (talk * 8 * S)
    hx, hy = cx + 255 * S, cy - 150 * S + hb
    d.rounded_rectangle([cx + 150 * S, cy - 120 * S, cx + 250 * S, cy - 20 * S], radius=40 * S, fill=(140, 208, 98))
    d.ellipse([hx - 105 * S, hy - 100 * S, hx + 105 * S, hy + 100 * S], fill=(140, 208, 98), outline=(80, 150, 60), width=6 * S)
    # caparazón
    d.pieslice([cx - 240 * S, cy - 260 * S, cx + 240 * S, cy + 80 * S], 180, 360, fill=(62, 160, 78), outline=(40, 115, 55), width=8 * S)
    d.rounded_rectangle([cx - 245 * S, cy - 105 * S, cx + 245 * S, cy - 60 * S], radius=22 * S, fill=(240, 200, 100), outline=(200, 160, 70), width=5 * S)
    for (px, py, rr) in ((-120, -150, 55), (0, -200, 60), (120, -150, 55), (-30, -125, 40), (60, -120, 35)):
        pts = [(cx + px * S + rr * S * math.cos(math.radians(a)), cy + py * S + rr * S * 0.8 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        d.polygon(pts, fill=(105, 195, 100))
    # cara
    closed = blink(t, 0.3)
    eye(d, hx - 30 * S, hy - 25 * S, 30 * S, 36 * S, 0.6, closed)
    eye(d, hx + 42 * S, hy - 25 * S, 30 * S, 36 * S, 0.6, closed)
    d.ellipse([hx - 85 * S, hy + 15 * S, hx - 45 * S, hy + 45 * S], fill=(255, 150, 160, 200))
    d.ellipse([hx + 60 * S, hy + 15 * S, hx + 100 * S, hy + 45 * S], fill=(255, 150, 160, 200))
    if talk > 0.08:
        oh = 10 * S + talk * 38 * S
        d.ellipse([hx - 30 * S, hy + 30 * S, hx + 40 * S, hy + 30 * S + oh], fill=(120, 30, 45))
        d.ellipse([hx - 14 * S, hy + 30 * S + oh * 0.5, hx + 24 * S, hy + 30 * S + oh], fill=(255, 120, 140))
    else:
        d.arc([hx - 30 * S, hy + 5 * S, hx + 40 * S, hy + 55 * S], 20, 160, fill=COL["dark"], width=7 * S)
    return im.resize((W // S, H // S), Image.LANCZOS)

def draw_pipo(t, talk, dance=0.0):
    S = 2; W, H = 520 * S, 520 * S; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = 260 * S, 270 * S + math.sin(t * 2.6) * 10 * S + abs(math.sin(t * 6)) * -30 * S * dance
    flap = math.sin(t * (22 if (talk > 0.08 or dance) else 5)) * (35 if (talk > 0.08 or dance) else 12)
    for side in (-1, 1):
        a = math.radians(flap * side)
        wx, wy = cx + side * 125 * S, cy + 5 * S
        pts = []
        for k in range(24):
            th = 2 * math.pi * k / 24; ex, ey = 70 * S * math.cos(th), 38 * S * math.sin(th)
            rx = ex * math.cos(a) - ey * math.sin(a); ry = ex * math.sin(a) + ey * math.cos(a)
            pts.append((wx + rx, wy + ry))
        d.polygon(pts, fill=(45, 140, 220))
    for k, ang in enumerate((-25, 0, 25)):
        a = math.radians(ang - 90); x2, y2 = cx + 150 * S * math.cos(a), cy + 150 * S * math.sin(a)
        d.ellipse([x2 - 18 * S, y2 - 30 * S, x2 + 18 * S, y2 + 30 * S], fill=(45, 140, 220))
    d.ellipse([cx - 125 * S, cy - 125 * S, cx + 125 * S, cy + 125 * S], fill=(80, 180, 255), outline=(45, 140, 220), width=7 * S)
    d.ellipse([cx - 80 * S, cy - 5 * S, cx + 80 * S, cy + 115 * S], fill=(210, 238, 255))
    for fx in (-35, 35):
        d.line([(cx + fx * S, cy + 120 * S), (cx + fx * S, cy + 160 * S)], fill=COL["orange"], width=9 * S)
        d.line([(cx + fx * S - 18 * S, cy + 165 * S), (cx + fx * S + 18 * S, cy + 165 * S)], fill=COL["orange"], width=9 * S)
    closed = blink(t, 1.7)
    eye(d, cx - 45 * S, cy - 40 * S, 28 * S, 34 * S, -0.6, closed)
    eye(d, cx + 25 * S, cy - 40 * S, 28 * S, 34 * S, -0.6, closed)
    d.ellipse([cx - 95 * S, cy - 5 * S, cx - 60 * S, cy + 22 * S], fill=(255, 150, 170, 200))
    d.ellipse([cx + 40 * S, cy - 5 * S, cx + 75 * S, cy + 22 * S], fill=(255, 150, 170, 200))
    op = talk * 26 * S if talk > 0.08 else 0
    bx, by = cx - 10 * S, cy + 12 * S
    d.polygon([(bx - 70 * S, by - 4 * S - op * 0.3), (bx + 10 * S, by - 24 * S), (bx + 10 * S, by + 2 * S)], fill=COL["orange"])
    d.polygon([(bx - 62 * S, by + 4 * S + op * 0.7), (bx + 10 * S, by + 4 * S), (bx + 6 * S, by + 24 * S + op * 0.4)], fill=(235, 125, 20))
    return im.resize((W // S, H // S), Image.LANCZOS)

# ---------- fondo ----------
class Scenery:
    def __init__(self, W, H):
        self.W, self.H = W, H; S = 2
        im = Image.new("RGB", (W * S, H * S)); d = ImageDraw.Draw(im)
        for y in range(H * S):
            k = y / (H * S); col = tuple(int(COL["sky1"][i] + (COL["sky2"][i] - COL["sky1"][i]) * k) for i in range(3))
            d.line([(0, y), (W * S, y)], fill=col)
        gy = H * S * (0.70 if W > H else 0.78)
        d.ellipse([-W * S * 0.3, gy - H * S * 0.10, W * S * 0.75, gy + H * S * 0.6], fill=COL["hill1"])
        d.ellipse([W * S * 0.35, gy - H * S * 0.07, W * S * 1.35, gy + H * S * 0.6], fill=(140, 214, 106))
        d.rectangle([0, gy + H * S * 0.08, W * S, H * S], fill=COL["hill2"])
        rnd = random.Random(4)
        for _ in range(int(W / 30)):
            x = rnd.uniform(0, W * S); y = rnd.uniform(gy + H * S * 0.1, H * S)
            c = rnd.choice([COL["yellow"], COL["pink"], (255, 255, 255), COL["purple"]])
            for a in range(5):
                ang = math.radians(a * 72); px, py = x + 9 * S * math.cos(ang), y + 9 * S * math.sin(ang)
                d.ellipse([px - 7 * S, py - 7 * S, px + 7 * S, py + 7 * S], fill=c)
            d.ellipse([x - 5 * S, y - 5 * S, x + 5 * S, y + 5 * S], fill=COL["yellow"] if c != COL["yellow"] else COL["orange"])
        self.base = im.resize((W, H), Image.LANCZOS).convert("RGBA")
        self.cloud = sprite("nube", 260)
        self.ground_y = gy / S
    def frame(self, t, night=0.0):
        im = self.base.copy()
        for i, (y, sp, sz) in enumerate(((0.10, 14, 1.0), (0.22, 9, 0.7), (0.06, 6, 0.55))):
            x = ((t * sp + i * 700) % (self.W + 400)) - 300
            c = self.cloud if sz == 1.0 else self.cloud.resize((int(260 * sz), int(260 * sz)))
            im.alpha_composite(c, (int(x), int(self.H * y)))
        if night > 0:
            ov = Image.new("RGBA", im.size, (30, 20, 80, int(150 * night))); im.alpha_composite(ov)
        return im

# ---------- dibujo de escena ----------
class Layout:
    def __init__(self, W, H):
        self.W, self.H = W, H; self.v = H > W
        if not self.v:
            self.stage = (470, 200, 1450, 780); self.tula = (-10, 520); self.pipo = (1440, 280); self.num_c = (960, 130)
        else:
            self.stage = (80, 520, 1000, 1220); self.tula = (-60, 1300); self.pipo = (600, 1180); self.num_c = (540, 400)

def grid_positions(n, box, size):
    x0, y0, x1, y1 = box
    rows = 1 if n <= 4 else 2 if n <= 10 else 3
    cols = math.ceil(n / rows)
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    pos = []
    for i in range(n):
        r, c = divmod(i, cols)
        cnt = cols if r < rows - 1 else n - cols * (rows - 1)
        off = (cols - cnt) * cw / 2
        pos.append((x0 + off + c * cw + cw / 2, y0 + r * ch + ch / 2))
    return pos

def paste_c(im, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01: return
    s = spr
    if abs(scale - 1) > 0.01: s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.5: s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = s.getchannel("A").point(lambda v: int(v * alpha)); s = s.copy(); s.putalpha(a)
    im.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))

def badge(d, x, y, txt, r=30, col=(255, 255, 255), tc=COL["dark"]):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=COL["dark"], width=4)
    d.text((x, y + 1), txt, font=font(r * 1.15), fill=tc, anchor="mm")

def outlined(d, xy, text, f, fill, stroke=COL["dark"], sw=10, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=stroke)

def numeral_disc(im, d, L, n, tt, word=True, cx=None, cy=None, r=110):
    cx = cx or L.num_c[0]; cy = cy or L.num_c[1]
    p = elastic(tt / 0.6)
    if p <= 0: return
    rr = r * p; col = RAINBOW[(n - 1) % 10] if n > 0 else COL["red"]
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col, outline=(255, 255, 255), width=10)
    outlined(d, (cx, cy + 4), str(n), font(rr * 1.25), (255, 255, 255), sw=int(6 * p))
    if word and tt > 0.25:
        a = ease((tt - 0.25) / 0.3)
        outlined(d, (cx, cy + r + 52), WORDS[n].upper(), font(70), (255, 255, 255), sw=9)

def qmark(d, L, t):
    y = L.num_c[1] + math.sin(t * 6) * 12
    outlined(d, (L.num_c[0], y), "?", font(200), COL["yellow"], sw=12)

def banner(d, L, text, tt, y=None, size=110, col=COL["yellow"]):
    p = elastic(tt / 0.6)
    if p <= 0: return
    y = y or (L.num_c[1] + 20)
    outlined(d, (L.W / 2, y), text, font(size * p), col, sw=int(12 * p))

def confetti(d, L, tt):
    rnd = random.Random(9)
    for i in range(120):
        x = rnd.uniform(0, L.W); sp = rnd.uniform(250, 520); y = -40 + tt * sp - rnd.uniform(0, 400)
        if y < -30 or y > L.H: continue
        c = RAINBOW[i % 10]; w = rnd.uniform(10, 20); a = tt * rnd.uniform(3, 8)
        x += math.sin(tt * 3 + i) * 30
        d.polygon([(x + w * math.cos(a), y + w * 0.5 * math.sin(a)), (x - w * math.cos(a), y - w * 0.5 * math.sin(a)),
                   (x - w * math.cos(a) + 6, y - w * 0.5 * math.sin(a) + 10), (x + w * math.cos(a) + 6, y + w * 0.5 * math.sin(a) + 10)], fill=c)

def notes(d, L, tt):
    for i in range(8):
        ph = (tt * 0.5 + i / 8) % 1
        x = L.W * (0.1 + 0.8 * ((i * 0.37) % 1)) + math.sin(tt * 2 + i) * 30; y = L.H * (0.85 - 0.7 * ph)
        c = RAINBOW[i]
        d.ellipse([x - 18, y - 13, x + 18, y + 13], fill=c); d.rectangle([x + 12, y - 70, x + 18, y], fill=c)
        d.polygon([(x + 18, y - 70), (x + 48, y - 55), (x + 18, y - 45)], fill=c)

def draw_frame(L, scen, t):
    b = block_at(t); kind = b["kind"]; bt = t - b["start"]
    night = 0.0
    if kind == "count" and b["args"][0] == 5: night = min(1, bt / 0.8) * 0.85 * min(1, max(0, (b["end"] - t) / 0.6))
    im = scen.frame(t, night); d = ImageDraw.Draw(im)
    who, env = speaking(t)
    danc = 1.0 if (kind == "dance" and b["dancing"] and t >= b["dancing"]) or kind in ("title", "end") else 0.0
    if kind == "review" and b["confetti"] and t >= b["confetti"]: danc = 1.0
    # ----- contenido -----
    if kind == "title" or kind == "end":
        txt1, txt2 = ("¡CONTAMOS", "DEL 1 AL 10!") if kind == "title" else ("¡HASTA LA", "PRÓXIMA!")
        p = elastic(bt / 0.8)
        cy = L.H * (0.24 if not L.v else 0.2)
        fs = (140 if not L.v else 112) * p
        for row, (txt, off) in enumerate(((txt1, 0), (txt2, 4))):
            f = font(max(1, fs)); widths = [f.getlength(ch) for ch in txt]; tot = sum(widths) + 8 * (len(txt) - 1)
            x = L.W / 2 - tot / 2
            for k, ch in enumerate(txt):
                yy = cy + row * (170 if not L.v else 140) + math.sin(t * 5 + k + off) * 10
                outlined(d, (x + widths[k] / 2, yy), ch, f, RAINBOW[(k + off) % 10], sw=12)
                x += widths[k] + 8
        if kind == "title" and bt > 1.0:
            outlined(d, (L.W / 2, cy + (330 if not L.v else 290)), "con Tula y Pipo", font(64), (255, 255, 255), sw=9)
    elif kind == "hello":
        banner(d, L, "¡Hola!", bt, size=150)
    elif kind in ("count", "quiz"):
        n = b["args"][0]; ok = KIND[n] if kind == "count" else b["args"][1]
        size = 300 if n <= 4 else 240 if n <= 8 else 210
        if L.v: size = int(size * 0.85)
        spr = sprite(ok, size, color=(RAINBOW[0] if ok == "corazon" else None))
        pos = grid_positions(n, L.stage, size)
        if kind == "count":
            shown = {i: tt for i, tt in b["pops"]}
        else:
            shown = {i + 1: (b["popall"] or 1e9) + i * 0.09 for i in range(n)} if b["popall"] else {}
        for i, (x, y) in enumerate(pos, 1):
            if i not in shown or t < shown[i]:
                if kind == "count" and bt > 0.6:
                    gs = sprite(ok, size, color=(RAINBOW[i - 1] if ok == "corazon" else None))
                    paste_c(im, gs, x, y + math.sin(t * 2.5 + i) * 3, ease((bt - 0.6) / 0.5) * 0.9, 0, alpha=0.38)
                continue
            tt = t - shown[i]; sc = elastic(tt / 0.45)
            s2 = sprite(ok, size, color=RAINBOW[i - 1]) if ok == "corazon" else spr
            wob = math.sin(t * 2.5 + i) * (6 if ok in ("globo", "burbuja", "nube", "pez") else 2)
            rot = math.sin(t * 2 + i) * (8 if ok in ("globo", "pez") else 3) + (t * 25 if ok == "sol" else 0)
            paste_c(im, s2, x, y + wob, sc, rot)
            if kind == "count":
                badge(d, x + size * 0.32, y - size * 0.38 + wob, str(i), r=int(30 * min(1, sc)) + 1)
        if q_on(b, t): qmark(d, L, t)
        if b["numeral"] and t >= b["numeral"][1]:
            numeral_disc(im, d, L, b["numeral"][0], t - b["numeral"][1])
        elif kind == "count" and b["pops"]:
            last = max(i for i, tt in b["pops"] if tt <= t) if any(tt <= t for i, tt in b["pops"]) else 0
            if last: outlined(d, L.num_c, str(last), font(150), (255, 255, 255), sw=12)
    elif kind == "review":
        for i, tt in b["rpops"]:
            if t < tt: continue
            cols = 5 if not L.v else 3
            r_, c_ = divmod(i - 1, cols)
            if not L.v: x, y = L.W * (0.2 + 0.15 * c_), L.H * (0.28 + 0.30 * r_)
            else: x, y = L.W * (0.2 + 0.3 * c_), L.H * (0.24 + 0.16 * r_)
            numeral_disc(im, d, L, i, t - tt, word=False, cx=x, cy=y + math.sin(t * 4 + i) * 8, r=90 if not L.v else 85)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "dance":
        banner(d, L, "¡A BAILAR!", bt, size=150, col=COL["pink"])
        if b["dancing"] and t >= b["dancing"]: notes(d, L, t - b["dancing"])
    elif kind == "quiz_intro":
        banner(d, L, "¡A JUGAR!", bt, size=150, col=COL["cyan"])
    elif kind == "missing_intro":
        banner(d, L, "¿QUÉ NÚMERO FALTA?", bt, size=110 if not L.v else 80, col=COL["purple"])
    elif kind == "missing":
        seq, miss = b["args"]; n = len(seq)
        for k, v in enumerate(seq):
            if not L.v: x, y = L.W * (0.26 + 0.16 * k), L.H * 0.42
            else: x, y = L.W * (0.25 + 0.5 * (k % 2)), L.H * (0.30 + 0.17 * (k // 2))
            tt = bt - k * 0.25
            if tt < 0: continue
            if k == miss and not (b["fill"] and t >= b["fill"]):
                p = elastic(tt / 0.6); r = 105 * p
                d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 200, 215), outline=(255, 255, 255), width=10)
                outlined(d, (x, y + math.sin(t * 6) * 6), "?", font(r * 1.3), (255, 255, 255), sw=6)
            else:
                tt2 = (t - b["fill"]) if (k == miss) else tt
                numeral_disc(im, d, L, v, tt2, word=False, cx=x, cy=y, r=105)
    elif kind == "sum_intro":
        banner(d, L, "¡A SUMAR!", bt, size=150, col=COL["green"])
    elif kind == "sum":
        a, bb = b["args"]; c = a + bb; size = 210 if not L.v else 170
        spr = sprite("manzana", size)
        x0, y0, x1, y1 = L.stage
        if not L.v:
            boxA = (x0 - 60, y0 + 140, x0 + 360, y1 - 120); boxB = (x0 + 470, y0 + 140, x0 + 850, y1 - 120)
        else:
            boxA = (x0, y0, x1, y0 + 260); boxB = (x0, y0 + 360, x1, y0 + 620)
        for tkey, box, nn in (("sa", boxA, a), ("sb", boxB, bb)):
            if b[tkey] and t >= b[tkey]:
                for k, (x, y) in enumerate(grid_positions(nn, box, size)):
                    paste_c(im, spr, x, y + math.sin(t * 2 + k) * 4, elastic((t - b[tkey] - k * 0.12) / 0.45))
        eq_y = L.num_c[1]
        parts = [str(a)]
        if b["sb"] and t >= b["sb"]: parts += ["+", str(bb)]
        if b["sc"] and t >= b["sc"]: parts += ["=", str(c)]
        txt = " ".join(parts)
        outlined(d, (L.W / 2, eq_y), txt, font(150 if not L.v else 130), COL["yellow"] if not (b["sc"] and t >= b["sc"]) else COL["green"], sw=12)
        if not L.v and b["sb"] and t >= b["sb"]:
            outlined(d, ((boxA[2] + boxB[0]) / 2, (y0 + y1) / 2 + 40), "+", font(140), (255, 255, 255), sw=10)
        if q_on(b, t): outlined(d, (L.W / 2 + (300 if not L.v else 0), eq_y + (0 if not L.v else 150)), "?", font(170), COL["yellow"], sw=12)
    elif kind == "rocket":
        cur = None
        for i, tt in b["cd"]:
            if tt <= t: cur = (i, tt)
        rx, ry = L.W / 2, L.H * (0.48 if not L.v else 0.5)
        if b["launch"] and t >= b["launch"]:
            lt = t - b["launch"]; ry -= (lt ** 2) * 260
            for k in range(14):
                sx = rx + math.sin(k * 1.7 + lt * 9) * 40; sy = ry + 230 + k * 22
                rr = 30 + k * 4
                d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=(255, 255, 255, 200) if k > 3 else COL["orange"])
        else:
            ry += math.sin(t * 30) * (2 if cur else 0)
        paste_c(im, sprite("cohete", 420), rx, ry)
        if cur and not (b["launch"] and t >= b["launch"] + 0.4):
            i, tt = cur
            numeral_disc(im, d, L, i if i > 0 else 0, t - tt, word=False, cx=L.W * (0.25 if not L.v else 0.5), cy=L.H * (0.3 if not L.v else 0.2), r=120)
        if b["launch"] and t >= b["launch"] + 0.4:
            banner(d, L, "¡DESPEGUE!", t - b["launch"] - 0.4, y=L.H * (0.3 if not L.v else 0.2), size=120, col=COL["red"])
    elif kind == "colors":
        n = b["args"][0]; ok = KIND[n]
        rev = b["reveal"] and t >= b["reveal"]
        spr = sprite(ok, 380, gray=not rev)
        paste_c(im, spr, L.W / 2, (L.stage[1] + L.stage[3]) / 2 + 20, elastic(bt / 0.5) * (1 + 0.08 * math.sin(t * 3)))
        if q_on(b, t): qmark(d, L, t)
        if rev:
            k, s, p, cs, cp = OBJS[n]; cw = cp if n != 1 else cs
            if len(b["args"]) > 1: cw = b["args"][1]   # texto opcional: ("scene", "colors", n, "ROJO")
            colc = {1: COL["yellow"], 4: COL["green"], 7: COL["cyan"], 8: COL["blue"]}.get(n, COL["yellow"])
            for pref, cn in (("amarill", "yellow"), ("verde", "green"), ("roj", "red"), ("azul", "blue"), ("celest", "cyan"),
                             ("morad", "purple"), ("rosad", "pink"), ("naranj", "orange")):
                if cw.lower().strip("¡! ").startswith(pref): colc = COL[cn]
            banner(d, L, cw.upper(), t - b["reveal"], size=130, col=colc)
    elif kind == "bye":
        banner(d, L, "¡ADIÓS!", bt, size=160, col=COL["orange"])
    # ----- personajes -----
    tw = env if who == "tula" else 0.0; pw_ = env if who == "pipo" else 0.0
    tsp = draw_tula(t, tw, danc); psp = draw_pipo(t, pw_, danc)
    sc_t = 0.95 if not L.v else 1.0; sc_p = 0.85 if not L.v else 0.9
    im.alpha_composite(tsp.resize((int(tsp.width * sc_t), int(tsp.height * sc_t)), Image.BILINEAR), (int(L.tula[0]), int(L.tula[1])))
    im.alpha_composite(psp.resize((int(psp.width * sc_p), int(psp.height * sc_p)), Image.BILINEAR), (int(L.pipo[0]), int(L.pipo[1])))
    if L.v and SHORT_TITLE:
        f = font(76)
        for k, line in enumerate(SHORT_TITLE.split("|")):
            outlined(d, (L.W / 2, 150 + k * 96), line, f, COL["yellow"] if k == 0 else (255, 255, 255), sw=11)
    return im

SHORT_TITLE = None
def main():
    global SHORT_TITLE
    mode = sys.argv[1]
    frames_only = None
    for a in sys.argv:
        if a.startswith("--frames="): frames_only = [float(x) for x in a.split("=")[1].split(",")]
        if a.startswith("--title="): SHORT_TITLE = a.split("=", 1)[1]
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    if mode == "long":
        W, H = 1920, 1080; t0 = 0.0; t1 = TOTAL; out = "kids_long.mp4"
        nfr = int(math.ceil(TOTAL * FPS)); f0, f1 = 0, nfr
        if len(args) >= 3: f0, f1, out = int(args[0]), min(nfr, int(args[1])), args[2]
        frames = range(f0, f1)
    else:
        W, H = 1080, 1920; t0, t1, out = float(args[0]), float(args[1]), args[2]
        frames = range(int(t0 * FPS), int(t1 * FPS))
    L = Layout(W, H); scen = Scenery(W, H)
    if frames_only:
        for t in frames_only:
            draw_frame(L, scen, t).convert("RGB").save(f"kprev_{mode}_{t:07.2f}.jpg", quality=85)
        return
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k, fr in enumerate(frames):
        t = fr / FPS
        ff.stdin.write(draw_frame(L, scen, t).convert("RGB").tobytes())
        if k % 250 == 0: print(out, k, len(frames), flush=True)
    ff.stdin.close(); ff.wait(); print("done", out)

if __name__ == "__main__":
    main()
