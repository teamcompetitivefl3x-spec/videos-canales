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
import script as _SC
TITLE = getattr(_SC, "TITLE", ("¡CONTAMOS", "DEL 1 AL 10!"))   # título del episodio (2 líneas)
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
                           confetti=None, cd=[], launch=None, sa=None, sb=None, sc=None, reveal=None, popall=None, dancing=None, fill=None,
                           trace=None, sides=[])
                blocks.append(cur)
            elif cur is not None:
                k = a[0]; t = e["start"]
                if k == "pop": cur["pops"].append((a[1], t))
                elif k == "side": cur["sides"].append((a[1], t))
                elif k == "trace": cur["trace"] = t
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

# ---------- formas geométricas (episodio de formas) ----------
SHAPES = ("circulo", "cuadrado", "triangulo", "estrellaf", "corazonf")
SHAPE_NAME = {"circulo": "CÍRCULO", "cuadrado": "CUADRADO", "triangulo": "TRIÁNGULO", "estrellaf": "ESTRELLA", "corazonf": "CORAZÓN"}
SHAPE_COL = {"circulo": "red", "cuadrado": "blue", "triangulo": "green", "estrellaf": "yellow", "corazonf": "pink"}
FACE_DY = {"triangulo": 0.25, "corazonf": -0.05, "estrellaf": 0.08}

def shape_verts(kind, cx, cy, r):
    """Vértices (lados/puntas) de la forma; None si es curva."""
    if kind == "cuadrado":
        h = r * 0.86; return [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    if kind == "triangulo":
        return [(cx, cy - r * 1.05), (cx + r * 1.05, cy + r * 0.78), (cx - r * 1.05, cy + r * 0.78)]
    if kind == "estrellaf":
        return star_pts(cx, cy + r * 0.08, r * 1.12, r * 0.48)
    return None

def shape_pts(kind, cx, cy, r, dense=96):
    """Contorno cerrado de la forma (lista de puntos), empezando arriba y en sentido horario."""
    if kind == "circulo":
        return [(cx + r * math.cos(math.radians(-90 + 360 * i / dense)), cy + r * math.sin(math.radians(-90 + 360 * i / dense))) for i in range(dense)]
    if kind == "corazonf":
        pts = []
        for i in range(dense):
            a = 2 * math.pi * i / dense
            x = 16 * math.sin(a) ** 3; y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
            pts.append((cx + r * x / 15.5, cy - r * y / 15.5 - r * 0.12))
        return pts
    v = shape_verts(kind, cx, cy, r); pts = []
    per = max(2, dense // len(v))
    for i in range(len(v)):
        (x0, y0), (x1, y1) = v[i], v[(i + 1) % len(v)]
        for k in range(per): pts.append((x0 + (x1 - x0) * k / per, y0 + (y1 - y0) * k / per))
    return pts

def partial_path(pts, p):
    """Primer tramo (fracción p del perímetro) del contorno cerrado."""
    loop = pts + [pts[0]]; seg = [math.dist(loop[i], loop[i + 1]) for i in range(len(loop) - 1)]
    tot = sum(seg); goal = tot * clamp(p); out = [loop[0]]; acc = 0
    for i, s in enumerate(seg):
        if acc + s >= goal:
            k = (goal - acc) / s if s else 0
            out.append((loop[i][0] + (loop[i + 1][0] - loop[i][0]) * k, loop[i][1] + (loop[i + 1][1] - loop[i][1]) * k)); break
        out.append(loop[i + 1]); acc += s
    return out

def shape_face(d, kind, c, r, S):
    fy = c + r * FACE_DY.get(kind, 0.0); ew = r * 0.13
    for ex in (-0.3, 0.3):
        d.ellipse([c + r * ex - ew, fy - r * 0.2 - ew * 1.2, c + r * ex + ew, fy - r * 0.2 + ew * 1.2], fill=(255, 255, 255))
        d.ellipse([c + r * ex - ew * 0.6, fy - r * 0.15 - ew * 0.7, c + r * ex + ew * 0.6, fy - r * 0.15 + ew * 0.7], fill=COL["dark"])
        d.ellipse([c + r * ex - ew * 0.25, fy - r * 0.22 - ew * 0.3, c + r * ex + ew * 0.1, fy - r * 0.22], fill=(255, 255, 255))
    d.arc([c - r * 0.25, fy - r * 0.1, c + r * 0.25, fy + r * 0.28], 20, 160, fill=COL["dark"], width=int(r * 0.07))
    for ex in (-0.5, 0.5):
        d.ellipse([c + r * ex - r * 0.11, fy + r * 0.02, c + r * ex + r * 0.11, fy + r * 0.14], fill=(255, 150, 170, 170))

# ---------- animales (caritas simples, de frente) ----------
ANIMALS = ("vaca", "perro", "gato", "pato", "oveja", "cerdo", "gallina", "caballo", "rana")
ANIMAL_COL = {"vaca": "pink", "perro": "red", "gato": "orange", "pato": "yellow", "oveja": "cyan",
              "cerdo": "pink", "gallina": "red", "caballo": "orange", "rana": "green"}

def _eyes(d, c, y, r, dx=0.32, s=0.15):
    ew = r * s
    for ex in (-dx, dx):
        x = c + r * ex
        d.ellipse([x - ew, y - ew * 1.2, x + ew, y + ew * 1.2], fill=(255, 255, 255), outline=COL["dark"], width=max(1, int(ew * 0.18)))
        d.ellipse([x - ew * 0.62, y - ew * 0.55, x + ew * 0.62, y + ew * 0.85], fill=COL["dark"])
        d.ellipse([x - ew * 0.3, y - ew * 0.45, x + ew * 0.08, y - ew * 0.05], fill=(255, 255, 255))

def _cheeks(d, c, y, r, dx=0.55):
    for ex in (-dx, dx):
        d.ellipse([c + r * ex - r * 0.12, y - r * 0.07, c + r * ex + r * 0.12, y + r * 0.07], fill=(255, 150, 170, 190))

def animal_face(d, kind, c, r, W, C):
    lw = max(2, int(W * 0.012))
    if kind == "vaca":
        for sx in (-1, 1):   # cuernos y orejas
            d.polygon([(c + sx * r * 0.42, c - r * 0.72), (c + sx * r * 0.62, c - r * 1.22), (c + sx * r * 0.72, c - r * 0.62)], fill=(250, 230, 170))
            d.ellipse([c + sx * r * 0.7 - r * 0.38, c - r * 0.62, c + sx * r * 0.7 + r * 0.38, c - r * 0.28], fill=(245, 245, 245), outline=COL["dark"], width=lw)
            d.ellipse([c + sx * r * 0.78 - r * 0.2, c - r * 0.54, c + sx * r * 0.78 + r * 0.2, c - r * 0.36], fill=C("pink"))
        d.ellipse([c - r * 0.78, c - r * 0.9, c + r * 0.78, c + r * 0.7], fill=(250, 250, 250), outline=COL["dark"], width=lw)
        d.ellipse([c - r * 0.7, c - r * 0.78, c - r * 0.22, c - r * 0.3], fill=COL["dark"])
        d.ellipse([c + r * 0.28, c - r * 0.1, c + r * 0.66, c + r * 0.3], fill=COL["dark"])
        d.ellipse([c - r * 0.62, c + r * 0.12, c + r * 0.62, c + r * 0.98], fill=C("pink"), outline=COL["dark"], width=lw)
        for sx in (-1, 1):
            d.ellipse([c + sx * r * 0.25 - r * 0.09, c + r * 0.45, c + sx * r * 0.25 + r * 0.09, c + r * 0.62], fill=(170, 80, 100))
        _eyes(d, c, c - r * 0.28, r)
        d.arc([c - r * 0.22, c + r * 0.62, c + r * 0.22, c + r * 0.86], 20, 160, fill=COL["dark"], width=lw)
    elif kind == "perro":
        body = C("brown"); ear = (100, 60, 35) if not C("brown") == (205, 205, 215) else (185, 185, 198)
        d.ellipse([c - r * 0.9, c - r * 0.85, c + r * 0.9, c + r * 0.85], fill=body)
        d.ellipse([c - r * 0.42, c + r * 0.0, c + r * 0.42, c + r * 0.78], fill=(235, 205, 165) if body != (205, 205, 215) else (225, 225, 232))
        for sx in (-1, 1):   # orejas caídas
            d.ellipse([c + sx * r * 0.95 - r * 0.32, c - r * 0.85, c + sx * r * 0.95 + r * 0.32, c + r * 0.45], fill=ear)
        d.ellipse([c - r * 0.6, c - r * 0.62, c - r * 0.05, c - r * 0.05], fill=(235, 205, 165) if body != (205, 205, 215) else (225, 225, 232))
        _eyes(d, c, c - r * 0.3, r)
        d.ellipse([c - r * 0.18, c + r * 0.08, c + r * 0.18, c + r * 0.32], fill=COL["dark"])
        d.ellipse([c - r * 0.08, c + r * 0.11, c + r * 0.02, c + r * 0.18], fill=(255, 255, 255, 180))
        d.line([(c, c + r * 0.32), (c, c + r * 0.45)], fill=COL["dark"], width=lw)
        d.arc([c - r * 0.25, c + r * 0.3, c, c + r * 0.55], 0, 180, fill=COL["dark"], width=lw)
        d.arc([c, c + r * 0.3, c + r * 0.25, c + r * 0.55], 0, 180, fill=COL["dark"], width=lw)
        d.rounded_rectangle([c - r * 0.1, c + r * 0.5, c + r * 0.1, c + r * 0.75], radius=int(r * 0.1), fill=C("red"))
        _cheeks(d, c, c + r * 0.15, r)
    elif kind == "gato":
        body = C("orange")
        for sx in (-1, 1):
            d.polygon([(c + sx * r * 0.85, c - r * 0.25), (c + sx * r * 0.75, c - r * 1.15), (c + sx * r * 0.2, c - r * 0.65)], fill=body)
            d.polygon([(c + sx * r * 0.7, c - r * 0.4), (c + sx * r * 0.68, c - r * 0.92), (c + sx * r * 0.38, c - r * 0.62)], fill=COL["pink"] if body != (205, 205, 215) else (225, 225, 232))
        d.ellipse([c - r * 0.95, c - r * 0.8, c + r * 0.95, c + r * 0.85], fill=body)
        for k in (-0.25, 0.0, 0.25):   # rayitas
            d.line([(c + r * k, c - r * 0.78), (c + r * k * 0.8, c - r * 0.5)], fill=(225, 110, 20) if body != (205, 205, 215) else (185, 185, 198), width=int(W * 0.02))
        d.ellipse([c - r * 0.4, c + r * 0.05, c + r * 0.4, c + r * 0.6], fill=(255, 235, 210) if body != (205, 205, 215) else (225, 225, 232))
        _eyes(d, c, c - r * 0.2, r, dx=0.35, s=0.16)
        d.polygon([(c - r * 0.1, c + r * 0.1), (c + r * 0.1, c + r * 0.1), (c, c + r * 0.22)], fill=COL["pink"] if body != (205, 205, 215) else (185, 185, 198))
        d.arc([c - r * 0.2, c + r * 0.12, c, c + r * 0.36], 0, 180, fill=COL["dark"], width=lw)
        d.arc([c, c + r * 0.12, c + r * 0.2, c + r * 0.36], 0, 180, fill=COL["dark"], width=lw)
        for sx in (-1, 1):   # bigotes
            for dy in (-0.05, 0.08):
                d.line([(c + sx * r * 0.42, c + r * (0.2 + dy)), (c + sx * r * 1.12, c + r * (0.14 + dy * 2.2))], fill=COL["dark"], width=max(1, lw // 2))
        _cheeks(d, c, c + r * 0.05, r, 0.6)
    elif kind == "pato":
        body = C("yellow")
        for k, (x, y) in enumerate(((-0.1, -1.0), (0.08, -1.08), (0.22, -0.98))):   # copete
            d.ellipse([c + r * x - r * 0.12, c + r * y - r * 0.2, c + r * x + r * 0.12, c + r * y + r * 0.2], fill=body)
        d.ellipse([c - r * 0.92, c - r * 0.92, c + r * 0.92, c + r * 0.92], fill=body)
        _eyes(d, c, c - r * 0.3, r, dx=0.34, s=0.17)
        bk = C("orange") if body != (205, 205, 215) else (185, 185, 198)
        d.ellipse([c - r * 0.6, c + r * 0.0, c + r * 0.6, c + r * 0.38], fill=bk)
        d.ellipse([c - r * 0.52, c + r * 0.24, c + r * 0.52, c + r * 0.56], fill=(235, 120, 20) if body != (205, 205, 215) else (175, 175, 188))
        d.line([(c - r * 0.5, c + r * 0.3), (c + r * 0.5, c + r * 0.3)], fill=(200, 95, 15), width=lw)
        for sx in (-1, 1): d.ellipse([c + sx * r * 0.2 - r * 0.04, c + r * 0.1, c + sx * r * 0.2 + r * 0.04, c + r * 0.16], fill=(170, 80, 10))
        _cheeks(d, c, c + r * 0.02, r, 0.68)
    elif kind == "oveja":
        wool = (250, 250, 252) if C("cyan") != (205, 205, 215) else (205, 205, 215)
        for i in range(12):
            a = math.radians(i * 30); x, y = c + r * 0.72 * math.cos(a), c + r * 0.72 * math.sin(a)
            d.ellipse([x - r * 0.36, y - r * 0.36, x + r * 0.36, y + r * 0.36], fill=wool, outline=(215, 215, 225), width=lw)
        d.ellipse([c - r * 0.8, c - r * 0.8, c + r * 0.8, c + r * 0.8], fill=wool)
        face = (95, 85, 95) if wool[0] == 250 else (160, 160, 172)
        for sx in (-1, 1):
            d.ellipse([c + sx * r * 0.62 - r * 0.3, c - r * 0.32, c + sx * r * 0.62 + r * 0.3, c - r * 0.08], fill=face)
        d.ellipse([c - r * 0.48, c - r * 0.5, c + r * 0.48, c + r * 0.78], fill=face)
        for (x, y) in ((-0.25, -0.62), (0.0, -0.72), (0.25, -0.62)):   # flequillo
            d.ellipse([c + r * x - r * 0.2, c + r * y - r * 0.2, c + r * x + r * 0.2, c + r * y + r * 0.2], fill=wool)
        _eyes(d, c, c - r * 0.12, r, dx=0.2, s=0.13)
        d.arc([c - r * 0.16, c + r * 0.3, c + r * 0.16, c + r * 0.52], 20, 160, fill=(255, 255, 255), width=lw)
        _cheeks(d, c, c + r * 0.22, r, 0.3)
    else:
        g = C("red") == (205, 205, 215)
        def G(rgb):   # color fijo de detalle; en gris, gris con la misma luminosidad
            if not g: return rgb
            v = int(150 + 0.36 * (0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2])); return (v, v, min(255, v + 8))
        if kind == "cerdo":
            body = C("pink"); dk = G((235, 110, 150))
            for sx in (-1, 1):   # orejas triangulares
                d.polygon([(c + sx * r * 0.25, c - r * 0.72), (c + sx * r * 0.85, c - r * 1.12), (c + sx * r * 0.82, c - r * 0.35)], fill=body)
                d.polygon([(c + sx * r * 0.42, c - r * 0.7), (c + sx * r * 0.76, c - r * 0.95), (c + sx * r * 0.74, c - r * 0.5)], fill=dk)
            d.ellipse([c - r * 0.95, c - r * 0.85, c + r * 0.95, c + r * 0.9], fill=body)
            _eyes(d, c, c - r * 0.35, r, dx=0.36, s=0.14)
            d.ellipse([c - r * 0.42, c - r * 0.08, c + r * 0.42, c + r * 0.42], fill=G((255, 170, 200)), outline=dk, width=lw)
            for sx in (-1, 1):
                d.ellipse([c + sx * r * 0.16 - r * 0.07, c + r * 0.06, c + sx * r * 0.16 + r * 0.07, c + r * 0.28], fill=G((180, 70, 110)))
            d.arc([c - r * 0.22, c + r * 0.42, c + r * 0.22, c + r * 0.68], 20, 160, fill=COL["dark"], width=lw)
            _cheeks(d, c, c + r * 0.2, r, 0.66)
        elif kind == "gallina":
            body = G((252, 252, 250)) if not g else (215, 215, 222); red = C("red") if not g else (175, 175, 188)
            for (x, y, rr) in ((-0.22, -0.88, 0.2), (0.0, -1.0, 0.24), (0.22, -0.88, 0.2)):   # cresta
                d.ellipse([c + r * x - r * rr, c + r * y - r * rr, c + r * x + r * rr, c + r * y + r * rr], fill=red)
            d.ellipse([c - r * 0.88, c - r * 0.85, c + r * 0.88, c + r * 0.92], fill=body, outline=G((215, 215, 225)), width=lw)
            _eyes(d, c, c - r * 0.3, r, dx=0.33, s=0.15)
            d.polygon([(c - r * 0.2, c - r * 0.02), (c + r * 0.2, c - r * 0.02), (c, c + r * 0.3)], fill=G((255, 185, 40)))
            d.line([(c - r * 0.2, c + r * 0.08), (c + r * 0.2, c + r * 0.08)], fill=G((220, 140, 20)), width=lw)
            d.ellipse([c - r * 0.1, c + r * 0.28, c + r * 0.1, c + r * 0.55], fill=red)   # barbilla
            _cheeks(d, c, c + r * 0.05, r, 0.58)
        elif kind == "caballo":
            body = C("brown"); light = G((225, 180, 135)); mane = G((70, 40, 25))
            for sx in (-1, 1):   # orejas
                d.polygon([(c + sx * r * 0.2, c - r * 0.75), (c + sx * r * 0.55, c - r * 1.25), (c + sx * r * 0.62, c - r * 0.6)], fill=body)
                d.polygon([(c + sx * r * 0.33, c - r * 0.78), (c + sx * r * 0.52, c - r * 1.08), (c + sx * r * 0.55, c - r * 0.7)], fill=light)
            d.ellipse([c - r * 0.68, c - r * 0.95, c + r * 0.68, c + r * 0.55], fill=body)
            d.ellipse([c - r * 0.58, c + r * 0.05, c + r * 0.58, c + r * 1.02], fill=light)
            for (x, y, rr) in ((-0.15, -0.88, 0.2), (0.08, -0.95, 0.22), (0.25, -0.82, 0.17)):   # flequillo
                d.ellipse([c + r * x - rr * r, c + r * y - rr * r, c + r * x + rr * r, c + r * y + rr * r], fill=mane)
            d.polygon([(c - r * 0.1, c - r * 0.6), (c + r * 0.1, c - r * 0.6), (c, c - r * 0.35)], fill=G((255, 255, 255)))   # mancha
            _eyes(d, c, c - r * 0.3, r, dx=0.32, s=0.14)
            for sx in (-1, 1):
                d.ellipse([c + sx * r * 0.24 - r * 0.08, c + r * 0.42, c + sx * r * 0.24 + r * 0.08, c + r * 0.62], fill=G((120, 70, 45)))
            d.arc([c - r * 0.25, c + r * 0.6, c + r * 0.25, c + r * 0.88], 20, 160, fill=COL["dark"], width=lw)
            _cheeks(d, c, c + r * 0.12, r, 0.52)
        elif kind == "rana":
            body = C("green"); belly = G((185, 235, 140))
            for sx in (-1, 1):   # ojos saltones
                d.ellipse([c + sx * r * 0.45 - r * 0.36, c - r * 0.95, c + sx * r * 0.45 + r * 0.36, c - r * 0.25], fill=body)
            d.ellipse([c - r * 1.0, c - r * 0.6, c + r * 1.0, c + r * 0.8], fill=body)
            d.ellipse([c - r * 0.6, c + r * 0.05, c + r * 0.6, c + r * 0.75], fill=belly)
            _eyes(d, c, c - r * 0.6, r, dx=0.45, s=0.2)
            d.arc([c - r * 0.62, c - r * 0.35, c + r * 0.62, c + r * 0.38], 25, 155, fill=COL["dark"], width=int(lw * 1.4))
            for sx in (-1, 1):
                d.ellipse([c + sx * r * 0.12 - r * 0.04, c - r * 0.2, c + sx * r * 0.12 + r * 0.04, c - r * 0.13], fill=COL["dark"])
            _cheeks(d, c, c + r * 0.05, r, 0.7)

def granero(d, c, r, W):
    rd, wh = (215, 50, 50), (255, 255, 255); lw = int(W * 0.022)
    d.polygon([(c - r * 1.2, c - r * 0.25), (c, c - r * 1.2), (c + r * 1.2, c - r * 0.25)], fill=(170, 35, 40))
    d.line([(c - r * 1.25, c - r * 0.2), (c, c - r * 1.25), (c + r * 1.25, c - r * 0.2)], fill=wh, width=lw)
    d.rectangle([c - r * 1.0, c - r * 0.35, c + r * 1.0, c + r * 1.15], fill=rd)
    d.rectangle([c - r * 0.45, c + r * 0.25, c + r * 0.45, c + r * 1.15], fill=wh)
    d.rectangle([c - r * 0.37, c + r * 0.33, c + r * 0.37, c + r * 1.15], fill=rd)
    d.line([(c - r * 0.37, c + r * 0.33), (c + r * 0.37, c + r * 1.15)], fill=wh, width=lw)
    d.line([(c + r * 0.37, c + r * 0.33), (c - r * 0.37, c + r * 1.15)], fill=wh, width=lw)
    d.rectangle([c - r * 0.2, c - r * 0.75, c + r * 0.2, c - r * 0.35], fill=wh)
    d.rectangle([c - r * 0.14, c - r * 0.69, c + r * 0.14, c - r * 0.41], fill=(250, 210, 90))

# ---------- frutas (episodio de frutas) ----------
FRUITS = ("banana", "naranja", "uvas", "fresa", "pera")
LEAF, LEAF2, STEM = (80, 175, 70), (55, 140, 55), (125, 80, 45)

def _leaf(d, K, x, y, w, h, ang):
    pts = []
    for k in range(24):
        th = 2 * math.pi * k / 24; ex, ey = w * math.cos(th), h * math.sin(th) * (1 - 0.35 * math.cos(th))
        a = math.radians(ang); pts.append((x + ex * math.cos(a) - ey * math.sin(a), y + ex * math.sin(a) + ey * math.cos(a)))
    d.polygon(pts, fill=K(LEAF))
    a = math.radians(ang); d.line([(x - w * 0.8 * math.cos(a), y - w * 0.8 * math.sin(a)), (x + w * 0.8 * math.cos(a), y + w * 0.8 * math.sin(a))], fill=K(LEAF2), width=max(2, int(h * 0.12)))

def fruit_draw(d, kind, c, r, W, K):
    lw = max(2, int(W * 0.012))
    if kind == "banana":
        cy0 = c - r * 0.85; R = r * 1.12; outer, inner, mid = [], [], []
        for i in range(61):
            u = i / 60; a = math.radians(30 + 120 * u); th = r * (0.1 + 0.5 * math.sin(math.pi * u) ** 0.8)
            ca, sa = math.cos(a), math.sin(a)
            outer.append((c - r * 0.08 + (R + th / 2) * ca, cy0 + (R + th / 2) * sa)); inner.append((c - r * 0.08 + (R - th / 2) * ca, cy0 + (R - th / 2) * sa))
            mid.append((c - r * 0.08 + (R - th * 0.1) * ca, cy0 + (R - th * 0.1) * sa))
        d.polygon(outer + inner[::-1], fill=K((255, 214, 50)), outline=K((215, 160, 20)))
        d.line(outer + inner[::-1] + [outer[0]], fill=K((215, 160, 20)), width=lw, joint="curve")
        d.line(mid[8:52], fill=K((250, 235, 140)), width=int(r * 0.07), joint="curve")
        x0, y0 = (outer[0][0] + inner[0][0]) / 2, (outer[0][1] + inner[0][1]) / 2   # tallo (derecha)
        d.polygon([(x0 - r * 0.05, y0 - r * 0.02), (x0 + r * 0.22, y0 - r * 0.32), (x0 + r * 0.32, y0 - r * 0.22), (x0 + r * 0.06, y0 + r * 0.08)], fill=K((120, 150, 60)))
        x1, y1 = (outer[-1][0] + inner[-1][0]) / 2, (outer[-1][1] + inner[-1][1]) / 2
        d.ellipse([x1 - r * 0.07, y1 - r * 0.07, x1 + r * 0.07, y1 + r * 0.07], fill=K((90, 60, 30)))
    elif kind == "naranja":
        d.ellipse([c - r * 0.95, c - r * 0.85, c + r * 0.95, c + r * 1.05], fill=K((255, 150, 35)), outline=K((225, 115, 15)), width=lw)
        rn = random.Random(7)
        for _ in range(26):
            a = rn.uniform(0, 2 * math.pi); q = rn.uniform(0.1, 0.8); x, y = c + r * 0.95 * q * math.cos(a), c + r * 0.1 + r * 0.9 * q * math.sin(a)
            d.ellipse([x - r * 0.03, y - r * 0.03, x + r * 0.03, y + r * 0.03], fill=K((240, 125, 20)))
        d.ellipse([c - r * 0.6, c - r * 0.55, c - r * 0.25, c - r * 0.2], fill=K((255, 205, 140)))
        d.line([(c, c - r * 0.82), (c + r * 0.05, c - r * 1.0)], fill=K(STEM), width=int(r * 0.09))
        _leaf(d, K, c + r * 0.32, c - r * 0.98, r * 0.32, r * 0.14, -20)
    elif kind == "uvas":
        d.line([(c, c - r * 0.75), (c + r * 0.12, c - r * 1.15)], fill=K(STEM), width=int(r * 0.09))
        _leaf(d, K, c + r * 0.42, c - r * 1.0, r * 0.36, r * 0.18, -25)
        g = r * 0.25
        for row, (yy, n) in enumerate(((-0.55, 4), (-0.12, 3), (0.3, 3), (0.7, 2), (1.05, 1))):
            for k in range(n):
                x = c + (k - (n - 1) / 2) * g * 1.75 + (0.06 * r if row % 2 else 0); y = c + r * yy
                d.ellipse([x - g, y - g, x + g, y + g], fill=K((150, 75, 200)), outline=K((105, 45, 155)), width=lw)
                d.ellipse([x - g * 0.55, y - g * 0.6, x - g * 0.15, y - g * 0.2], fill=K((215, 175, 240)))
    elif kind == "fresa":
        body = K((235, 45, 70))
        d.ellipse([c - r * 0.92, c - r * 0.62, c + r * 0.92, c + r * 0.42], fill=body)
        d.polygon([(c - r * 0.9, c - r * 0.18), (c + r * 0.9, c - r * 0.18), (c + r * 0.18, c + r * 1.0), (c - r * 0.18, c + r * 1.0)], fill=body)
        d.ellipse([c - r * 0.22, c + r * 0.8, c + r * 0.22, c + r * 1.12], fill=body)
        for (x, y) in ((-0.55, -0.25), (-0.2, -0.3), (0.2, -0.3), (0.55, -0.25), (-0.38, 0.1), (0.0, 0.08), (0.38, 0.1),
                       (-0.2, 0.45), (0.2, 0.45), (0.0, 0.78)):
            d.ellipse([c + r * x - r * 0.04, c + r * y - r * 0.065, c + r * x + r * 0.04, c + r * y + r * 0.065], fill=K((255, 225, 90)))
        d.polygon(star_pts(c, c - r * 0.6, r * 0.62, r * 0.22, n=6, rot=-90), fill=K(LEAF))
        d.line([(c, c - r * 0.65), (c + r * 0.06, c - r * 1.02)], fill=K((70, 150, 60)), width=int(r * 0.09))
        d.ellipse([c - r * 0.6, c - r * 0.45, c - r * 0.3, c - r * 0.2], fill=K((255, 150, 165)))
    elif kind == "pera":
        body = K((175, 212, 70)); ol = K((130, 170, 40))
        d.ellipse([c - r * 0.48, c - r * 0.85, c + r * 0.48, c + r * 0.1], fill=body, outline=ol, width=lw)
        d.ellipse([c - r * 0.82, c - r * 0.25, c + r * 0.82, c + r * 1.12], fill=body, outline=ol, width=lw)
        d.polygon([(c - r * 0.46, c - r * 0.3), (c + r * 0.46, c - r * 0.3), (c + r * 0.74, c + r * 0.2), (c - r * 0.74, c + r * 0.2)], fill=body)
        d.ellipse([c - r * 0.45, c - r * 0.1, c - r * 0.15, c + r * 0.35], fill=K((220, 240, 160)))
        d.line([(c, c - r * 0.82), (c + r * 0.1, c - r * 1.18)], fill=K(STEM), width=int(r * 0.09))
        _leaf(d, K, c + r * 0.38, c - r * 1.05, r * 0.3, r * 0.14, -15)

# ---------- vocales (episodio de las vocales) ----------
VOWELS = ("A", "E", "I", "O", "U")
VCOL = {"A": "red", "E": "blue", "I": "green", "O": "orange", "U": "purple"}
VOWEL_OBJS = ("abeja", "arbol", "elefante", "iglu", "isla", "oso", "uno")

def letter_draw(im, ch, W, K):
    """Letra grande con borde blanco y sombra (kind 'L_A', 'L_a'...)."""
    col = K(COL[VCOL.get(ch.upper(), "red")]); d = ImageDraw.Draw(im)
    f = font(W * (0.86 if ch.isupper() else 0.95)); c = W / 2
    d.text((c + W * 0.025, c + W * 0.035), ch, font=f, fill=(40, 40, 60, 110), anchor="mm", stroke_width=int(W * 0.045), stroke_fill=(40, 40, 60, 110))
    d.text((c, c), ch, font=f, fill=col, anchor="mm", stroke_width=int(W * 0.045), stroke_fill=(255, 255, 255))

def vowel_obj_draw(im, d, kind, c, r, W, K):
    lw = max(2, int(W * 0.012)); dark = COL["dark"]
    if kind == "abeja":
        for sx, a in ((-0.15, -25), (0.3, 20)):   # alas
            d.ellipse([c + r * sx - r * 0.38, c - r * 1.0, c + r * sx + r * 0.38, c - r * 0.25], fill=K((205, 240, 255)) + (220,), outline=K((140, 200, 235)), width=lw)
        body = Image.new("RGBA", im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
        box = [c - r * 0.8, c - r * 0.55, c + r * 0.95, c + r * 0.6]
        bd.ellipse(box, fill=K((255, 205, 40)))
        for x in (0.05, 0.45):
            bd.rectangle([c + r * x, c - r * 0.7, c + r * (x + 0.2), c + r * 0.7], fill=K(dark))
        mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).ellipse(box, fill=255)
        im.paste(body, (0, 0), mask); d = ImageDraw.Draw(im)
        d.ellipse(box, outline=K((60, 50, 40)), width=lw)
        d.polygon([(c + r * 0.92, c - r * 0.08), (c + r * 1.22, c + r * 0.03), (c + r * 0.92, c + r * 0.14)], fill=K(dark))
        hx = c - r * 0.78
        for sx in (-1, 1):   # antenas
            d.line([(hx + sx * r * 0.12, c - r * 0.38), (hx + sx * r * 0.28, c - r * 0.82)], fill=K(dark), width=lw)
            d.ellipse([hx + sx * r * 0.28 - r * 0.07, c - r * 0.89, hx + sx * r * 0.28 + r * 0.07, c - r * 0.75], fill=K(dark))
        d.ellipse([hx - r * 0.45, c - r * 0.45, hx + r * 0.45, c + r * 0.42], fill=K((255, 215, 70)), outline=K((60, 50, 40)), width=lw)
        _eyes(d, hx, c - r * 0.08, r, dx=0.17, s=0.1)
        d.arc([hx - r * 0.15, c + r * 0.02, hx + r * 0.15, c + r * 0.24], 20, 160, fill=K(dark), width=lw)
        _cheeks(d, hx, c + r * 0.12, r, 0.3)
    elif kind == "elefante":
        g = K((165, 175, 200)); gd = K((125, 135, 165))
        for sx in (-1, 1):   # orejas grandes
            d.ellipse([c + sx * r * 0.78 - r * 0.55, c - r * 0.85, c + sx * r * 0.78 + r * 0.55, c + r * 0.35], fill=g, outline=gd, width=lw)
            d.ellipse([c + sx * r * 0.82 - r * 0.36, c - r * 0.65, c + sx * r * 0.82 + r * 0.36, c + r * 0.15], fill=K((250, 175, 190)))
        d.ellipse([c - r * 0.68, c - r * 0.8, c + r * 0.68, c + r * 0.55], fill=g, outline=gd, width=lw)
        tr = [(c + r * 0.0, c + r * 0.15), (c + r * 0.02, c + r * 0.55), (c + r * 0.12, c + r * 0.85), (c + r * 0.32, c + r * 1.0), (c + r * 0.48, c + r * 0.92)]
        d.line(tr, fill=gd, width=int(r * 0.34), joint="curve"); d.line(tr, fill=g, width=int(r * 0.26), joint="curve")
        for (x, y) in tr[1:4]:
            d.arc([x - r * 0.1, y - r * 0.03, x + r * 0.1, y + r * 0.05], 20, 160, fill=gd, width=max(1, lw // 2))
        _eyes(d, c, c - r * 0.25, r, dx=0.3, s=0.14)
        _cheeks(d, c, c + r * 0.08, r, 0.45)
        for sx in (-1, 1):   # colmillos chiquitos
            d.polygon([(c + sx * r * 0.2, c + r * 0.35), (c + sx * r * 0.33, c + r * 0.38), (c + sx * r * 0.3, c + r * 0.55)], fill=K((255, 252, 240)))
    elif kind == "iglu":
        d.ellipse([c - r * 1.3, c + r * 0.6, c + r * 1.3, c + r * 1.05], fill=K((235, 245, 255)))
        cy0 = c + r * 0.8; rx = r * 1.1; ry = r * 1.25
        d.pieslice([c - rx, cy0 - ry, c + rx, cy0 + ry], 180, 360, fill=K((240, 248, 255)), outline=K((150, 195, 230)), width=lw * 2)
        rows = 5
        for k in range(1, rows):
            y = cy0 - ry * k / rows; hw = rx * math.sqrt(max(0, 1 - ((cy0 - y) / ry) ** 2))
            d.line([(c - hw, y), (c + hw, y)], fill=K((170, 205, 235)), width=lw)
        for k in range(rows):
            y0, y1 = cy0 - ry * k / rows, cy0 - ry * (k + 1) / rows; hw = rx * math.sqrt(max(0, 1 - ((cy0 - y0) / ry) ** 2))
            nb = max(2, int(5 - k)); off = 0.5 if k % 2 else 0
            for j in range(nb):
                x = c - hw + (j + off + 0.5) * (2 * hw / (nb + 0.5))
                if abs(x - c) < hw * 0.95: d.line([(x, y0), (x, y1 + 2)], fill=K((170, 205, 235)), width=lw)
        d.pieslice([c - r * 0.38, cy0 - r * 0.75, c + r * 0.38, cy0 + r * 0.75], 180, 360, fill=K((60, 110, 190)))
        d.rectangle([c - r * 0.38, cy0 - r * 0.02, c + r * 0.38, cy0 + r * 0.04], fill=K((60, 110, 190)))
    elif kind == "oso":
        b = K((165, 105, 60)); bl = K((230, 190, 145))
        for sx in (-1, 1):
            d.ellipse([c + sx * r * 0.68 - r * 0.3, c - r * 1.0, c + sx * r * 0.68 + r * 0.3, c - r * 0.4], fill=b)
            d.ellipse([c + sx * r * 0.68 - r * 0.16, c - r * 0.86, c + sx * r * 0.68 + r * 0.16, c - r * 0.54], fill=bl)
        d.ellipse([c - r * 0.92, c - r * 0.85, c + r * 0.92, c + r * 0.85], fill=b)
        d.ellipse([c - r * 0.42, c + r * 0.0, c + r * 0.42, c + r * 0.62], fill=bl)
        _eyes(d, c, c - r * 0.25, r, dx=0.33, s=0.14)
        d.ellipse([c - r * 0.17, c + r * 0.08, c + r * 0.17, c + r * 0.3], fill=K(dark))
        d.ellipse([c - r * 0.08, c + r * 0.11, c + r * 0.0, c + r * 0.17], fill=(255, 255, 255, 170))
        d.line([(c, c + r * 0.3), (c, c + r * 0.42)], fill=K(dark), width=lw)
        d.arc([c - r * 0.2, c + r * 0.3, c, c + r * 0.52], 0, 180, fill=K(dark), width=lw)
        d.arc([c, c + r * 0.3, c + r * 0.2, c + r * 0.52], 0, 180, fill=K(dark), width=lw)
        _cheeks(d, c, c + r * 0.12, r, 0.58)
    elif kind == "arbol":
        d.rounded_rectangle([c - r * 0.18, c + r * 0.1, c + r * 0.18, c + r * 1.2], radius=int(r * 0.06), fill=K((140, 90, 50)))
        d.polygon([(c - r * 0.18, c + r * 1.2), (c - r * 0.42, c + r * 1.25), (c + r * 0.42, c + r * 1.25), (c + r * 0.18, c + r * 1.2)], fill=K((140, 90, 50)))
        for (x, y, rr) in ((-0.5, -0.1, 0.5), (0.5, -0.1, 0.5), (0, -0.55, 0.6), (-0.3, 0.25, 0.42), (0.3, 0.25, 0.42), (0, 0.0, 0.5)):
            d.ellipse([c + r * x - r * rr, c + r * y - r * rr, c + r * x + r * rr, c + r * y + r * rr], fill=K((85, 180, 75)))
        for (x, y, rr) in ((-0.25, -0.65, 0.22), (0.35, -0.35, 0.18)):
            d.ellipse([c + r * x - r * rr, c + r * y - r * rr, c + r * x + r * rr, c + r * y + r * rr], fill=K((130, 210, 110)))
        for (x, y) in ((-0.5, -0.05), (0.15, -0.6), (0.55, 0.05), (-0.1, 0.3), (0.3, -0.15)):
            d.ellipse([c + r * x - r * 0.09, c + r * y - r * 0.09, c + r * x + r * 0.09, c + r * y + r * 0.09], fill=K((235, 60, 60)))
    elif kind == "isla":
        d.ellipse([c - r * 1.35, c + r * 0.5, c + r * 1.35, c + r * 1.25], fill=K((70, 160, 235)))
        for k in range(3):
            x = c - r * 0.9 + k * r * 0.9; d.arc([x - r * 0.18, c + r * 0.95, x + r * 0.18, c + r * 1.15], 200, 340, fill=(255, 255, 255), width=lw)
        d.chord([c - r * 0.95, c + r * 0.35, c + r * 0.95, c + r * 1.05], 180, 360, fill=K((250, 215, 120)))
        tr = [(c - r * 0.05, c + r * 0.62), (c + r * 0.02, c + r * 0.2), (c + r * 0.15, c - r * 0.2), (c + r * 0.3, c - r * 0.5)]
        d.line(tr, fill=K((150, 100, 55)), width=int(r * 0.16), joint="curve")
        tx, ty = tr[-1]
        for ang in (-160, -120, -60, -20, 30, 170):
            a = math.radians(ang); _leaf(d, K, tx + r * 0.36 * math.cos(a), ty + r * 0.22 * math.sin(a) + r * 0.05, r * 0.42, r * 0.13, ang)
        for (x, y) in ((0.2, -0.38), (0.38, -0.36)):
            d.ellipse([c + r * x - r * 0.08, c + r * y - r * 0.08, c + r * x + r * 0.08, c + r * y + r * 0.08], fill=K((120, 80, 40)))
    elif kind == "uno":
        d.ellipse([c - r, c - r, c + r, c + r], fill=K(COL["purple"]), outline=(255, 255, 255), width=int(W * 0.03))
        d.text((c, c + r * 0.05), "1", font=font(r * 1.5), fill=(255, 255, 255), anchor="mm", stroke_width=int(W * 0.015), stroke_fill=K(dark))

# ---------- opuestos: objetos nuevos (luna, taza, helado, auto, caracol, caritas, vasos, puertas) ----------
OPP_SPRITES = ("luna", "taza", "helado", "auto", "caracol", "carafeliz", "caratriste", "vaso_lleno", "vaso_vacio", "puerta_a", "puerta_c")

def opp_sprite_draw(d, kind, c, r, W, C, K):
    lw = max(2, int(W * 0.014)); dk = K(COL["dark"])
    if kind == "luna":
        d.ellipse([c - r * 1.05, c - r * 1.05, c + r * 1.05, c + r * 1.05], fill=K((255, 226, 110)))
        d.ellipse([c - r * 0.25, c - r * 1.35, c + r * 1.45, c + r * 0.55], fill=(0, 0, 0, 0))
        for (x, y, rr) in ((-0.55, 0.45, 0.13), (-0.75, -0.15, 0.09), (-0.2, 0.8, 0.08)):
            d.ellipse([c + r * x - r * rr, c + r * y - r * rr, c + r * x + r * rr, c + r * y + r * rr], fill=K((240, 200, 80)))
        d.arc([c - r * 0.78, c - r * 0.28, c - r * 0.42, c - r * 0.02], 20, 160, fill=dk, width=lw)
        d.arc([c - r * 0.72, c + r * 0.12, c - r * 0.32, c + r * 0.45], 20, 150, fill=dk, width=lw)
        d.ellipse([c - r * 0.98, c - r * 0.02, c - r * 0.72, c + r * 0.16], fill=(255, 150, 170, 170))
    elif kind == "taza":
        d.ellipse([c - r * 1.2, c + r * 0.82, c + r * 1.0, c + r * 1.18], fill=K((250, 250, 255)), outline=K((200, 205, 220)), width=lw)
        d.ellipse([c + r * 0.25, c - r * 0.2, c + r * 1.1, c + r * 0.7], outline=C("red"), width=int(r * 0.17))
        d.rounded_rectangle([c - r * 0.95, c - r * 0.45, c + r * 0.55, c + r * 0.98], radius=int(r * 0.3), fill=C("red"))
        d.ellipse([c - r * 0.95, c - r * 0.62, c + r * 0.55, c - r * 0.25], fill=C("red"))
        d.ellipse([c - r * 0.85, c - r * 0.55, c + r * 0.45, c - r * 0.32], fill=K((120, 70, 40)))
        heart(d, c - r * 0.2, c + r * 0.3, r * 0.32, K((255, 255, 255)))
    elif kind == "helado":
        d.polygon([(c - r * 0.6, c + r * 0.05), (c + r * 0.6, c + r * 0.05), (c, c + r * 1.45)], fill=K((228, 172, 100)))
        def _edge(sd, f): return (c + sd * r * 0.6 * (1 - f), c + r * 0.05 + r * 1.4 * f)
        for f in (0.0, 0.2, 0.4):
            for sd in (-1, 1):
                d.line([_edge(sd, f), _edge(-sd, f + 0.35)], fill=K((196, 135, 70)), width=lw)
        d.ellipse([c - r * 0.55, c - r * 1.2, c + r * 0.55, c - r * 0.2], fill=K((170, 225, 250)))
        d.ellipse([c - r * 0.72, c - r * 0.58, c + r * 0.72, c + r * 0.3], fill=C("pink"))
        for x in (-0.5, -0.1, 0.35):
            d.ellipse([c + r * x - r * 0.12, c + r * 0.1, c + r * x + r * 0.12, c + r * 0.42], fill=C("pink"))
        d.ellipse([c - r * 0.14, c - r * 1.42, c + r * 0.14, c - r * 1.14], fill=K((230, 45, 60)))
        _eyes(d, c, c - r * 0.2, r * 0.9, dx=0.28, s=0.13)
        d.arc([c - r * 0.2, c - r * 0.12, c + r * 0.2, c + r * 0.15], 20, 160, fill=dk, width=lw)
    elif kind == "auto":
        d.rounded_rectangle([c - r * 1.25, c - r * 0.15, c + r * 1.25, c + r * 0.6], radius=int(r * 0.25), fill=C("red"))
        d.polygon([(c - r * 0.75, c - r * 0.12), (c - r * 0.5, c - r * 0.72), (c + r * 0.4, c - r * 0.72), (c + r * 0.75, c - r * 0.12)], fill=C("red"))
        d.polygon([(c - r * 0.6, c - r * 0.16), (c - r * 0.43, c - r * 0.6), (c - r * 0.07, c - r * 0.6), (c - r * 0.07, c - r * 0.16)], fill=K((170, 225, 250)))
        d.polygon([(c + r * 0.03, c - r * 0.16), (c + r * 0.03, c - r * 0.6), (c + r * 0.36, c - r * 0.6), (c + r * 0.6, c - r * 0.16)], fill=K((170, 225, 250)))
        d.ellipse([c + r * 1.0, c - r * 0.02, c + r * 1.22, c + r * 0.2], fill=K((255, 230, 90)))
        d.rectangle([c - r * 1.25, c + r * 0.12, c + r * 1.25, c + r * 0.2], fill=K((255, 255, 255)))
        for x in (-0.68, 0.68):
            d.ellipse([c + r * x - r * 0.33, c + r * 0.28, c + r * x + r * 0.33, c + r * 0.94], fill=dk)
            d.ellipse([c + r * x - r * 0.14, c + r * 0.47, c + r * x + r * 0.14, c + r * 0.75], fill=K((200, 200, 210)))
    elif kind == "caracol":
        body = K((255, 205, 120)); dbody = K((225, 160, 80))
        d.rounded_rectangle([c - r * 1.3, c + r * 0.5, c + r * 1.0, c + r * 0.95], radius=int(r * 0.22), fill=body, outline=dbody, width=lw)
        d.ellipse([c + r * 0.5, c - r * 0.25, c + r * 1.2, c + r * 0.9], fill=body, outline=dbody, width=lw)
        for (x0, x1) in ((0.7, 0.62), (1.02, 1.16)):
            d.line([(c + r * x0, c - r * 0.05), (c + r * x1, c - r * 0.62)], fill=dbody, width=int(lw * 1.6))
            d.ellipse([c + r * x1 - r * 0.12, c - r * 0.76, c + r * x1 + r * 0.12, c - r * 0.52], fill=(255, 255, 255), outline=dk, width=lw)
            d.ellipse([c + r * x1 - r * 0.05, c - r * 0.68, c + r * x1 + r * 0.07, c - r * 0.56], fill=dk)
        d.arc([c + r * 0.72, c + r * 0.2, c + r * 1.05, c + r * 0.5], 20, 160, fill=dk, width=lw)
        d.ellipse([c - r * 1.05, c - r * 0.7, c + r * 0.55, c + r * 0.85], fill=C("purple"), outline=K((120, 70, 190)), width=lw)
        sx, sy = c - r * 0.25, c + r * 0.08
        pts = [(sx + r * 0.68 * (1 - a / (5.2 * math.pi)) * math.cos(a), sy + r * 0.68 * (1 - a / (5.2 * math.pi)) * math.sin(a)) for a in [i * 0.15 for i in range(int(5 * math.pi / 0.15))]]
        d.line(pts, fill=K((215, 185, 250)), width=int(lw * 1.5), joint="curve")
    elif kind in ("carafeliz", "caratriste"):
        happy = kind == "carafeliz"
        d.ellipse([c - r * 1.1, c - r * 1.1, c + r * 1.1, c + r * 1.1], fill=K((255, 214, 70)), outline=K((235, 170, 40)), width=lw)
        _eyes(d, c, c - r * 0.25, r * 1.1, dx=0.32, s=0.15)
        if happy:
            d.chord([c - r * 0.55, c - r * 0.1, c + r * 0.55, c + r * 0.75], 0, 180, fill=K((150, 40, 55)))
            d.ellipse([c - r * 0.25, c + r * 0.45, c + r * 0.25, c + r * 0.72], fill=K((255, 120, 140)))
            _cheeks(d, c, c + r * 0.2, r * 1.1, dx=0.62)
        else:
            d.arc([c - r * 0.42, c + r * 0.38, c + r * 0.42, c + r * 0.95], 200, 340, fill=dk, width=int(lw * 1.6))
            for sx_ in (-1, 1):
                d.line([(c + sx_ * r * 0.18, c - r * 0.62), (c + sx_ * r * 0.55, c - r * 0.5)], fill=dk, width=int(lw * 1.4))
    elif kind in ("vaso_lleno", "vaso_vacio"):
        top, bot = c - r * 1.1, c + r * 1.15; tw, bw = r * 0.8, r * 0.6
        d.polygon([(c - tw, top), (c + tw, top), (c + bw, bot), (c - bw, bot)], fill=(225, 242, 255, 110))
        if kind == "vaso_lleno":
            wl = top + r * 0.3; k_ = (wl - top) / (bot - top); ww = tw - (tw - bw) * k_
            d.polygon([(c - ww, wl), (c + ww, wl), (c + bw, bot), (c - bw, bot)], fill=C("blue"))
            d.ellipse([c - ww, wl - r * 0.1, c + ww, wl + r * 0.1], fill=K((120, 175, 250)))
        d.line([(c - tw, top), (c - bw, bot), (c + bw, bot), (c + tw, top)], fill=K((150, 180, 210)), width=int(lw * 1.6), joint="curve")
        d.ellipse([c - tw, top - r * 0.1, c + tw, top + r * 0.1], outline=K((150, 180, 210)), width=lw)
        d.line([(c - tw * 0.7, top + r * 0.35), (c - bw * 0.72, bot - r * 0.25)], fill=(255, 255, 255, 200), width=int(lw * 1.8))
    elif kind in ("puerta_a", "puerta_c"):
        x0, x1, y0, y1 = c - r * 0.75, c + r * 0.75, c - r * 1.3, c + r * 1.3
        d.rectangle([x0 - r * 0.14, y0 - r * 0.14, x1 + r * 0.14, y1], fill=K((255, 255, 255)))
        if kind == "puerta_c":
            d.rectangle([x0, y0, x1, y1], fill=K((175, 105, 55)))
            for (a, b_) in ((0.12, 0.45), (0.55, 0.9)):
                d.rectangle([x0 + r * 0.18, y0 + (y1 - y0) * a, x1 - r * 0.18, y0 + (y1 - y0) * b_], outline=K((140, 80, 40)), width=lw)
            d.ellipse([x1 - r * 0.38, c - r * 0.05, x1 - r * 0.14, c + r * 0.19], fill=K((255, 211, 51)))
        else:
            d.rectangle([x0, y0, x1, y1], fill=K((70, 50, 95)))
            d.rectangle([x0, y1 - r * 0.25, x1, y1], fill=K((235, 190, 110)))
            d.polygon([(x0, y0), (x0 + r * 0.55, y0 - r * 0.18), (x0 + r * 0.55, y1 + r * 0.15), (x0, y1)], fill=K((175, 105, 55)))
            d.ellipse([x0 + r * 0.34, c, x0 + r * 0.5, c + r * 0.2], fill=K((255, 211, 51)))

# paneles de opuestos: clave -> (fondo A, fondo B, función que dibuja el lado)
OPP_BG = {"tam": ((200, 235, 255), (200, 235, 255)), "pos": ((190, 228, 255), (190, 228, 255)),
          "dia": ((130, 205, 250), (40, 45, 110)), "vaso": ((255, 244, 205), (255, 244, 205)),
          "puerta": ((255, 220, 230), (255, 220, 230)), "temp": ((255, 215, 190), (210, 236, 255)),
          "vel": ((215, 245, 205), (215, 245, 205)), "cara": ((255, 240, 185), (205, 222, 252))}
_pbg = {}
def opp_panel(key, side, t, P):
    """Cuadro P x P (RGBA) con el lado A o B del opuesto, animado."""
    ck = (key, side, P)
    if ck not in _pbg:
        S = 3; Q = P * S; im = Image.new("RGBA", (Q, Q), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        bg = OPP_BG[key][0 if side == "A" else 1]
        d.rectangle([0, 0, Q, Q], fill=bg)
        if key in ("pos", "dia", "vel"):
            gcol = (110, 190, 80) if not (key == "dia" and side == "B") else (40, 95, 60)
            d.ellipse([-Q * 0.3, Q * 0.74, Q * 1.3, Q * 1.6], fill=gcol)
        if key == "vel": d.rectangle([0, Q * 0.8, Q, Q * 0.92], fill=(150, 150, 165)); [d.rectangle([x, Q * 0.855, x + Q * 0.08, Q * 0.865], fill=(255, 255, 255)) for x in np.arange(0, Q, Q * 0.16)]
        if key == "puerta":
            for yy in np.arange(Q * 0.12, Q, Q * 0.12): d.line([(0, yy), (Q, yy)], fill=(250, 200, 215), width=S * 2)
        mask = Image.new("L", (Q, Q), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, Q - 1, Q - 1], radius=int(Q * 0.09), fill=255)
        _pbg[ck] = (im.resize((P, P), Image.LANCZOS), mask.resize((P, P), Image.LANCZOS))
    base, mask = _pbg[ck]; im = base.copy(); d = ImageDraw.Draw(im); h = P / 2
    if key == "tam":
        if side == "A": paste_c(im, sprite("pelota", int(P * 0.92)), h, h + 8 + math.sin(t * 2.5) * 5, 1.0, math.sin(t * 2) * 4)
        else: paste_c(im, sprite("pelota", int(P * 0.3)), h, P * 0.68 + math.sin(t * 2.5) * 3, 1.0, math.sin(t * 2) * 4)
    elif key == "pos":
        if side == "A":
            y = P * 0.24 + math.sin(t * 3) * 10; paste_c(im, sprite("pelota", int(P * 0.32)), h, y, 1.0, t * 40)
            for k in range(3): d.line([(h - 40 + k * 40, y + 75), (h - 40 + k * 40, y + 120)], fill=(255, 255, 255), width=6)
        else:
            sq = 1 + 0.04 * abs(math.sin(t * 3)); paste_c(im, sprite("pelota", int(P * 0.32)), h, P * 0.74, sq)
    elif key == "dia":
        if side == "A":
            paste_c(im, sprite("sol", int(P * 0.5)), P * 0.66, P * 0.32, 1.0, t * 20)
            paste_c(im, sprite("nube", int(P * 0.42)), P * 0.28 + math.sin(t * 0.8) * 12, P * 0.5)
        else:
            rn = random.Random(11)
            for k in range(14):
                x, y = rn.uniform(0.06, 0.94) * P, rn.uniform(0.06, 0.62) * P; s = (7 + 5 * rn.random()) * (0.7 + 0.3 * math.sin(t * 4 + k))
                d.polygon(star_pts(x, y, s * 1.6, s * 0.6), fill=(255, 240, 150))
            paste_c(im, sprite("luna", int(P * 0.5)), P * 0.6, P * 0.36, 1.0, math.sin(t * 1.5) * 5)
    elif key == "vaso":
        paste_c(im, sprite("vaso_lleno" if side == "A" else "vaso_vacio", int(P * 0.82)), h, h + 15)
        if side == "A":
            for k in range(5):
                ph = (t * 0.45 + k / 5) % 1; x = h + (k - 2) * 26 + math.sin(t * 3 + k) * 6; y = P * 0.78 - ph * P * 0.42; rr = 6 + k % 3 * 2
                d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 255, 255, 220), width=3)
    elif key == "puerta":
        paste_c(im, sprite("puerta_a" if side == "A" else "puerta_c", int(P * 0.9)), h, h + 22)
    elif key == "temp":
        if side == "A":
            paste_c(im, sprite("taza", int(P * 0.72)), h, P * 0.64)
            for k in range(3):
                x0 = h - 50 + k * 40
                for j in range(3):
                    ph = (t * 0.6 + j / 3 + k * 0.17) % 1; yb = P * 0.36 - ph * P * 0.3; a = int(230 * math.sin(ph * math.pi))
                    pts = [(x0 + math.sin((yy / 14) + t * 3 + k) * 9, yb - yy) for yy in range(0, 50, 5)]
                    d.line(pts, fill=(255, 255, 255, a), width=7, joint="curve")
        else:
            paste_c(im, sprite("helado", int(P * 0.78)), h, h + 12, 1.0, math.sin(t * 2) * 3)
            rn = random.Random(5)
            for k in range(12):
                x = rn.uniform(0.05, 0.95) * P + math.sin(t * 1.5 + k) * 10; y = ((rn.random() + t * 0.12) % 1) * P; s = 7 + 4 * rn.random()
                for a in range(3):
                    ang = math.radians(a * 60 + t * 40)
                    d.line([(x - s * math.cos(ang), y - s * math.sin(ang)), (x + s * math.cos(ang), y + s * math.sin(ang))], fill=(255, 255, 255, 230), width=3)
    elif key == "vel":
        if side == "A":
            ph = (t * 0.7) % 1; x = -P * 0.35 + ph * P * 1.7; y = P * 0.68 + math.sin(t * 25) * 2
            for k in range(4): d.line([(x - 120 - k * 18, y - 40 + k * 22), (x - 70 - k * 18, y - 40 + k * 22)], fill=(255, 255, 255), width=6)
            paste_c(im, sprite("auto", int(P * 0.5)), x, y)
        else:
            x = P * 0.42 + math.sin(t * 0.25) * P * 0.12
            paste_c(im, sprite("caracol", int(P * 0.55)), x, P * 0.66 + math.sin(t * 1.2) * 2)
    elif key == "cara":
        paste_c(im, sprite("carafeliz" if side == "A" else "caratriste", int(P * 0.85)), h, h + 5 + (math.sin(t * 4) * 6 if side == "A" else 0),
                1.0 + (0.03 * math.sin(t * 5) if side == "A" else 0))
        if side == "B":
            for k, sx_ in enumerate((-1, 1)):
                ph = (t * 0.5 + k * 0.5) % 1; x = h + sx_ * P * 0.15; y = P * 0.44 + ph * P * 0.28; rr = 11
                d.polygon([(x, y - rr * 1.8), (x + rr, y), (x - rr, y)], fill=(110, 180, 250, int(255 * (1 - ph))))
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(110, 180, 250, int(255 * (1 - ph))))
    a = np.minimum(np.asarray(im.getchannel("A")), np.asarray(mask)); im.putalpha(Image.fromarray(a))
    return im

def opp_card(im, d, panel, cx, cy, P, scale=1.0, alpha=1.0, glow=False):
    if scale <= 0.02: return
    s = P * scale / 2
    d.rounded_rectangle([cx - s + 8, cy - s + 12, cx + s + 8, cy + s + 12], radius=int(P * 0.1 * scale), fill=(40, 40, 60, int(70 * alpha)))
    if glow:
        g = s + 14 + 5 * math.sin(cx + cy)
        d.rounded_rectangle([cx - g, cy - g, cx + g, cy + g], radius=int(P * 0.12 * scale), outline=COL["yellow"], width=12)
    d.rounded_rectangle([cx - s - 9, cy - s - 9, cx + s + 9, cy + s + 9], radius=int(P * 0.1 * scale), fill=(255, 255, 255))
    paste_c(im, panel, cx, cy, scale, 0, alpha=alpha)

def opp_q_card(d, cx, cy, P, scale, t):
    if scale <= 0.02: return
    s = P * scale / 2
    d.rounded_rectangle([cx - s + 8, cy - s + 12, cx + s + 8, cy + s + 12], radius=int(P * 0.1 * scale), fill=(40, 40, 60, 70))
    d.rounded_rectangle([cx - s - 9, cy - s - 9, cx + s + 9, cy + s + 9], radius=int(P * 0.1 * scale), fill=(210, 210, 226), outline=(255, 255, 255), width=10)
    outlined(d, (cx, cy + math.sin(t * 6) * 8), "?", font(P * 0.6 * scale), (255, 255, 255), sw=max(1, int(10 * scale)))

def sparkle(d, x, y, rt, base, dur=1.2):
    if rt >= dur: return
    for j in range(10):
        a = j * 36 + rt * 90; r2 = base + rt * 230
        d.polygon(star_pts(x + r2 * math.cos(math.radians(a)), y + r2 * math.sin(math.radians(a)), 22 * (dur - rt), 9 * (dur - rt)), fill=RAINBOW[j])

def two_arrow(d, cx, cy, w, col):
    h = w * 0.28
    d.polygon([(cx - w / 2, cy), (cx - w / 2 + h * 1.2, cy - h * 1.3), (cx - w / 2 + h * 1.2, cy - h * 0.5), (cx + w / 2 - h * 1.2, cy - h * 0.5),
               (cx + w / 2 - h * 1.2, cy - h * 1.3), (cx + w / 2, cy), (cx + w / 2 - h * 1.2, cy + h * 1.3), (cx + w / 2 - h * 1.2, cy + h * 0.5),
               (cx - w / 2 + h * 1.2, cy + h * 0.5), (cx - w / 2 + h * 1.2, cy + h * 1.3)], fill=col, outline=COL["dark"], width=5)

def silhouette(spr, col=(120, 110, 170)):
    s = Image.new("RGBA", spr.size, col + (255,)); s.putalpha(spr.getchannel("A")); return s

def mancha(d, c, r, W, base):
    """Mancha de pintura redondeada con gotitas y carita sonriente."""
    dark = tuple(int(v * 0.78) for v in base); light = tuple(int(v + (255 - v) * 0.5) for v in base)
    rn = random.Random(7)
    blobs = [(0, 0, 0.82)] + [(0.78 * math.cos(math.radians(a)), 0.78 * math.sin(math.radians(a)), 0.30 + 0.06 * (k % 2))
                              for k, a in enumerate(range(0, 360, 40))]
    drops = [(1.18, -0.55, 0.11), (-1.2, 0.35, 0.09), (0.55, 1.18, 0.1), (-0.75, -1.05, 0.08)]
    for col, grow in ((dark, 0.045), (base, 0.0)):
        for (x, y, rr) in blobs + drops:
            R = r * (rr + grow); d.ellipse([c + r * x - R, c + r * y - R, c + r * x + R, c + r * y + R], fill=col)
    d.ellipse([c - r * 0.55, c - r * 0.62, c - r * 0.2, c - r * 0.35], fill=light + (220,))
    _eyes(d, c, c - r * 0.05, r * 0.9)
    d.arc([c - r * 0.3, c + r * 0.05, c + r * 0.3, c + r * 0.45], 20, 160, fill=COL["dark"], width=int(W * 0.02))
    _cheeks(d, c, c + r * 0.2, r * 0.9)

# ---------- días de la semana ----------
DAYS = [("LUNES", "red"), ("MARTES", "orange"), ("MIÉRCOLES", "yellow"), ("JUEVES", "green"),
        ("VIERNES", "blue"), ("SÁBADO", "purple"), ("DOMINGO", "pink")]
WEEK_SPRITES = ("paleta", "regadera", "tambor", "cometa", "pastel")

def fit_font(text, maxw, size):
    while size > 10 and font(size).getlength(text) > maxw: size -= 2
    return font(size)

def week_sprite_draw(d, kind, c, r, W, C, K):
    lw = max(2, int(W * 0.014)); dk = K(COL["dark"])
    if kind == "paleta":   # paleta de pintor con pincel
        base = K((242, 210, 160)); edge = K((205, 160, 100))
        d.ellipse([c - r * 1.25, c - r * 0.9, c + r * 1.15, c + r * 0.95], fill=base, outline=edge, width=lw * 2)
        d.ellipse([c + r * 0.35, c + r * 0.2, c + r * 0.8, c + r * 0.62], fill=(0, 0, 0, 0))
        d.arc([c + r * 0.35, c + r * 0.2, c + r * 0.8, c + r * 0.62], 0, 360, fill=edge, width=lw * 2)
        for (x, y, cn) in ((-0.75, -0.15, "red"), (-0.4, -0.55, "yellow"), (0.1, -0.6, "blue"), (0.6, -0.3, "green"), (-0.55, 0.38, "purple"), (-0.05, 0.5, "pink")):
            col = C("red") if cn == "red" else K(COL[cn])
            d.ellipse([c + r * (x - 0.22), c + r * (y - 0.19), c + r * (x + 0.22), c + r * (y + 0.19)], fill=col)
        # pincel en diagonal
        d.line([(c - r * 0.1, c + r * 0.15), (c + r * 1.15, c - r * 1.15)], fill=K((150, 95, 50)), width=int(W * 0.035))
        d.polygon([(c - r * 0.18, c + r * 0.05), (c + r * 0.0, c + r * 0.25), (c - r * 0.45, c + r * 0.55)], fill=C("red"))
        d.line([(c - r * 0.05, c + r * 0.1), (c + r * 0.12, c - r * 0.07)], fill=K((200, 200, 210)), width=int(W * 0.045))
    elif kind == "regadera":   # regadera
        col = C("yellow"); dcol = tuple(max(0, v - 45) for v in col[:3])
        d.line([(c + r * 0.55, c + r * 0.35), (c + r * 1.3, c - r * 0.55)], fill=dcol, width=int(W * 0.05))
        d.polygon([(c + r * 1.15, c - r * 0.75), (c + r * 1.45, c - r * 0.45), (c + r * 1.35, c - r * 0.8)], fill=dcol)
        d.arc([c - r * 0.75, c - r * 1.15, c + r * 0.45, c - r * 0.05], 180, 360, fill=dcol, width=int(W * 0.04))
        d.rounded_rectangle([c - r * 0.95, c - r * 0.5, c + r * 0.65, c + r * 1.0], radius=int(r * 0.25), fill=col)
        d.rectangle([c - r * 0.95, c + r * 0.05, c + r * 0.65, c + r * 0.2], fill=K((255, 255, 255)))
        for (x, y) in ((1.5, -0.3), (1.65, 0.05), (1.4, 0.15)):
            gx, gy = c + r * x * 0.85, c + r * y
            d.ellipse([gx - r * 0.08, gy - r * 0.1, gx + r * 0.08, gy + r * 0.1], fill=K((90, 170, 240)))
        _eyes(d, c - r * 0.15, c + r * 0.5, r * 0.8, dx=0.3, s=0.12)
    elif kind == "tambor":   # tambor con palillos
        col = C("blue"); top = K((250, 244, 226))
        d.rectangle([c - r * 0.95, c - r * 0.35, c + r * 0.95, c + r * 0.8], fill=col)
        d.ellipse([c - r * 0.95, c + r * 0.5, c + r * 0.95, c + r * 1.1], fill=col)
        d.rectangle([c - r * 0.95, c + r * 0.62, c + r * 0.95, c + r * 0.78], fill=K((255, 211, 51)))
        d.rectangle([c - r * 0.95, c - r * 0.35, c + r * 0.95, c - r * 0.2], fill=K((255, 211, 51)))
        for k in range(5):   # cordones en zigzag
            x0 = c - r * 0.95 + k * r * 0.38
            d.line([(x0, c - r * 0.2), (x0 + r * 0.19, c + r * 0.62), (x0 + r * 0.38, c - r * 0.2)], fill=K((255, 255, 255)), width=lw * 2)
        d.ellipse([c - r * 0.95, c - r * 0.65, c + r * 0.95, c - r * 0.05], fill=top, outline=K((220, 200, 160)), width=lw * 2)
        for sx in (-1, 1):
            d.line([(c + sx * r * 0.2, c - r * 0.45), (c + sx * r * 1.05, c - r * 1.3)], fill=K((150, 95, 50)), width=int(W * 0.03))
            d.ellipse([c + sx * r * 1.05 - r * 0.14, c - r * 1.44, c + sx * r * 1.05 + r * 0.14, c - r * 1.16], fill=K((240, 70, 70)))
    elif kind == "cometa":   # cometa (barrilete) con cola de moños
        col = C("purple"); lt = tuple(int(v + (255 - v) * 0.45) for v in col[:3])
        top, rt, bot, lf = (c - r * 0.2, c - r * 1.3), (c + r * 0.65, c - r * 0.35), (c - r * 0.2, c + r * 0.85), (c - r * 1.05, c - r * 0.35)
        cen = (c - r * 0.2, c - r * 0.35)
        d.polygon([top, rt, cen], fill=col); d.polygon([rt, bot, cen], fill=lt); d.polygon([bot, lf, cen], fill=col); d.polygon([lf, top, cen], fill=lt)
        d.line([top, bot], fill=K((255, 255, 255)), width=lw); d.line([lf, rt], fill=K((255, 255, 255)), width=lw)
        tail = [(bot[0] + math.sin(k * 1.1) * r * 0.25 + k * r * 0.18, bot[1] + k * r * 0.18) for k in range(7)]
        d.line(tail, fill=K((90, 90, 110)), width=lw, joint="curve")
        for k, cn in ((2, "red"), (4, "yellow"), (6, "cyan")):
            x, y = tail[k]
            d.polygon([(x, y), (x - r * 0.2, y - r * 0.12), (x - r * 0.2, y + r * 0.12)], fill=K(COL[cn]))
            d.polygon([(x, y), (x + r * 0.2, y - r * 0.12), (x + r * 0.2, y + r * 0.12)], fill=K(COL[cn]))
        _eyes(d, cen[0], cen[1] + r * 0.05, r * 0.75, dx=0.3, s=0.12)
        d.arc([cen[0] - r * 0.18, cen[1] + r * 0.1, cen[0] + r * 0.18, cen[1] + r * 0.35], 20, 160, fill=dk, width=lw)
    elif kind == "pastel":   # pastel de dos pisos con vela
        col = C("pink"); lt = tuple(int(v + (255 - v) * 0.5) for v in col[:3]); wh = K((255, 255, 255))
        d.ellipse([c - r * 1.3, c + r * 0.95, c + r * 1.3, c + r * 1.25], fill=K((225, 225, 235)))
        d.rounded_rectangle([c - r * 1.1, c + r * 0.05, c + r * 1.1, c + r * 1.1], radius=int(r * 0.12), fill=col)
        d.rounded_rectangle([c - r * 0.75, c - r * 0.65, c + r * 0.75, c + r * 0.12], radius=int(r * 0.12), fill=lt)
        for (y0, x0, x1) in ((0.05, -1.1, 1.1), (-0.65, -0.75, 0.75)):
            d.rectangle([c + r * x0, c + r * y0, c + r * x1, c + r * (y0 + 0.14)], fill=wh)
            n = 6 if x1 > 1 else 4
            for k in range(n):
                x = c + r * x0 + (k + 0.5) * r * (x1 - x0) / n
                d.ellipse([x - r * 0.12, c + r * (y0 + 0.02), x + r * 0.12, c + r * (y0 + 0.32)], fill=wh)
        for k, cn in enumerate(("yellow", "cyan", "green", "orange", "purple")):
            x = c - r * 0.8 + k * r * 0.4
            d.ellipse([x - r * 0.07, c + r * 0.62, x + r * 0.07, c + r * 0.76], fill=K(COL[cn]))
        d.rounded_rectangle([c - r * 0.08, c - r * 1.15, c + r * 0.08, c - r * 0.6], radius=int(r * 0.04), fill=K((110, 205, 250)))
        d.polygon([(c, c - r * 1.5), (c + r * 0.13, c - r * 1.25), (c, c - r * 1.13), (c - r * 0.13, c - r * 1.25)], fill=K((255, 170, 40)))
        d.ellipse([c - r * 0.05, c - r * 1.3, c + r * 0.05, c - r * 1.18], fill=K((255, 240, 150)))

def calendar_draw(d, n, c, r, W):
    """Hoja de calendario: n = 1..7 (día) o 0 (escondido: '?')."""
    name, cn = DAYS[n - 1] if n else ("", None)
    col = COL[cn] if cn else (190, 190, 205)
    x0, y0, x1, y1 = c - r * 1.05, c - r * 1.1, c + r * 1.05, c + r * 1.25
    d.rounded_rectangle([x0 + W * 0.015, y0 + W * 0.02, x1 + W * 0.015, y1 + W * 0.02], radius=int(r * 0.18), fill=(40, 40, 60, 90))
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(r * 0.18), fill=(255, 255, 255), outline=COL["dark"], width=int(W * 0.012))
    d.rounded_rectangle([x0, y0, x1, y0 + r * 0.55], radius=int(r * 0.18), fill=col, outline=COL["dark"], width=int(W * 0.012))
    d.rectangle([x0 + W * 0.006, y0 + r * 0.3, x1 - W * 0.006, y0 + r * 0.55 - W * 0.006], fill=col)
    for sx in (-0.55, 0.55):
        d.rounded_rectangle([c + r * sx - r * 0.09, y0 - r * 0.22, c + r * sx + r * 0.09, y0 + r * 0.2], radius=int(r * 0.08), fill=(120, 120, 140), outline=COL["dark"], width=int(W * 0.008))
    if n:
        d.text((c, c + r * 0.25), str(n), font=font(r * 1.15), fill=col, anchor="mm", stroke_width=int(W * 0.012), stroke_fill=COL["dark"])
        f = fit_font(name, r * 1.85, int(r * 0.36))
        d.text((c, c + r * 1.0), name, font=f, fill=COL["dark"], anchor="mm")
    else:
        d.text((c, c + r * 0.45), "?", font=font(r * 1.3), fill=(190, 190, 205), anchor="mm", stroke_width=int(W * 0.01), stroke_fill=COL["dark"])

def obj_sprite(kind, size=220, color=None, gray=False, face=False):
    S = 4; W = size * S; im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = W / 2; r = W * 0.36
    if kind == "manzanar": kind = "manzana"; color = color or (230, 45, 55)
    def C(name): return (205, 205, 215) if gray else (color or COL[name])
    def K(rgb):   # color fijo; en gris, conserva la luminosidad para que se vean los detalles
        if not gray: return rgb
        a = rgb[3:] ; v = int(150 + 0.36 * (0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2])); return (v, v, min(255, v + 8)) + tuple(a)
    ol = (0, 0, 0, 0)
    if kind in SHAPES:
        rr = r * 1.08; pts = shape_pts(kind, c, c, rr, 160)
        d.polygon(pts, fill=C(SHAPE_COL[kind]))
        d.line(pts + [pts[0], pts[1]], fill=(255, 255, 255), width=int(W * 0.035), joint="curve")
        if kind == "circulo": d.arc([c - rr * 0.72, c - rr * 0.72, c + rr * 0.72, c + rr * 0.72], 200, 250, fill=(255, 255, 255, 150), width=int(W * 0.03))
        if face: shape_face(d, kind, c, rr, S)
    elif kind == "regalo":
        d.rectangle([c - r * 0.95, c - r * 0.55, c + r * 0.95, c + r * 1.2], fill=C("red"))
        d.rectangle([c - r * 1.05, c - r * 0.8, c + r * 1.05, c - r * 0.45], fill=(220, 50, 60))
        d.rectangle([c - r * 0.15, c - r * 0.8, c + r * 0.15, c + r * 1.2], fill=COL["yellow"])
        for sx in (-1, 1):
            d.ellipse([c + sx * r * 0.05 - r * 0.45 + (sx > 0) * r * 0.4, c - r * 1.25, c + sx * r * 0.05 + (sx > 0) * r * 0.4 - r * 0.05, c - r * 0.8], outline=COL["yellow"], width=int(W * 0.03))
    elif kind == "ventana":
        d.rectangle([c - r * 1.05, c - r * 1.05, c + r * 1.05, c + r * 1.05], fill=(255, 255, 255))
        d.rectangle([c - r * 0.88, c - r * 0.88, c + r * 0.88, c + r * 0.88], fill=C("cyan"))
        d.rectangle([c - r * 0.06, c - r * 0.9, c + r * 0.06, c + r * 0.9], fill=(255, 255, 255))
        d.rectangle([c - r * 0.9, c - r * 0.06, c + r * 0.9, c + r * 0.06], fill=(255, 255, 255))
        d.line([(c - r * 0.7, c - r * 0.2), (c - r * 0.25, c - r * 0.65)], fill=(255, 255, 255, 170), width=int(W * 0.025))
    elif kind == "bloque":
        d.rounded_rectangle([c - r, c - r, c + r, c + r], radius=int(r * 0.12), fill=C("orange"))
        d.rounded_rectangle([c - r * 0.7, c - r * 0.7, c + r * 0.7, c + r * 0.7], radius=int(r * 0.1), fill=(255, 190, 100))
        heart(d, c, c + r * 0.05, r * 0.38, COL["red"])
    elif kind == "gorro":
        d.polygon([(c, c - r * 1.15), (c + r * 0.85, c + r * 1.0), (c - r * 0.85, c + r * 1.0)], fill=C("purple"))
        for (x, y) in ((-0.15, -0.3), (0.2, 0.2), (-0.35, 0.55), (0.45, 0.75), (0.0, 0.7)):
            d.ellipse([c + r * x - r * 0.09, c + r * y - r * 0.09, c + r * x + r * 0.09, c + r * y + r * 0.09], fill=COL["yellow"])
        d.rounded_rectangle([c - r * 0.95, c + r * 0.92, c + r * 0.95, c + r * 1.15], radius=int(r * 0.1), fill=COL["pink"])
        d.ellipse([c - r * 0.2, c - r * 1.38, c + r * 0.2, c - r * 0.98], fill=COL["yellow"])
    elif kind == "sandia":
        d.polygon([(c - r * 1.1, c - r * 0.75), (c + r * 1.1, c - r * 0.75), (c, c + r * 1.2)], fill=(60, 160, 60))
        d.polygon([(c - r * 0.92, c - r * 0.6), (c + r * 0.92, c - r * 0.6), (c, c + r * 1.0)], fill=(235, 60, 80))
        d.rectangle([c - r * 1.1, c - r * 0.75, c + r * 1.1, c - r * 0.62], fill=(160, 220, 120))
        for (x, y) in ((-0.4, -0.3), (0.0, -0.2), (0.4, -0.3), (-0.15, 0.2), (0.18, 0.25), (0.0, 0.6)):
            d.ellipse([c + r * x - r * 0.05, c + r * y - r * 0.08, c + r * x + r * 0.05, c + r * y + r * 0.08], fill=COL["dark"])
    elif kind == "barco":
        d.polygon([(c - r * 1.1, c + r * 0.6), (c + r * 1.1, c + r * 0.6), (c + r * 0.75, c + r * 1.1), (c - r * 0.75, c + r * 1.1)], fill=COL["brown"])
        d.rectangle([c - r * 0.04, c - r * 1.2, c + r * 0.04, c + r * 0.6], fill=(110, 70, 40))
        d.polygon([(c + r * 0.08, c - r * 1.15), (c + r * 0.95, c + r * 0.45), (c + r * 0.08, c + r * 0.45)], fill=C("red"))
        d.polygon([(c - r * 0.08, c - r * 0.85), (c - r * 0.08, c + r * 0.45), (c - r * 0.75, c + r * 0.45)], fill=(255, 255, 255))
    elif kind == "estrellamar":
        pts = star_pts(c, c + r * 0.05, r * 1.15, r * 0.6)
        d.polygon(pts, fill=C("orange"))
        d.line(pts + [pts[0], pts[1]], fill=(240, 110, 30), width=int(W * 0.025), joint="curve")
        for i in range(5):
            a = math.radians(-90 + i * 72)
            for k in (0.35, 0.65):
                x, y = c + r * k * math.cos(a), c + r * 0.05 + r * k * math.sin(a)
                d.ellipse([x - r * 0.06, y - r * 0.06, x + r * 0.06, y + r * 0.06], fill=(255, 220, 150))
    elif kind == "varita":
        d.line([(c - r * 0.8, c + r * 1.2), (c + r * 0.2, c - r * 0.1)], fill=(150, 90, 200), width=int(W * 0.04))
        d.polygon(star_pts(c + r * 0.35, c - r * 0.35, r * 0.8, r * 0.34), fill=C("yellow"))
        for (x, y, s) in ((0.95, -1.0, 0.12), (-0.3, -0.95, 0.09), (1.1, 0.25, 0.08)):
            d.polygon(star_pts(c + r * x, c + r * y, r * s * 1.6, r * s * 0.5, n=4), fill=COL["yellow"])
    elif kind == "globoc":
        d.line([(c, c + r * 0.8), (c - r * 0.18, c + r * 1.2), (c + r * 0.12, c + r * 1.6)], fill=(110, 110, 125), width=int(W * 0.018))
        d.polygon([(c - r * 0.12, c + r * 0.9), (c + r * 0.12, c + r * 0.9), (c, c + r * 0.72)], fill=C("purple"))
        heart(d, c, c - r * 0.3, r * 0.95, C("purple"))
        d.ellipse([c - r * 0.6, c - r * 0.9, c - r * 0.35, c - r * 0.65], fill=(255, 255, 255, 150))
    elif kind == "galleta":
        heart(d, c, c, r * 1.1, C("orange") if color else (215, 160, 90))
        heart(d, c, c + r * 0.02, r * 0.82, COL["pink"])
        rn = random.Random(3)
        for _ in range(12):
            x, y = c + rn.uniform(-0.45, 0.45) * r, c + rn.uniform(-0.45, 0.35) * r
            d.ellipse([x - r * 0.04, y - r * 0.04, x + r * 0.04, y + r * 0.04], fill=rn.choice([COL["yellow"], COL["cyan"], (255, 255, 255)]))
    elif kind == "sol":
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
        hc = C("green"); d.ellipse([c - r * 0.6, c - r * 0.45, c - r * 0.3, c - r * 0.05], fill=tuple(int(v + (255 - v) * 0.55) for v in hc[:3]))
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
    elif kind in ANIMALS:
        animal_face(d, kind, c, r, W, C)
    elif kind == "granero":
        granero(d, c, r, W)
    elif kind in FRUITS:
        fruit_draw(d, kind, c, r, W, K)
    elif kind.startswith("N_"):   # disco con número (miniatura / carteles): N_11, N_20...
        n_ = int(kind[2:]); col = RAINBOW[(n_ - 1) % 10] if n_ > 0 else COL["red"]; rr = r * 1.25
        d.ellipse([c - rr + W * 0.02, c - rr + W * 0.03, c + rr + W * 0.02, c + rr + W * 0.03], fill=(40, 40, 60, 110))
        d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=col, outline=(255, 255, 255), width=int(W * 0.04))
        d.text((c, c + W * 0.01), str(n_), font=font(rr * (1.3 if n_ < 10 else 1.12)), fill=(255, 255, 255), anchor="mm",
               stroke_width=int(W * 0.025), stroke_fill=COL["dark"])
    elif kind.startswith("L_"):
        letter_draw(im, kind[2:], W, K)
    elif kind in VOWEL_OBJS:
        vowel_obj_draw(im, d, kind, c, r, W, K)
    elif kind.startswith("M_"):   # mancha de pintura con carita: M_red, M_blue, M_white...
        cn = kind[2:]; base = (205, 205, 215) if gray else (color or (COL[cn] if cn != "white" else (250, 250, 252)))
        mancha(d, c, r, W, base[:3])
    elif kind == "gota":
        col = C("blue")
        d.polygon([(c, c - r * 1.25), (c + r * 0.62, c + r * 0.05), (c - r * 0.62, c + r * 0.05)], fill=col)
        d.ellipse([c - r * 0.78, c - r * 0.45, c + r * 0.78, c + r * 1.1], fill=col)
        d.ellipse([c - r * 0.45, c - r * 0.2, c - r * 0.18, c + r * 0.25], fill=(255, 255, 255, 170))
        _eyes(d, c + r * 0.05, c + r * 0.35, r * 0.75); d.arc([c - r * 0.22, c + r * 0.45, c + r * 0.32, c + r * 0.85], 20, 160, fill=COL["dark"], width=int(W * 0.018))
    elif kind == "cohete":
        d.polygon([(c, c - r * 1.4), (c - r * 0.45, c - r * 0.5), (c + r * 0.45, c - r * 0.5)], fill=COL["red"])
        d.rounded_rectangle([c - r * 0.45, c - r * 0.6, c + r * 0.45, c + r * 0.9], radius=int(r * 0.2), fill=(240, 240, 248))
        d.ellipse([c - r * 0.22, c - r * 0.3, c + r * 0.22, c + r * 0.14], fill=COL["cyan"], outline=COL["blue"], width=int(W * 0.015))
        d.polygon([(c - r * 0.45, c + r * 0.3), (c - r * 0.85, c + r * 1.0), (c - r * 0.45, c + r * 0.9)], fill=COL["red"])
        d.polygon([(c + r * 0.45, c + r * 0.3), (c + r * 0.85, c + r * 1.0), (c + r * 0.45, c + r * 0.9)], fill=COL["red"])
    elif kind == "calcetin":   # calcetín (de a pares)
        col = C("red"); lt = (255, 255, 255, 255) if not gray else (235, 235, 240)
        d.rounded_rectangle([c - r * 0.62, c - r * 1.1, c + r * 0.12, c + r * 0.5], radius=int(r * 0.22), fill=col)
        d.rounded_rectangle([c - r * 0.62, c + r * 0.02, c + r * 1.1, c + r * 0.78], radius=int(r * 0.38), fill=col)
        d.pieslice([c + r * 0.55, c + r * 0.02, c + r * 1.1, c + r * 0.78], -90, 90, fill=lt)
        d.pieslice([c - r * 0.62, c + r * 0.02, c - r * 0.02, c + r * 0.78], 90, 180, fill=lt)
        for yy in (-0.55, -0.25):
            d.rectangle([c - r * 0.62, c + r * yy, c + r * 0.12, c + r * (yy + 0.13)], fill=lt)
        d.rounded_rectangle([c - r * 0.7, c - r * 1.22, c + r * 0.2, c - r * 0.88], radius=int(r * 0.12), fill=lt)
    elif kind == "guante":   # guante de lana (mitón)
        col = C("blue"); lt = (255, 255, 255) if not gray else (235, 235, 240)
        d.ellipse([c - r * 1.02, c - r * 0.42, c - r * 0.38, c + r * 0.22], fill=col)
        d.rounded_rectangle([c - r * 0.62, c - r * 1.1, c + r * 0.62, c + r * 0.7], radius=int(r * 0.6), fill=col)
        heart(d, c, c - r * 0.25, r * 0.28, lt)
        d.rounded_rectangle([c - r * 0.7, c + r * 0.55, c + r * 0.7, c + r * 1.15], radius=int(r * 0.14), fill=lt)
        for k in range(5):
            x = c - r * 0.5 + k * r * 0.25
            d.line([(x, c + r * 0.62), (x, c + r * 1.08)], fill=K((210, 210, 225)), width=max(2, int(W * 0.012)))
    elif kind == "zapato":   # zapatilla de lado
        col = C("green"); lt = (255, 255, 255) if not gray else (235, 235, 240)
        d.rounded_rectangle([c - r * 1.12, c + r * 0.45, c + r * 1.18, c + r * 0.8], radius=int(r * 0.16), fill=lt)
        d.rounded_rectangle([c - r * 1.05, c - r * 0.45, c + r * 0.15, c + r * 0.55], radius=int(r * 0.25), fill=col)
        d.ellipse([c - r * 0.5, c - r * 0.1, c + r * 1.18, c + r * 0.62], fill=col)
        d.pieslice([c + r * 0.5, c - r * 0.1, c + r * 1.18, c + r * 0.62], -70, 90, fill=lt)
        d.ellipse([c - r * 0.95, c - r * 0.6, c - r * 0.1, c - r * 0.3], fill=K((70, 60, 80)))
        for k in range(3):
            x = c - r * 0.05 + k * r * 0.2
            d.line([(x - r * 0.12, c - r * 0.25 + k * r * 0.1), (x + r * 0.12, c - r * 0.05 + k * r * 0.1)], fill=lt, width=max(2, int(W * 0.02)))
        d.rectangle([c - r * 1.0, c + r * 0.1, c - r * 0.6, c + r * 0.2], fill=lt)
    elif kind == "cereza":   # par de cerezas
        col = C("red"); stem = K((90, 150, 50))
        d.line([(c - r * 0.5, c + r * 0.2), (c + r * 0.15, c - r * 0.95)], fill=stem, width=max(2, int(W * 0.028)))
        d.line([(c + r * 0.55, c + r * 0.3), (c + r * 0.15, c - r * 0.95)], fill=stem, width=max(2, int(W * 0.028)))
        _leaf(d, K, c + r * 0.5, c - r * 0.95, r * 0.42, r * 0.2, -25)
        for (x, y) in ((-0.5, 0.58), (0.55, 0.66)):
            d.ellipse([c + r * x - r * 0.48, c + r * y - r * 0.46, c + r * x + r * 0.48, c + r * y + r * 0.46], fill=col)
            d.ellipse([c + r * (x - 0.28), c + r * (y - 0.28), c + r * (x - 0.08), c + r * (y - 0.08)], fill=(255, 255, 255, 200) if not gray else (240, 240, 245))
    elif kind in OPP_SPRITES:
        opp_sprite_draw(d, kind, c, r, W, C, K)
    elif kind in WEEK_SPRITES:
        week_sprite_draw(d, kind, c, r, W, C, K)
    elif kind.startswith("cal_"):   # hoja de calendario: cal_1..cal_7, cal_0 = '?'
        calendar_draw(d, int(kind[4:]), c, r, W)
    return im.resize((size, size), Image.LANCZOS)

KIND = {n: OBJS[n][0] for n in OBJS}
KIND_NAMES = {"sol", "pez", "globo", "manzana", "estrella", "flor", "burbuja", "pelota", "nube", "corazon"}
_sp = {}
def sprite(kind, size, color=None, gray=False, face=False):
    k = (kind, size, color, gray, face)
    if k not in _sp: _sp[k] = obj_sprite(kind, size, color, gray, face)
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

def big_word(d, L, word, ch, tt, y, size):
    """Palabra grande con la primera letra en el color de la vocal."""
    p = elastic(tt / 0.6)
    if p <= 0: return
    f = font(size * p); ws = [f.getlength(c) for c in word]; gap = 6 * p; tot = sum(ws) + gap * (len(word) - 1)
    x = L.W / 2 + 30 - tot / 2
    for k, c in enumerate(word):
        col = COL[VCOL.get(ch, "red")] if k == 0 else (255, 255, 255)
        outlined(d, (x + ws[k] / 2, y + math.sin(tt * 5 + k) * 6), c, f, col, sw=max(1, int(11 * p)))
        x += ws[k] + gap

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
    if kind == "count" and b["args"][0] == 5 and len(b["args"]) == 1: night = min(1, bt / 0.8) * 0.85 * min(1, max(0, (b["end"] - t) / 0.6))
    im = scen.frame(t, night); d = ImageDraw.Draw(im)
    who, env = speaking(t)
    danc = 1.0 if (kind == "dance" and b["dancing"] and t >= b["dancing"]) or kind in ("title", "end") else 0.0
    if kind in ("review", "sreview", "freview", "bowl", "lreview", "review20", "rainbow", "hop", "week", "day") and b["confetti"] and t >= b["confetti"]: danc = 1.0
    if kind == "cmd" and b["rpops"] and t >= b["rpops"][0][1]: danc = 0.6
    if kind == "oreview" and b["confetti"] and t >= b["confetti"]: danc = 1.0
    # ----- contenido -----
    if kind == "title" or kind == "end":
        txt1, txt2 = TITLE if kind == "title" else ("¡HASTA LA", "PRÓXIMA!")
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
        n = b["args"][0]; ok = (b["args"][1] if len(b["args"]) > 1 else KIND[n]) if kind == "count" else b["args"][1]
        size = 300 if n <= 4 else 240 if n <= 8 else 210
        if ok in SHAPES: size = int(size * 0.8)
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
        if not (L.v and SHORT_TITLE):   # en el Short el título ya hace la pregunta
            outlined(d, (L.W / 2 + 20, L.num_c[1] - 10), "¿QUÉ NÚMERO FALTA?", font(96 if not L.v else 70), COL["purple"], sw=10)
        for k, v in enumerate(seq):
            if not L.v: x, y = L.W * (0.245 + 0.118 * k), L.H * 0.42
            else: x, y = L.W * (0.27 + 0.46 * (k % 2)), L.H * (0.31 + 0.20 * (k // 2))
            tt = bt - k * 0.25
            if tt < 0: continue
            if k == miss and not (b["fill"] and t >= b["fill"]):
                p = elastic(tt / 0.6); r = (95 if not L.v else 135) * p
                d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 200, 215), outline=(255, 255, 255), width=10)
                outlined(d, (x, y + math.sin(t * 6) * 6), "?", font(r * 1.3), (255, 255, 255), sw=6)
            else:
                tt2 = (t - b["fill"]) if (k == miss) else tt
                numeral_disc(im, d, L, v, tt2, word=False, cx=x, cy=y, r=95 if not L.v else 135)
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
    elif kind == "card":   # cartel de sección: ("scene", "card", "TEXTO", "color")
        txt = b["args"][0]; cn = b["args"][1] if len(b["args"]) > 1 else "yellow"
        big = 150 if len(txt) <= 11 else (115 if len(txt) <= 17 else 96) if not L.v else (80 if len(txt) <= 17 else 66)
        banner(d, L, txt, bt, y=L.H * (0.30 if not L.v else 0.27), size=big, col=COL[cn])
        if len(b["args"]) > 2:   # objetos opcionales que aparecen debajo del cartel
            objs = b["args"][2]; sz = 300 if L.v else 240
            box = (L.stage[0], L.stage[1] + (120 if L.v else 140), L.stage[2], L.stage[3] + (40 if L.v else 0))
            gp = grid_positions(len(objs), box, sz)
            if all(o.startswith("L_") for o in objs):   # letras: una sola fila
                sz = 230; gp = [(L.W / 2 + 30 + (k - (len(objs) - 1) / 2) * 175, (L.stage[1] + L.stage[3]) / 2 + 120) for k in range(len(objs))]
            for k, (x, y) in enumerate(gp):
                paste_c(im, sprite(objs[k], sz), x, y + math.sin(t * 3 + k) * 8, elastic((bt - 0.5 - k * 0.25) / 0.45), math.sin(t * 2 + k) * 5)
    elif kind == "shape":  # forma grande que se dibuja: trace -> fill (cara) -> reveal (nombre) -> side i (lados/puntas)
        sk = b["args"][0]; cx = (L.stage[0] + L.stage[2]) / 2; cy = (L.stage[1] + L.stage[3]) / 2 + (40 if not L.v else 60)
        R = 225 if not L.v else 250; col = COL[SHAPE_COL[sk]]
        pts = shape_pts(sk, cx, cy, R, 240)
        filled = b["fill"] is not None and t >= b["fill"]
        if not filled:
            for k in range(0, len(pts), 6):
                x, y = pts[k]; d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 255))
            if b["trace"] is not None and t >= b["trace"]:
                p = clamp((t - b["trace"]) / 3.2); pp = partial_path(pts, p)
                if len(pp) > 1:
                    d.line(pp, fill=COL["dark"], width=24, joint="curve"); d.line(pp, fill=col, width=16, joint="curve")
                x, y = pp[-1]
                if p < 1:
                    d.polygon(star_pts(x, y, 34 + 6 * math.sin(t * 20), 14), fill=COL["yellow"], outline=COL["dark"])
        else:
            paste_c(im, sprite(sk, int(R / 0.389), face=True), cx, cy, elastic((t - b["fill"]) / 0.5))
            v = shape_verts(sk, cx, cy, R)
            for i, tt in b["sides"]:
                if t < tt or not v: continue
                p = ease((t - tt) / 0.35)
                if sk == "estrellaf":
                    x, y = v[2 * (i - 1)]; dx, dy = x - cx, y - cy; m = math.hypot(dx, dy) or 1
                    d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=COL["yellow"], outline=COL["dark"], width=4)
                    badge(d, x + dx / m * 62, y + dy / m * 62, str(i), r=int(34 * p) + 1)
                else:
                    a, c2 = v[i - 1], v[i % len(v)]
                    e2 = (a[0] + (c2[0] - a[0]) * p, a[1] + (c2[1] - a[1]) * p)
                    d.line([a, e2], fill=COL["dark"], width=26); d.line([a, e2], fill=COL["yellow"], width=16)
                    mx, my = (a[0] + c2[0]) / 2, (a[1] + c2[1]) / 2; dx, dy = mx - cx, my - cy; m = math.hypot(dx, dy) or 1
                    badge(d, mx + dx / m * 62, my + dy / m * 62, str(i), r=int(34 * p) + 1)
        if q_on(b, t): qmark(d, L, t)
        elif b["reveal"] is not None and t >= b["reveal"]:
            banner(d, L, SHAPE_NAME[sk], t - b["reveal"], size=120, col=col)
    elif kind == "world":  # cosas del mundo con esa forma: ("scene", "world", forma, [obj1, obj2, obj3]) + pop i
        sk, objs = b["args"]; size = 270 if not L.v else 250
        pos = grid_positions(len(objs), (L.stage[0], L.stage[1] + 60, L.stage[2], L.stage[3] + 20), size)
        banner(d, L, SHAPE_NAME[sk], bt, size=110, col=COL[SHAPE_COL[sk]])
        shown = dict(b["pops"])
        for i, (x, y) in enumerate(pos, 1):
            if i in shown and t >= shown[i]:
                wob = math.sin(t * 2.5 + i) * 5
                paste_c(im, sprite(objs[i - 1], size), x, y + wob, elastic((t - shown[i]) / 0.45), math.sin(t * 2 + i) * 3)
            elif bt > 0.5:
                paste_c(im, sprite(sk, int(size * 0.62), gray=True), x, y, 1.0, 0, alpha=0.45)
    elif kind == "sshow":  # ¿qué forma es? / ¿de qué color es?: ("scene", "sshow", forma, color, texto|None)
        sk, cn = b["args"][0], b["args"][1]; txt = b["args"][2] if len(b["args"]) > 2 else None
        cx = (L.stage[0] + L.stage[2]) / 2; cy = (L.stage[1] + L.stage[3]) / 2 + 40
        paste_c(im, sprite(sk, 560, color=COL[cn], face=True), cx, cy + math.sin(t * 3) * 8, elastic(bt / 0.5))
        if q_on(b, t): qmark(d, L, t)
        elif b["reveal"] is not None and t >= b["reveal"]:
            banner(d, L, txt or SHAPE_NAME[sk], t - b["reveal"], size=130, col=COL[cn])
    elif kind == "spattern":  # ¿qué forma falta?: ("scene", "spattern", [formas], idx) + fill
        seq, miss = b["args"][0], b["args"][1]; n = len(seq); sp = min(250, 900 / max(1, n - 1)); size = int(min(220, sp * 0.9))
        y0 = L.H * (0.40 if not L.v else 0.42); x0 = L.W / 2 - sp * (n - 1) / 2
        outlined(d, (L.W / 2, L.num_c[1]), b["args"][2] if len(b["args"]) > 2 else "¿QUÉ FORMA FALTA?", font(80 if not L.v else 64), COL["purple"], sw=9)
        for k, sk in enumerate(seq):
            x = x0 + k * sp if not L.v else L.W * (0.25 + 0.5 * (k % 2)); y = y0 if not L.v else L.H * (0.30 + 0.15 * (k // 2))
            tt = bt - k * 0.25
            if tt < 0: continue
            if k == miss and not (b["fill"] is not None and t >= b["fill"]):
                p = elastic(tt / 0.6); h = size * 0.42 * p
                d.rounded_rectangle([x - h, y - h, x + h, y + h], radius=int(h * 0.25) + 1, fill=(215, 215, 228), outline=(255, 255, 255), width=8)
                outlined(d, (x, y + math.sin(t * 6) * 6), "?", font(max(1, h * 1.4)), (255, 255, 255), sw=6)
            else:
                st = (t - b["fill"]) if k == miss else tt
                paste_c(im, sprite(sk, size), x, y + math.sin(t * 2.5 + k) * 4, elastic(st / 0.45))
    elif kind == "house":  # casita hecha de formas: pop 1..6
        hx = L.W / 2 + (0 if not L.v else 0); gy = L.H * (0.66 if not L.v else 0.58)
        parts = [("cuadrado", "yellow", hx, gy - 150, 172), ("triangulo", "red", hx, gy - 300 - 0.78 * 172 + 14, 172),
                 ("circulo", "cyan", hx - 70, gy - 190, 46), ("cuadrado", "brown", hx + 62, gy - 62, 70),
                 ("corazonf", "pink", hx + 62, gy - 66, 26), ("estrellaf", "yellow", hx - (330 if not L.v else 300), gy - (420 if not L.v else 560), 66)]
        shown = dict(b["pops"])
        for i, (sk, cn, x, y, R) in enumerate(parts, 1):
            if i in shown and t >= shown[i]:
                paste_c(im, sprite(sk, int(R / 0.389), color=COL[cn]), x, y, elastic((t - shown[i]) / 0.5))
    elif kind == "sreview":  # repaso de todas las formas: rpop 1..5 + confetti
        pos = [(600, 300), (960, 300), (1320, 300), (780, 600), (1140, 600)] if not L.v else \
              [(290, 620), (790, 620), (290, 960), (790, 960), (540, 1170)]
        for i, tt in b["rpops"]:
            if t < tt: continue
            sk = SHAPES[i - 1]; x, y = pos[i - 1]; y += math.sin(t * 3 + i) * 6
            paste_c(im, sprite(sk, 250, face=True), x, y, elastic((t - tt) / 0.5))
            if t - tt > 0.3: outlined(d, (x, y + 132), SHAPE_NAME[sk], font(46), (255, 255, 255), sw=7)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "size":   # grande y pequeño: ("scene", "size", objeto, lado_grande "L"|"R", meta "big"|"small", "GRANDE", "PEQUEÑO") + reveal
        ok, bside, goal = b["args"][0], b["args"][1], b["args"][2]
        lb = b["args"][3] if len(b["args"]) > 3 else "GRANDE"; ls = b["args"][4] if len(b["args"]) > 4 else "PEQUEÑO"
        cy = (L.stage[1] + L.stage[3]) / 2 + (30 if not L.v else 40)
        xl, xr = (L.W * 0.36, L.W * 0.64) if not L.v else (L.W * 0.32, L.W * 0.75)
        big_s = 440 if not L.v else 540; sm_s = 190 if not L.v else 210
        items = [("big", xl if bside == "L" else xr, big_s, lb), ("small", xr if bside == "L" else xl, sm_s, ls)]
        rev = b["reveal"] is not None and t >= b["reveal"]
        for k, (role, x, s, lab) in enumerate(items):
            tt = bt - k * 0.35
            if tt < 0: continue
            yy = cy + (big_s - s) * 0.36 + math.sin(t * 2.5 + k) * 5
            sc = elastic(tt / 0.5); alpha = 1.0
            if rev:
                rt = t - b["reveal"]
                if role == goal:
                    sc *= 1 + 0.10 * abs(math.sin(rt * 5)) * math.exp(-rt * 0.6)
                    rr = s * 0.55 + 8 * math.sin(t * 6)
                    d.ellipse([x - rr, yy - rr, x + rr, yy + rr], outline=COL["yellow"], width=14)
                else:
                    alpha = 0.55
            paste_c(im, sprite(ok, s), x, yy, sc, math.sin(t * 2 + k) * 3, alpha=alpha)
            if rev:
                rt = t - b["reveal"]; ly = cy + big_s * 0.36 + (60 if not L.v else 70)
                fsz = (64 if role == "big" else 50) if not L.v else (62 if role == "big" else 48)
                p = elastic((rt - (0 if role == goal else 0.4)) / 0.5)
                if p > 0:
                    outlined(d, (x, ly), lab, font(fsz * p), COL["yellow"] if role == goal else (255, 255, 255), sw=max(1, int(8 * p)))
        if q_on(b, t): qmark(d, L, t)
    elif kind == "animal":  # ¿quién hace...?: ("scene", "animal", animal, "¡MUU!", "VACA") + qmark (sonido) + reveal
        ak, snd, name = b["args"][0], b["args"][1], b["args"][2]
        cx = (L.stage[0] + L.stage[2]) / 2; cy = (L.stage[1] + L.stage[3]) / 2 + (30 if not L.v else 70)
        sz = 560 if not L.v else 780
        rev = b["reveal"] is not None and t >= b["reveal"]
        spr = sprite(ak, sz)
        if not rev:
            key = ("sil", ak, sz)
            if key not in _sp: _sp[key] = silhouette(spr)
            wig = math.sin(t * 3) * 4
            paste_c(im, _sp[key], cx, cy + math.sin(t * 2.5) * 6, elastic(bt / 0.5), wig)
            if bt > 0.4: outlined(d, (cx, cy + 10 + math.sin(t * 6) * 8), "?", font(260), (255, 255, 255), sw=12)
        else:
            rt = t - b["reveal"]
            paste_c(im, spr, cx, cy + math.sin(t * 2.5) * 6, elastic(rt / 0.5) * (1 + 0.06 * math.sin(t * 4)), math.sin(t * 3) * 4)
        ys = L.num_c[1] + (40 if L.v else -10)
        if q_on(b, t) or rev:
            qt = next((tt for v, tt in b["q"] if v), t)
            p = elastic((t - qt) / 0.5)
            if rev: p = 1.0
            fs = (120 if not rev else 64) if L.v else (110 if not rev else 60)
            yy = ys if not rev else ys + (120 if L.v else 90)
            if p > 0:
                xs = cx + (0 if L.v else 380)
                outlined(d, (xs, yy + math.sin(t * 8) * 6), snd, font(fs * p), COL["yellow"] if not rev else (255, 255, 255), sw=max(1, int(11 * p)))
        if rev:
            banner(d, L, name, t - b["reveal"], y=ys - (0 if L.v else 0), size=140 if L.v else 120, col=COL[ANIMAL_COL[ak]])
    elif kind == "fruit":  # ¿qué fruta es? / ¿de qué color es?: ("scene", "fruit", fruta, "guess"|"color", "TEXTO", color) + qmark + reveal
        fk, mode, lab, cn = b["args"][0], b["args"][1], b["args"][2], b["args"][3]
        cx = (L.stage[0] + L.stage[2]) / 2; cy = (L.stage[1] + L.stage[3]) / 2 + (50 if not L.v else 80)
        sz = 500 if not L.v else 720
        rev = b["reveal"] is not None and t >= b["reveal"]
        bob = math.sin(t * 2.5) * 6; rot = math.sin(t * 2) * 4
        if not rev:
            if mode == "guess":
                key = ("sil", fk, sz)
                if key not in _sp: _sp[key] = silhouette(sprite(fk, sz))
                paste_c(im, _sp[key], cx, cy + bob, elastic(bt / 0.5), rot)
                if bt > 0.4: outlined(d, (cx, cy + 10 + math.sin(t * 6) * 8), "?", font(240), (255, 255, 255), sw=12)
            else:
                paste_c(im, sprite(fk, sz, gray=True), cx, cy + bob, elastic(bt / 0.5), rot)
        else:
            rt = t - b["reveal"]
            paste_c(im, sprite(fk, sz), cx, cy + bob, (0.85 + 0.15 * elastic(rt / 0.5)) * (1 + 0.05 * math.sin(t * 4)), rot)
            if rt < 1.2:
                for k in range(10):
                    a = k * 36 + rt * 90; rr = 200 + rt * 260
                    d.polygon(star_pts(cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)), 26 * (1.2 - rt), 10 * (1.2 - rt)), fill=RAINBOW[k])
            banner(d, L, lab, rt, size=130 if len(lab) <= 10 else 105, col=COL[cn])
        if q_on(b, t) and mode == "color": qmark(d, L, t)
        elif q_on(b, t) and bt > 0.4: outlined(d, (L.W / 2, L.num_c[1] + math.sin(t * 6) * 10), "¿QUÉ FRUTA ES?", font(90 if not L.v else 76), COL["yellow"], sw=10)
    elif kind == "bowl":  # ensalada de frutas: ("scene", "bowl", [frutas]) + pop i (cae la fruta i) + confetti
        objs = b["args"][0]; n = len(objs)
        bx = L.W * (0.52 if not L.v else 0.5); top = L.H * (0.60 if not L.v else 0.56); bw = 330 if not L.v else 400; bh = 250 if not L.v else 290
        banner(d, L, "¡ENSALADA DE FRUTAS!", bt, y=L.num_c[1] - (10 if not L.v else -60), size=96 if not L.v else 70, col=COL["orange"])
        shown = dict(b["pops"]); fs = 220 if not L.v else 250
        front = [k for k in range(n) if k % 2 == 0]; back = [k for k in range(n) if k % 2 == 1]; slots = [None] * n
        for row, ks, yy in ((0, front, top - 75), (1, back, top - 175)):
            for j, k in enumerate(ks):
                span = bw * (1.3 if row == 0 else 0.95); m = len(ks)
                slots[k] = (bx + (j - (m - 1) / 2) * (span / max(1, m - 1)), yy - (25 if row == 1 and j == (m - 1) / 2 else 0))
        order = sorted(range(n), key=lambda k: slots[k][1])
        for k in order:
            i = k + 1
            if i not in shown or t < shown[i]: continue
            ft = t - shown[i]; tx, ty = slots[k]
            p = clamp(ft / 0.45); y = ty - (1 - p) ** 2 * 650
            sq = 1 + (0.12 * math.sin(min(1, (ft - 0.45) / 0.3) * math.pi) if ft > 0.45 else 0)
            paste_c(im, sprite(objs[k], fs), tx, y + (math.sin(t * 3 + k) * 3 if p >= 1 else 0), sq, (k - n / 2) * 6)
        d.chord([bx - bw, top - bh, bx + bw, top + bh], 0, 180, fill=(255, 255, 255), outline=COL["dark"], width=8)
        d.chord([bx - bw * 0.93, top - bh * 0.93 + 40, bx + bw * 0.93, top + bh * 0.93 - 10], 10, 170, fill=COL["cyan"])
        for k in range(7):
            x = bx - bw * 0.7 + k * bw * 0.233; d.ellipse([x - 16, top + 70 - 16, x + 16, top + 70 + 16], fill=COL["yellow"])
        d.rounded_rectangle([bx - bw - 14, top - 14, bx + bw + 14, top + 14], radius=14, fill=(255, 255, 255), outline=COL["dark"], width=7)
        d.rounded_rectangle([bx - bw * 0.35, top + bh - 8, bx + bw * 0.35, top + bh + 26], radius=12, fill=(255, 255, 255), outline=COL["dark"], width=7)
    elif kind == "freview":  # repaso de frutas: ("scene", "freview", [(fruta, "NOMBRE")...]) + rpop i + confetti
        items = b["args"][0]; n = len(items); sz = 200 if not L.v else 230
        box = (L.stage[0], L.stage[1] - 20, L.stage[2], L.stage[3] - 80) if not L.v else (L.stage[0], L.stage[1] - 60, L.stage[2], L.stage[3] + 80)
        big_n = n > 6 and not L.v   # muchos elementos: más chicos y corridos a la derecha (lejos de Tula)
        if big_n: sz = 175; box = (560, 150, 1440, 660)
        pos = grid_positions(n, box, sz) if not L.v else [(L.W * (0.2 + 0.3 * (k % 3)), box[1] + 150 + 270 * (k // 3)) for k in range(n)]
        for i, tt in b["rpops"]:
            if t < tt: continue
            fk, nm = items[i - 1]; x, y = pos[i - 1]; y += math.sin(t * 3 + i) * 6
            paste_c(im, sprite(fk, sz), x, y, elastic((t - tt) / 0.5), math.sin(t * 2 + i) * 4)
            if t - tt > 0.3: outlined(d, (x, y + sz * 0.56), nm, font((34 if big_n else 40) if not L.v else 46), (255, 255, 255), sw=6 if big_n else 7)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "letter":  # vocal grande: ("scene", "letter", "A") + pop 2 (minúscula)
        ch = b["args"][0]; cx = (L.stage[0] + L.stage[2]) / 2 + 20; cy = (L.stage[1] + L.stage[3]) / 2 + 40
        low = dict(b["pops"]).get(2)
        sh = ease((t - low) / 0.5) if (low is not None and t >= low) else 0.0
        paste_c(im, sprite("L_" + ch, 560), cx - 200 * sh, cy + math.sin(t * 3) * 10, elastic(bt / 0.6), math.sin(t * 2.2) * 4)
        if sh > 0:
            paste_c(im, sprite("L_" + ch.lower(), 470), cx + 230, cy + 30 + math.sin(t * 3 + 1) * 10, elastic((t - low) / 0.6), math.sin(t * 2.2 + 1) * 4)
        for k in range(6):   # estrellitas alrededor
            a = t * 0.8 + k * math.pi / 3; rr = 330 + 20 * math.sin(t * 2 + k)
            x, y = cx + rr * 1.25 * math.cos(a), cy + rr * 0.75 * math.sin(a)
            if L.stage[0] - 40 < x < L.stage[2] + 20 and bt > 0.6:
                d.polygon(star_pts(x, y, 22, 9), fill=RAINBOW[k])
    elif kind == "word":  # palabra que empieza con la vocal: ("scene", "word", objeto, "ABEJA", "A") + qmark + reveal
        ok, wd, ch = b["args"][0], b["args"][1], b["args"][2]
        cx = (L.stage[0] + L.stage[2]) / 2 + 20; cy = (L.stage[1] + L.stage[3]) / 2 + 70
        rev = b["reveal"] is not None and t >= b["reveal"]
        sc = elastic(bt / 0.5) * (1 + (0.05 * math.sin(t * 4) if rev else 0))
        paste_c(im, sprite(ok, 470), cx, cy + math.sin(t * 2.5) * 7, sc, math.sin(t * 2) * 4)
        if rev:
            rt = t - b["reveal"]
            if rt < 1.2:
                for k in range(10):
                    a = k * 36 + rt * 90; rr = 190 + rt * 250
                    d.polygon(star_pts(cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)), 26 * (1.2 - rt), 10 * (1.2 - rt)), fill=RAINBOW[k])
            big_word(d, L, wd, ch, rt, L.num_c[1] - 5, 130 if len(wd) <= 6 else 112)
        elif q_on(b, t):
            outlined(d, (L.W / 2 + 20, L.num_c[1] + math.sin(t * 6) * 10), "¿QUÉ ES?", font(110), COL["yellow"], sw=11)
    elif kind == "vstart":  # ¿con qué vocal empieza?: ("scene", "vstart", objeto, "OSO", "O") + qmark + reveal
        ok, wd, ch = b["args"][0], b["args"][1], b["args"][2]
        cx = (L.stage[0] + L.stage[2]) / 2 + 30
        rev = b["reveal"] is not None and t >= b["reveal"]
        if L.v: cx = L.W / 2
        paste_c(im, sprite(ok, 330 if not L.v else 500), cx, (375 if not L.v else 760) + math.sin(t * 2.5) * 6, elastic(bt / 0.5), math.sin(t * 2) * 3)
        for k, v in enumerate(VOWELS):
            x = (cx + 40 + (k - 2) * 150) if not L.v else (cx + (k - 2) * 190); y = (640 if not L.v else 1120) + math.sin(t * 3 + k) * 5; tt = bt - 0.4 - k * 0.15
            if tt < 0: continue
            sc = elastic(tt / 0.45); al = 1.0
            if rev:
                if v == ch:
                    rt = t - b["reveal"]; sc *= 1.25 + 0.08 * math.sin(rt * 7)
                    rr = (92 if not L.v else 105) + 5 * math.sin(t * 6); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 230), outline=COL["yellow"], width=12)
                else: al = 0.35
            paste_c(im, sprite("L_" + v, 175 if not L.v else 200), x, y, sc, 0, alpha=al)
        if rev: big_word(d, L, wd, ch, t - b["reveal"], L.num_c[1] - 10, 120)
        elif not L.v: outlined(d, (L.W / 2 + 30, L.num_c[1] - 10), "¿CON QUÉ VOCAL EMPIEZA?", font(70), COL["yellow"], sw=9)
        else:
            for j, ln in enumerate(("¿CON QUÉ VOCAL", "EMPIEZA?")): outlined(d, (L.W / 2, L.num_c[1] - 30 + j * 86), ln, font(78), COL["yellow"], sw=9)
    elif kind == "lfind":  # ¿dónde está la...?: ("scene", "lfind", ["E","O","A"], idx, "A") + qmark + reveal
        seq, idx, ch = b["args"][0], b["args"][1], b["args"][2]
        cx = (L.stage[0] + L.stage[2]) / 2 + 30
        rev = b["reveal"] is not None and t >= b["reveal"]
        outlined(d, (L.W / 2 + 30, L.num_c[1] - 10), f"¿DÓNDE ESTÁ LA {ch}?", font(90), COL["yellow"], sw=10)
        for k, v in enumerate(seq):
            x = cx + 10 + (k - (len(seq) - 1) / 2) * 300; y = 490 + math.sin(t * 2.6 + k) * 8; tt = bt - k * 0.25
            if tt < 0: continue
            sc = elastic(tt / 0.5); al = 1.0
            if rev:
                if k == idx:
                    rt = t - b["reveal"]; sc *= 1.12 + 0.08 * math.sin(rt * 6)
                    rr = 150 + 6 * math.sin(t * 6); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 200), outline=COL["yellow"], width=16)
                else: al = 0.4
            paste_c(im, sprite("L_" + v, 300), x, y, sc, math.sin(t * 2 + k) * 4, alpha=al)
    elif kind == "lpattern":  # ¿qué vocal falta?: ("scene", "lpattern", ["A","E","I","O","U"], idx) + fill
        seq, miss = b["args"][0], b["args"][1]
        cx = (L.stage[0] + L.stage[2]) / 2 + 30
        if L.v: cx = L.W / 2 + 10
        outlined(d, (L.W / 2 + (30 if not L.v else 0), L.num_c[1] - 10), "¿QUÉ VOCAL FALTA?", font(96 if not L.v else 84), COL["purple"], sw=10)
        for k, v in enumerate(seq):
            x = cx - 10 + (k - 2) * (170 if not L.v else 195); y = (480 if not L.v else 800) + math.sin(t * 2.6 + k) * 6; tt = bt - k * 0.22
            if tt < 0: continue
            if k == miss and not (b["fill"] is not None and t >= b["fill"]):
                p = elastic(tt / 0.6); h = (70 if not L.v else 82) * p
                d.rounded_rectangle([x - h, y - h * 1.2, x + h, y + h * 1.2], radius=int(h * 0.3) + 1, fill=(215, 215, 228), outline=(255, 255, 255), width=8)
                outlined(d, (x, y + math.sin(t * 6) * 6), "?", font(max(1, h * 1.6)), (255, 255, 255), sw=6)
            else:
                st = (t - b["fill"]) if k == miss else tt
                paste_c(im, sprite("L_" + v, 220 if not L.v else 250), x, y, elastic(st / 0.45) * (1.15 if k == miss else 1.0))
    elif kind == "lreview":  # repaso: ("scene", "lreview", [("A", "abeja", "ABEJA")...]) + rpop i + confetti
        items = b["args"][0]; cx = (L.stage[0] + L.stage[2]) / 2 + 30
        for i, tt in b["rpops"]:
            if t < tt: continue
            ch, ok, wd = items[i - 1]; x = cx + 40 + (i - 3) * 188; ph = math.sin(t * 3 + i) * 6
            p = elastic((t - tt) / 0.5)
            paste_c(im, sprite("L_" + ch, 230), x, 285 + ph, p)
            paste_c(im, sprite(ok, 195), x, 515 + ph, elastic((t - tt - 0.25) / 0.5), math.sin(t * 2 + i) * 4)
            if t - tt > 0.4: outlined(d, (x, 645 + ph), wd, font(38), (255, 255, 255), sw=6)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "teens":  # del 11 al 20 con dos cajitas de diez: ("scene", "teens", n, objeto, visibles_al_inicio) + pop i | popall + numeral + reveal
        n, ok, init = b["args"][0], b["args"][1], b["args"][2]
        if not L.v: cs = 92; fx = [L.W / 2 - 255, L.W / 2 + 255]; fy = [500, 500]
        else: cs = 150; fx = [L.W / 2, L.W / 2]; fy = [650, 975]
        def cell(i):
            f_, j = divmod(i - 1, 10); r_, c_ = divmod(j, 5)
            return f_, fx[f_] + (c_ - 2) * cs, fy[f_] + (r_ - 0.5) * cs
        for f_ in (0, 1):   # las dos cajitas
            if f_ == 1 and n <= 10: continue
            p = elastic(bt / 0.5); x0, y0 = fx[f_] - 2.5 * cs - 12, fy[f_] - cs - 12
            if p <= 0: continue
            w2, h2 = (5 * cs + 24) * p / 2, (2 * cs + 24) * p / 2
            d.rounded_rectangle([fx[f_] - w2 + 6, fy[f_] - h2 + 9, fx[f_] + w2 + 6, fy[f_] + h2 + 9], radius=int(22 * p) + 1, fill=(60, 110, 60))
            d.rounded_rectangle([fx[f_] - w2, fy[f_] - h2, fx[f_] + w2, fy[f_] + h2], radius=int(22 * p) + 1, fill=(255, 250, 232), outline=COL["dark"], width=6)
            if p > 0.95:
                for j in range(10):
                    r_, c_ = divmod(j, 5); cx_, cy_ = fx[f_] + (c_ - 2) * cs, fy[f_] + (r_ - 0.5) * cs
                    d.rounded_rectangle([cx_ - cs / 2 + 5, cy_ - cs / 2 + 5, cx_ + cs / 2 - 5, cy_ + cs / 2 - 5], radius=12, outline=(214, 205, 185), width=3)
        if init > 0: shown = {i: b["start"] + 0.35 + 0.05 * i for i in range(1, init + 1)}
        else: shown = {i: b["popall"] + 0.07 * i for i in range(1, n + 1)} if b["popall"] else {}
        for i, tt in b["pops"]: shown[i] = tt
        spr = sprite(ok, int(cs * 0.86))
        for i in range(1, n + 1):
            if i not in shown or t < shown[i]: continue
            f_, x, y = cell(i); tt = t - shown[i]
            new = any(i == pi for pi, _ in b["pops"])
            sc = elastic(tt / 0.45) * ((1 + 0.12 * math.sin(t * 7)) if new and tt < 3 else 1)
            if new and tt < 1.0:
                for k in range(8):
                    a = math.radians(k * 45 + tt * 120); rr = cs * 0.6 + tt * cs * 1.2
                    d.polygon(star_pts(x + rr * math.cos(a), y + rr * math.sin(a), 16 * (1 - tt) + 1, 6 * (1 - tt) + 1), fill=RAINBOW[k])
            paste_c(im, spr, x, y + math.sin(t * 2.5 + i) * 2, sc, math.sin(t * 2 + i) * 4)
        if b["reveal"] is not None and t >= b["reveal"]:   # 10 + k debajo de las cajitas
            rt = t - b["reveal"]; k_ = n - 10
            if not L.v:
                ly = fy[0] + cs + 62
                outlined(d, (fx[0], ly), "10", font(78 * elastic(rt / 0.5) + 1), COL["yellow"], sw=9)
                outlined(d, (L.W / 2, ly), "+", font(78 * elastic((rt - 0.15) / 0.5) + 1), (255, 255, 255), sw=9)
                outlined(d, (fx[1], ly), str(k_), font(78 * elastic((rt - 0.3) / 0.5) + 1), COL["yellow"], sw=9)
            else:
                outlined(d, (L.W / 2, fy[1] + cs + 70), f"10 + {k_}", font(90 * elastic(rt / 0.5) + 1), COL["yellow"], sw=10)
        if q_on(b, t): qmark(d, L, t)
        if b["numeral"] and t >= b["numeral"][1]:
            numeral_disc(im, d, L, b["numeral"][0], t - b["numeral"][1])
    elif kind == "numq":  # ¿qué número es?: ("scene", "numq", n, objeto) + qmark + reveal
        n, ok = b["args"][0], b["args"][1]
        cx = L.W / 2 + (20 if not L.v else 0); cy = (L.stage[1] + L.stage[3]) / 2 + (60 if not L.v else 40)
        rev = b["reveal"] is not None and t >= b["reveal"]
        pul = (1 + 0.05 * math.sin((t - b["reveal"]) * 7)) if rev else 1
        for k, sx in enumerate((-1, 1)):
            paste_c(im, sprite(ok, 170), cx + sx * (360 if not L.v else 330), cy + 40 + math.sin(t * 2.5 + k * 2) * 10, elastic((bt - 0.4) / 0.5), math.sin(t * 2 + k) * 8)
        numeral_disc(im, d, L, n, bt, word=False, cx=cx, cy=cy + math.sin(t * 2.2) * 6, r=int(200 * pul))
        if rev:
            rt = t - b["reveal"]
            if rt < 1.2:
                for k in range(10):
                    a = math.radians(k * 36 + rt * 90); rr = 230 + rt * 260
                    d.polygon(star_pts(cx + rr * math.cos(a), cy + rr * math.sin(a), 26 * (1.2 - rt), 10 * (1.2 - rt)), fill=RAINBOW[k])
            banner(d, L, WORDS[n].upper(), rt, y=L.num_c[1] - 5, size=130, col=RAINBOW[(n - 1) % 10])
        else:
            outlined(d, (L.W / 2 + 20, L.num_c[1] - 5 + math.sin(t * 6) * 6), "¿QUÉ NÚMERO ES?", font(96 if not L.v else 80), COL["yellow"], sw=10)
    elif kind == "review20":  # contar del 1 al N (10 o 20): ("scene", "review20", N) + rpop i + confetti
        N = b["args"][0]
        last = 0
        for i, tt in b["rpops"]:
            if t < tt: continue
            last = max(last, i)
            if not L.v:
                r_, c_ = divmod(i - 1, 10); x = L.W / 2 + 20 + (c_ - 4.5) * 98; y = (430 if N <= 10 else 390 + r_ * 150)
            else:
                r_, c_ = divmod(i - 1, 4); x = L.W / 2 + (c_ - 1.5) * 220; y = 560 + r_ * 150
            numeral_disc(im, d, L, i, t - tt, word=False, cx=x, cy=y + math.sin(t * 4 + i) * 6, r=46 if not L.v else 62)
        if last:
            lt = max(tt for i, tt in b["rpops"] if i == last)
            outlined(d, (L.W / 2 + 20, L.num_c[1] - 10), WORDS[last].upper(), font(110 * elastic((t - lt) / 0.4) + 1), RAINBOW[(last - 1) % 10], sw=11)
        else:
            banner(d, L, "¡A CONTAR!", bt, y=L.num_c[1] - 10, size=120, col=COL["yellow"])
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "odd":  # ¿cuál es diferente?: ("scene", "odd", [(objeto, color|None, escala)...], idx_distinto, "TEXTO", color) + qmark + reveal
        items, oi, lab, cn = b["args"][0], b["args"][1], b["args"][2], b["args"][3]
        n = len(items); rev = b["reveal"] is not None and t >= b["reveal"]
        if L.v:
            sz = 300; pos = [(L.W / 2 + (-200 if k % 2 == 0 else 200), 700 + (k // 2) * 330) for k in range(n)]
        else:
            sz = 240 if n <= 4 else 220; sp = 250 if n <= 4 else 205; pos = [(L.W / 2 + (20 if n <= 4 else -20) + (k - (n - 1) / 2) * sp, 470) for k in range(n)]
        for k, (ok, oc, osc) in enumerate(items):
            x, y = pos[k]; y += math.sin(t * 3 + k) * 7; tt = bt - 0.2 - k * 0.18
            if tt < 0: continue
            sc = elastic(tt / 0.45) * osc; al = 1.0; rot = math.sin(t * 2 + k) * 4
            if rev:
                rt = t - b["reveal"]
                if k == oi:
                    rr = sz * 0.6 + 6 * math.sin(t * 6)
                    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, 235), outline=COL["yellow"], width=14)
                    sc *= 1.12 + 0.07 * math.sin(rt * 7)
                    if rt < 1.2:
                        for j in range(10):
                            a = j * 36 + rt * 90; r2 = sz * 0.55 + rt * 230
                            d.polygon(star_pts(x + r2 * math.cos(math.radians(a)), y + r2 * math.sin(math.radians(a)), 22 * (1.2 - rt), 9 * (1.2 - rt)), fill=RAINBOW[j])
                else: al = 0.35
            col = tuple(oc) if oc else None
            paste_c(im, sprite(ok, sz, col), x, y, sc, rot, alpha=al)
        if rev: banner(d, L, lab, t - b["reveal"], y=L.num_c[1] if L.v else L.num_c[1] - 10, size=(110 if len(lab) <= 12 else 90) if L.v else 100, col=COL[cn])
        elif bt > 0.5:
            yy = L.num_c[1] + math.sin(t * 5) * 6
            if L.v:
                if q_on(b, t): qmark(d, L, t)   # el título del Short ya dice "¿CUÁL ES DIFERENTE?"
            else: outlined(d, (L.W / 2 + 30, yy - 10), "¿CUÁL ES DIFERENTE?", font(84), COL["yellow"], sw=10)
    elif kind == "paint":  # color nuevo: ("scene", "paint", "M_red", "ROJO", "red") + qmark + reveal (nombre)
        mk, lab, cn = b["args"][0], b["args"][1], b["args"][2]
        cx = (L.stage[0] + L.stage[2]) / 2; cy = (L.stage[1] + L.stage[3]) / 2 + (50 if not L.v else 80)
        sz = 470 if not L.v else 640; tc = COL[cn] if cn in COL else (255, 255, 255)
        if bt < 0.55:   # gotas que caen antes del ¡splash!
            for k in range(3):
                yy = cy - 520 + (bt / 0.55) ** 2 * 520 + k * 60; rr = 30 - k * 7
                d.ellipse([cx - rr, yy - rr * 1.3, cx + rr, yy + rr], fill=tc)
        else:
            st = bt - 0.55
            paste_c(im, sprite(mk, sz), cx, cy + math.sin(t * 2.5) * 6, elastic(st / 0.5) * (1 + 0.04 * math.sin(t * 3.5)), math.sin(t * 2) * 3)
            if st < 0.8:
                for k in range(12):
                    a = math.radians(k * 30 + 10); rr = sz * 0.35 + st * 420; s2 = 22 * (1 - st / 0.8)
                    x, y = cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.8
                    d.ellipse([x - s2, y - s2, x + s2, y + s2], fill=tc)
        if q_on(b, t): qmark(d, L, t)
        elif b["reveal"] is not None and t >= b["reveal"]:
            banner(d, L, lab, t - b["reveal"], size=140, col=tc)
    elif kind == "colorw":  # cosas de un color: ("scene", "colorw", "ROJO", "red", [(objeto, color|None, "NOMBRE")...]) + pop i
        lab, cn, items = b["args"][0], b["args"][1], b["args"][2]; n = len(items); tc = COL[cn]
        size = 270 if not L.v else 300
        box = (L.stage[0] + 20, L.stage[1] + 70, L.stage[2] - 20, L.stage[3] - 10) if not L.v else (L.stage[0], L.stage[1] + 40, L.stage[2], L.stage[3] + 120)
        pos = grid_positions(n, box, size)
        outlined(d, (L.W / 2 + 20, L.num_c[1] - 10), lab, font(110 * elastic(bt / 0.6) + 1), tc, sw=11)
        shown = dict(b["pops"]); mk = "M_" + cn
        for i, (x, y) in enumerate(pos, 1):
            ok, oc, nm = items[i - 1]
            if i in shown and t >= shown[i]:
                tt = t - shown[i]; wob = math.sin(t * 2.5 + i) * 5
                paste_c(im, sprite(ok, size, tuple(oc) if oc else None), x, y + wob, elastic(tt / 0.45), math.sin(t * 2 + i) * 3)
                if tt > 0.3: outlined(d, (x, y + size * 0.58), nm, font(44 if len(nm) <= 9 else 36), (255, 255, 255), sw=7)
            elif bt > 0.5:
                paste_c(im, sprite(mk, int(size * 0.5)), x, y, 1.0, 0, alpha=0.35)
    elif kind == "mix":  # mezcla: ("scene", "mix", cA, cB, cR, "NARANJA") + sa + sb + qmark + reveal
        ca, cb, cr, lab = b["args"][0], b["args"][1], b["args"][2], b["args"][3]
        cy = (L.stage[1] + L.stage[3]) / 2 + (60 if not L.v else 0); sz = 250 if not L.v else 300
        if not L.v: xa, xp, xb, xe, xr = 600, 775, 950, 1110, 1280
        else: xa, xp, xb, xe, xr = 300, 540, 780, 540, 540
        ya = yb = cy; yr = cy if not L.v else cy + 420; ye = cy if not L.v else cy + 210
        outlined(d, (L.W / 2 + 20, L.num_c[1] - 10), "¡MAGIA DE COLORES!", font(90 if not L.v else 70), COL["purple"], sw=10)
        rev = b["reveal"] is not None and t >= b["reveal"]
        for key, x, y, cn in (("sa", xa, ya, ca), ("sb", xb, yb, cb)):
            if b[key] is not None and t >= b[key]:
                tt = t - b[key]
                if True:
                    paste_c(im, sprite("M_" + cn, sz), x, y + math.sin(t * 3 + x) * 6, elastic(tt / 0.5), math.sin(t * 2 + x) * 4)
        if b["sb"] is not None and t >= b["sb"]:
            outlined(d, (xp, ye if L.v else cy), "+", font(130), (255, 255, 255), sw=10)
            outlined(d, (xe, ye if not L.v else ye), "=", font(130), (255, 255, 255), sw=10)
            if not rev:
                h = sz * 0.36
                d.rounded_rectangle([xr - h, yr - h, xr + h, yr + h], radius=int(h * 0.3), fill=(215, 215, 228), outline=(255, 255, 255), width=8)
                outlined(d, (xr, yr + math.sin(t * 6) * 6), "?", font(h * 1.4), (255, 255, 255), sw=6)
        if rev:
            rt = t - b["reveal"]
            if rt > 0.4:
                paste_c(im, sprite("M_" + cr, int(sz * 1.15)), xr, yr + math.sin(t * 3) * 6, elastic((rt - 0.4) / 0.5))
                if rt < 1.6:
                    for k in range(10):
                        a = k * 36 + rt * 90; r2 = sz * 0.5 + (rt - 0.4) * 230
                        d.polygon(star_pts(xr + r2 * math.cos(math.radians(a)), yr + r2 * math.sin(math.radians(a)), 22 * (1.6 - rt), 9 * (1.6 - rt)), fill=RAINBOW[k])
                if not L.v: outlined(d, (xr, yr + sz * 0.72), lab, font(64 * elastic((rt - 0.5) / 0.5) + 1), COL[cr], sw=9)
                else: banner(d, L, lab, rt - 0.5, y=yr + sz * 0.8, size=90, col=COL[cr])
    elif kind == "rainbow":  # arcoíris por bandas: ("scene", "rainbow", [(color, "NOMBRE")...]) + rpop i + confetti
        items = b["args"][0]; n = len(items)
        cx = L.W / 2 + 110 if not L.v else L.W / 2; cy = L.H * (0.72 if not L.v else 0.62); R0 = 380 if not L.v else 450; bw = 46 if not L.v else 52
        last = None
        for i, tt in b["rpops"]:
            if t < tt: continue
            last = (i, tt); cn = items[i - 1][0]; R = R0 - (i - 1) * bw; p = ease((t - tt) / 0.7)
            d.arc([cx - R, cy - R, cx + R, cy + R], 180, 180 + 180 * p, fill=COL[cn], width=bw + 2)
        if last and last[0] == n and t - last[1] > 0.7:
            for sx in (-1, 1):
                x = cx + sx * (R0 - n * bw / 2); y = cy + 10
                for (dx, dy, rr) in ((-70, 0, 70), (0, -35, 85), (70, 0, 70), (0, 25, 70)):
                    d.ellipse([x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr], fill=(250, 250, 255))
        if last:
            i, tt = last; cn, nm = items[i - 1]
            outlined(d, (L.W / 2 + 20, L.num_c[1] - 10), nm, font(120 * elastic((t - tt) / 0.4) + 1), COL[cn], sw=11)
        else:
            banner(d, L, "¡EL ARCOÍRIS!", bt, y=L.num_c[1] - 10, size=120, col=COL["yellow"])
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "opp":  # opuestos: ("scene", "opp", clave, "A", "B", colorA, colorB) + sa (nombre A) + qmark + sb (aparece B)
        key, la, lb, ca, cb = b["args"][:5]
        P = 400 if not L.v else 430
        if not L.v: (xa, ya), (xb, yb) = (780, 440), (1250, 440)
        else: (xa, ya), (xb, yb) = (540, 760), (540, 1290)
        opp_card(im, d, opp_panel(key, "A", t, P), xa, ya + math.sin(t * 2) * 4, P, elastic(bt / 0.6))
        sbt = b["sb"]
        if sbt is not None and t >= sbt:
            rt = t - sbt
            opp_card(im, d, opp_panel(key, "B", t, P), xb, yb + math.sin(t * 2 + 1) * 4, P, 0.85 + 0.15 * elastic(rt / 0.5))
            sparkle(d, xb, yb, rt, P * 0.45)
            outlined(d, (xb, yb + P / 2 + 52), lb, font((66 if len(lb) <= 7 else 58) * elastic((rt - 0.2) / 0.5) + 1), COL[cb], sw=9)
            if not L.v and rt > 0.4: two_arrow(d, (xa + xb) / 2, ya, 92 * elastic((rt - 0.4) / 0.5) + 1, COL["yellow"])
            if rt > 0.9: banner(d, L, f"{la} Y {lb}", rt - 0.9, y=L.num_c[1] - 10, size=96 if len(la + lb) <= 13 else 80, col=(255, 255, 255))
        elif b["sa"] is not None and t >= b["sa"] + 0.6:
            opp_q_card(d, xb, yb, P, elastic((t - b["sa"] - 0.6) / 0.5), t)
        if b["sa"] is not None and t >= b["sa"]:
            outlined(d, (xa, ya + P / 2 + 52), la, font((66 if len(la) <= 7 else 58) * elastic((t - b["sa"]) / 0.5) + 1), COL[ca], sw=9)
        if q_on(b, t): qmark(d, L, t)
    elif kind == "opp1":  # ¿cómo está?: ("scene", "opp1", clave, "A"|"B", "¡TEXTO!", color, "¿PREGUNTA?") + qmark + reveal
        key, side, lab, cn, hdr = b["args"][:5]
        P = 470 if not L.v else 640
        cx = (L.stage[0] + L.stage[2]) / 2; cy = (L.stage[1] + L.stage[3]) / 2 + (40 if not L.v else 90)
        rev = b["reveal"] is not None and t >= b["reveal"]
        sc = elastic(bt / 0.6) * (1 + (0.05 * math.sin(t * 5) * math.exp(-(t - b["reveal"]) * 0.5) if rev else 0))
        opp_card(im, d, opp_panel(key, side, t, P), cx, cy + math.sin(t * 2) * 4, P, sc, glow=rev)
        if rev:
            rt = t - b["reveal"]; sparkle(d, cx, cy, rt, P * 0.5)
            banner(d, L, lab, rt, y=L.num_c[1] - 10, size=120 if len(lab) <= 9 else 100, col=COL[cn])
        elif bt > 0.4:
            outlined(d, (L.W / 2 + 20, L.num_c[1] - 10 + math.sin(t * 5) * 6), hdr, font(92 if not L.v else 72), COL["yellow"], sw=10)
    elif kind == "cmd":  # juego con el cuerpo: ("scene", "cmd", [("¡ARRIBA!", color, "up"|"down"|None)...]) + rpop i + confetti
        items = b["args"][0]; last = None
        for i, tt in b["rpops"]:
            if tt <= t: last = (i, tt)
        if last is None:
            banner(d, L, "¡MUÉVETE!", bt, y=L.H * 0.36, size=150, col=COL["pink"])
        else:
            i, tt = last; txt, cn, ic = items[i - 1]; rt = t - tt
            cy = L.H * (0.40 if not L.v else 0.36)
            if ic == "up": cy -= ease(rt / 0.8) * 90
            if ic == "down": cy += ease(rt / 0.8) * 110
            p = elastic(rt / 0.6); f = font((160 if not L.v else 130) * p + 1)
            outlined(d, (L.W / 2 - 10, cy + math.sin(t * 6) * 8), txt, f, COL[cn], sw=max(1, int(14 * p)))
            if ic in ("up", "down") and rt > 0.3:
                ax = L.W / 2 - 10; sgn = -1 if ic == "up" else 1; ay = cy + sgn * 170 + math.sin(t * 7) * 10 * sgn
                d.polygon([(ax, ay + sgn * 70), (ax - 70, ay), (ax - 28, ay), (ax - 28, ay - sgn * 60), (ax + 28, ay - sgn * 60), (ax + 28, ay), (ax + 70, ay)],
                          fill=COL[cn], outline=COL["dark"], width=6)
            for k, (tx, cn2, _) in enumerate(items):
                x = L.W / 2 + 20 + (k - (len(items) - 1) / 2) * 70; y = L.H * (0.08 if not L.v else 0.06)
                done = any(j == k + 1 and tj <= t for j, tj in b["rpops"])
                d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=COL[cn2] if done else (255, 255, 255, 150), outline=(255, 255, 255), width=4)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "oreview":  # repaso de opuestos: ("scene", "oreview", [(clave, "A", "B")...]) + rpop i (A) + pop i (B) + confetti
        items = b["args"][0]; last = None
        for i, tt in b["rpops"]:
            if tt <= t: last = (i, tt)
        if last is None:
            banner(d, L, "¡REPASO!", bt, y=L.H * 0.36, size=150, col=COL["yellow"])
        else:
            i, tt = last; key, la, lb = items[i - 1]; P = 360
            (xa, ya), (xb, yb) = ((720, 440), (1200, 440)) if not L.v else ((540, 760), (540, 1240))
            rt = t - tt
            opp_card(im, d, opp_panel(key, "A", t, P), xa, ya, P, elastic(rt / 0.5))
            outlined(d, (xa, ya + P / 2 + 48), la, font(60 * elastic((rt - 0.1) / 0.5) + 1), COL["yellow"], sw=9)
            pb = next((tj for j, tj in b["pops"] if j == i), None)
            if pb is not None and t >= pb:
                rb = t - pb
                opp_card(im, d, opp_panel(key, "B", t, P), xb, yb, P, elastic(rb / 0.5))
                outlined(d, (xb, yb + P / 2 + 48), lb, font(60 * elastic((rb - 0.1) / 0.5) + 1), COL["cyan"], sw=9)
                if not L.v: two_arrow(d, (xa + xb) / 2, ya, 90 * elastic(rb / 0.5) + 1, COL["yellow"])
            for k in range(len(items)):
                x = L.W / 2 + 20 + (k - (len(items) - 1) / 2) * 64; y = L.num_c[1] - 40
                d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=RAINBOW[k] if k < i else (255, 255, 255, 150), outline=(255, 255, 255), width=4)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "pairs":   # contar de 2 en 2: ("scene", "pairs", npares, objeto, multicolor) + pop k (par k) | popall + numeral + qmark
        npr, ok, multi = b["args"][0], b["args"][1], b["args"][2]
        rows = 1 if npr <= 3 else 2; cols = math.ceil(npr / rows)
        x0, y0, x1, y1 = (470, 230, 1450, 800) if not L.v else (60, 560, 1020, 1250)
        tw, th = (x1 - x0) / cols, (y1 - y0) / rows
        objl = ok if isinstance(ok, list) else None   # lista: un objeto por bandeja (p. ej. animales = un par de ojos)
        single = ok == "cereza" or objl is not None
        if npr == 1: tw = min(tw, 560); th = min(th, 420)
        sz = int(min(tw * (0.8 if single else 0.56), th * 0.7, 260 if single else 270))
        if b["popall"]: shown = {k: b["popall"] + 0.18 * (k - 1) for k in range(1, npr + 1)}
        else: shown = {k: tt for k, tt in b["pops"]}
        last = 0
        for k in range(1, npr + 1):
            r_, c_ = divmod(k - 1, cols); cnt = cols if r_ < rows - 1 else npr - cols * (rows - 1)
            cx = x0 + (cols - cnt) * tw / 2 + c_ * tw + tw / 2; cy = y0 + r_ * th + th / 2 + 10
            p = elastic((bt - 0.1 - 0.05 * k) / 0.5)
            if p > 0:   # bandejita del par
                w2, h2 = tw * 0.46 * p, min(th * 0.44, sz * 0.78) * p
                d.rounded_rectangle([cx - w2 + 5, cy - h2 + 8, cx + w2 + 5, cy + h2 + 8], radius=int(24 * p) + 1, fill=(70, 130, 70))
                d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], radius=int(24 * p) + 1, fill=(255, 250, 232), outline=COL["dark"], width=5)
            col = RAINBOW[(k - 1) % 10] if multi else None
            spr = sprite(objl[k - 1] if objl else ok, sz, col)
            xs = [cx] if single else [cx - sz * 0.42, cx + sz * 0.42]
            if k not in shown or t < shown[k]:
                if not b["popall"] and bt > 0.7 and p > 0.95:
                    for j, x in enumerate(xs): paste_c(im, spr, x, cy, 0.85, 0, alpha=0.3)
                continue
            tt = t - shown[k]; last = max(last, k)
            for j, x in enumerate(xs):
                sc = elastic((tt - 0.12 * j) / 0.45)
                paste_c(im, spr, x, cy + math.sin(t * 2.6 + k + j) * 4, sc, math.sin(t * 2 + k + j) * 5 * (1 if j else -1))
            if tt < 0.9 and not b["popall"]:
                for j in range(8):
                    a = math.radians(j * 45 + tt * 120); rr = sz * 0.5 + tt * sz * 1.1
                    d.polygon(star_pts(cx + rr * math.cos(a), cy + rr * math.sin(a), 15 * (1 - tt) + 1, 6 * (1 - tt) + 1), fill=RAINBOW[j])
            if not b["popall"] or (b["numeral"] and t >= b["numeral"][1]):
                badge(d, cx + tw * 0.40, cy - min(th * 0.44, sz * 0.78) + 6, str(2 * k), r=int(36 * min(1, elastic(tt / 0.45))) + 1, col=COL["yellow"])
        if q_on(b, t): qmark(d, L, t)
        if b["numeral"] and t >= b["numeral"][1]:
            nt = t - b["numeral"][1]; nn = b["numeral"][0]
            numeral_disc(im, d, L, nn, nt, word=False, cx=L.num_c[0] - 150, r=95)
            if nt > 0.25: outlined(d, (L.num_c[0] - 30, L.num_c[1] + 4), WORDS[nn].upper(), font(90 * elastic((nt - 0.25) / 0.4) + 1), RAINBOW[(nn - 1) % 10], sw=10, anchor="lm")
        elif last and not b["popall"]:
            lt = shown[last]
            outlined(d, (L.num_c[0], L.num_c[1] - 10), str(2 * last), font(130 * elastic((t - lt) / 0.4) + 1), RAINBOW[(last - 1) % 10], sw=12)
    elif kind == "hop":   # la rana salta de 2 en 2: ("scene", "hop", N) + rpop v (cae en v) + confetti
        N = b["args"][0]
        per = 10 if not L.v else 5; rows = math.ceil(N / per)
        def spot(v):
            if v == 0: return ((500, 470 if N <= 10 else 380) if not L.v else (130, 640))
            r_, c_ = divmod(v - 1, per)
            if not L.v: return (610 + c_ * 92, (470 if N <= 10 else 380 + r_ * 230))
            return (230 + c_ * 170, 640 + r_ * 200)
        # río
        for r_ in range(rows):
            y = spot(1 + r_ * per)[1]
            d.rounded_rectangle([spot(0)[0] - 70 if r_ == 0 else spot(1)[0] - 70, y - 48, spot(min(N, (r_ + 1) * per))[0] + 70, y + 58], radius=50, fill=(90, 170, 240))
            for k in range(6):
                xx = spot(1 + r_ * per)[0] + ((t * 40 + k * 160) % (per * 92)) - 40
                d.arc([xx - 30, y + 14, xx + 30, y + 40], 200, 340, fill=(200, 235, 255), width=5)
        landed = [(v, tt) for v, tt in b["rpops"] if tt <= t]
        lv = {v: tt for v, tt in landed}
        sx_, sy_ = spot(0); d.ellipse([sx_ - 52, sy_ - 22, sx_ + 52, sy_ + 34], fill=(150, 100, 60)); outlined(d, (sx_, sy_ + 4), "0", font(40), (255, 255, 255), sw=5)
        for v in range(1, N + 1):
            x, y = spot(v); even = v % 2 == 0
            on = v in lv
            rr = (44 if even else 36) * (1 + (0.15 * elastic((t - lv[v]) / 0.5) if on else 0))
            fill = RAINBOW[(v // 2 - 1) % 10] if (on and even) else ((120, 200, 100) if even else (150, 205, 135))
            d.ellipse([x - rr, y - rr * 0.62, x + rr, y + rr * 0.62], fill=fill, outline=(60, 120, 60), width=4)
            outlined(d, (x, y + 2), str(v), font(int(rr * (0.95 if even else 0.7))), (255, 255, 255) if even else (235, 245, 230), sw=5 if even else 3)
        # rana
        fr = 150 if not L.v else 170
        if landed:
            v, tt = landed[-1]; prev = landed[-2][0] if len(landed) > 1 else 0
            if v - prev > 2 or v < prev: prev = max(0, v - 2)
            jt = clamp((t - tt + 0.42) / 0.42)   # el salto termina al decir el número
            (ax, ay), (bx, by) = spot(prev), spot(v)
            fx = ax + (bx - ax) * jt; fy = ay + (by - ay) * jt - math.sin(math.pi * jt) * 150 - 55
            sq = 1 + 0.12 * math.sin(math.pi * jt)
        else:
            fx, fy = spot(0); fy -= 55 + abs(math.sin(t * 3)) * 12; sq = 1
        # el salto empieza un poco antes del evento: mira el próximo rpop
        nxt = [(v, tt) for v, tt in b["rpops"] if tt > t]
        if nxt and nxt[0][1] - t < 0.42:
            v, tt = nxt[0]; prev = landed[-1][0] if landed else 0
            if v - prev > 2 or v < prev: prev = max(0, v - 2)
            jt = clamp(1 - (tt - t) / 0.42); sq = 1 + 0.12 * math.sin(math.pi * jt)
            (ax, ay), (bx, by) = spot(prev), spot(v)
            fx = ax + (bx - ax) * jt; fy = ay + (by - ay) * jt - math.sin(math.pi * jt) * 150 - 55
        paste_c(im, sprite("rana", fr), fx, fy, sq)
        if landed:
            v, tt = landed[-1]
            if v % 2 == 0:
                outlined(d, (L.num_c[0], L.num_c[1] - 10), WORDS[v].upper(), font(110 * elastic((t - tt) / 0.4) + 1), RAINBOW[(v // 2 - 1) % 10], sw=11)
        else:
            banner(d, L, "¡DE 2 EN 2!", bt, y=L.num_c[1] - 10, size=120, col=COL["yellow"])
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "match":   # ¿cuál es su pareja?: ("scene", "match", objeto, color, [colores], correcta, "TEXTO") + qmark + reveal
        ok, tc, opts, ci, lab = b["args"][:5]
        rev = b["reveal"] is not None and t >= b["reveal"]
        tx, ty = (680, 480) if not L.v else (540, 700)
        fr = 300 if not L.v else 340
        d.rounded_rectangle([tx - fr * 0.75 + 6, ty - fr * 0.62 + 9, tx + fr * 0.75 + 6, ty + fr * 0.62 + 9], radius=30, fill=(70, 130, 70))
        d.rounded_rectangle([tx - fr * 0.75, ty - fr * 0.62, tx + fr * 0.75, ty + fr * 0.62], radius=30, fill=(255, 250, 232), outline=COL["dark"], width=6)
        p0 = elastic((bt - 0.1) / 0.5)
        paste_c(im, sprite(ok, 210, COL[tc]), tx - fr * 0.33, ty + math.sin(t * 2.5) * 5, p0, -6)
        if not rev:
            d.rounded_rectangle([tx + fr * 0.33 - 85, ty - 100, tx + fr * 0.33 + 85, ty + 100], radius=26, outline=(190, 180, 160), width=6)
            outlined(d, (tx + fr * 0.33, ty + math.sin(t * 6) * 6), "?", font(140), COL["yellow"], sw=8)
        for k, oc in enumerate(opts):
            if not L.v: ox, oy = 1010 + k * 170, 480 + (k % 2) * 40
            else: ox, oy = 220 + k * 320, 1080
            tt = bt - 0.5 - k * 0.2
            if tt < 0: continue
            sc = elastic(tt / 0.45) * 0.8; al = 1.0
            if rev:
                rt = t - b["reveal"]
                if k == ci:
                    m = ease(rt / 0.7); ox = ox + (tx + fr * 0.33 - ox) * m; oy = oy + (ty - oy) * m; sc = 0.8 + 0.2 * m
                    if rt < 1.2:
                        for j in range(10):
                            a = math.radians(j * 36 + rt * 90); r2 = 120 + rt * 220
                            d.polygon(star_pts(ox + r2 * math.cos(a), oy + r2 * math.sin(a), 22 * (1.2 - rt), 9 * (1.2 - rt)), fill=RAINBOW[j])
                else: al = max(0.25, 1 - rt * 1.5)
            paste_c(im, sprite(ok, 210, COL[oc]), ox, oy + math.sin(t * 3 + k) * 6, sc, 6 if (rev and k == ci) else math.sin(t * 2 + k) * 6, alpha=al)
        if rev: banner(d, L, lab, t - b["reveal"], y=L.num_c[1] - 10, size=96 if len(lab) <= 16 else 80, col=COL[tc] if tc not in ("yellow",) else COL["orange"])
        elif bt > 0.5: outlined(d, (L.W / 2 + 30, L.num_c[1] - 10 + math.sin(t * 5) * 6), "¿CUÁL ES SU PAREJA?", font(84 if not L.v else 66), COL["yellow"], sw=10)
    elif kind == "seq":   # ¿qué sigue? (patrones): ("scene", "seq", [(objeto, color|None)...], idx_falta, "TEXTO", color) + qmark + reveal
        items, miss, lab, cn = b["args"][0], b["args"][1], b["args"][2], b["args"][3]; n = len(items)
        if L.v:   # vertical: filas de 3 para que el patrón se lea en renglones
            size = 260; xs = (L.W * 0.2, L.W * 0.5, L.W * 0.8)
            pos = [(xs[k % 3], 680 + (k // 3) * 310) for k in range(n)]
        else:
            sp = min(260, 1300 / n); size = int(min(230, sp * 0.88))
            pos = [(L.W / 2 + (k - (n - 1) / 2) * sp, (L.stage[1] + L.stage[3]) / 2 + 40) for k in range(n)]
        rev = b["reveal"] is not None and t >= b["reveal"]
        qt = next((tt for v, tt in b["q"] if v), None)
        for k, ((sk, col), (x, y)) in enumerate(zip(items, pos)):
            tt = bt - k * 0.22
            if tt < 0: continue
            bob = math.sin(t * 2.5 + k) * 5; sc = elastic(tt / 0.45)
            if qt is not None and not rev and k != miss:   # "leemos" el patrón: cada objeto salta en orden
                ph = (t - qt) - k * 0.5
                if 0 <= ph < 0.45: sc *= 1 + 0.18 * math.sin(ph / 0.45 * math.pi)
            if rev:   # ola de festejo al acertar
                ph = (t - b["reveal"]) - 0.6 - k * 0.18
                if 0 <= ph < 0.4: bob -= 30 * math.sin(ph / 0.4 * math.pi)
            if k == miss and not rev:
                h = size * 0.42 * elastic(tt / 0.6)
                d.rounded_rectangle([x - h, y - h, x + h, y + h], radius=int(h * 0.25) + 1, fill=(215, 215, 228), outline=(255, 255, 255), width=8)
                outlined(d, (x, y + math.sin(t * 6) * 6), "?", font(max(1, h * 1.4)), (255, 255, 255), sw=6)
            else:
                if k == miss:
                    sc = elastic((t - b["reveal"]) / 0.45); rr = size * 0.56
                    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 248, 210), outline=COL["yellow"], width=10)
                paste_c(im, sprite(sk, size, color=COL[col] if col else None), x, y + bob, sc)
        if q_on(b, t): qmark(d, L, t)
        elif rev: banner(d, L, lab, t - b["reveal"], size=130, col=COL[cn])
    elif kind == "week":   # la semana: ("scene", "week", hasta, falta|None, "TEXTO"|None, "names"|"count"|None) + rpop i + qmark + reveal + confetti
        upto, miss, hdr = b["args"][0], b["args"][1], b["args"][2]; mode = b["args"][3] if len(b["args"]) > 3 else None
        cw, ch_, gap = (232, 150, 16) if not L.v else (236, 170, 12)
        rows_y = (360, 560) if not L.v else (640, 850)
        def wpos(k):
            row = 0 if k < 4 else 1; n_in = 4 if row == 0 else 3; kk = k if row == 0 else k - 4
            return (L.W / 2 + (kk - (n_in - 1) / 2) * (cw + gap), rows_y[row])
        rp = {i: tt for i, tt in b["rpops"]}
        rev = b["reveal"] is not None and t >= b["reveal"]
        last = None
        for i, tt in b["rpops"]:
            if tt <= t: last = (i, tt)
        for k in range(upto):
            i = k + 1; x, y = wpos(k)
            if rp:
                if i not in rp or t < rp[i]: continue
                tt = t - rp[i]
            else: tt = bt - k * 0.16
            if tt < 0: continue
            sc = elastic(tt / 0.45); bob = math.sin(t * 2.5 + k) * 4
            hi = last is not None and last[0] == i and t - last[1] < 1.6
            if hi: sc *= 1 + 0.12 * math.sin(clamp((t - last[1]) / 0.5) * math.pi) + 0.06
            if rev and miss:   # ola de festejo
                ph = (t - b["reveal"]) - 0.5 - k * 0.12
                if 0 <= ph < 0.4: bob -= 24 * math.sin(ph / 0.4 * math.pi)
            name, cn = DAYS[k]; col = COL[cn]
            hw, hh = cw / 2 * sc, ch_ / 2 * sc
            if hw < 2: continue
            hidden = (i == miss and not rev)
            if i == miss and rev:
                rt = t - b["reveal"]; s2 = elastic(rt / 0.45); hw, hh = cw / 2 * s2, ch_ / 2 * s2
                if rt < 1.2:
                    for j in range(10):
                        a = math.radians(j * 36 + rt * 90); r2 = 90 + rt * 200
                        d.polygon(star_pts(x + r2 * math.cos(a), y + r2 * math.sin(a), 20 * (1.2 - rt), 8 * (1.2 - rt)), fill=RAINBOW[j])
            yy = y + bob
            d.rounded_rectangle([x - hw + 6, yy - hh + 9, x + hw + 6, yy + hh + 9], radius=int(26 * min(1, hw / (cw / 2))) + 1, fill=(40, 40, 60, 90))
            if hidden:
                d.rounded_rectangle([x - hw, yy - hh, x + hw, yy + hh], radius=int(26 * sc) + 1, fill=(215, 215, 228), outline=(255, 255, 255), width=7)
                outlined(d, (x, yy + math.sin(t * 6) * 5), "?", font(max(1, 120 * sc)), (255, 255, 255), sw=6)
                continue
            d.rounded_rectangle([x - hw, yy - hh, x + hw, yy + hh], radius=int(26 * hw / (cw / 2)) + 1, fill=col, outline=(255, 255, 255), width=7)
            fs = fit_font(name, cw * 0.86, 52)
            f = font(max(1, fs.size * hw / (cw / 2)))
            outlined(d, (x, yy + 18 * hh / (ch_ / 2)), name, f, (255, 255, 255), sw=max(1, int(6 * hw / (cw / 2))))
            br = 25 * hw / (cw / 2)
            if br > 4:
                d.ellipse([x - br, yy - hh * 0.62 - br, x + br, yy - hh * 0.62 + br], fill=(255, 255, 255), outline=COL["dark"], width=3)
                d.text((x, yy - hh * 0.62 + 1), str(i), font=font(br * 1.3), fill=COL["dark"], anchor="mm")
        if q_on(b, t): qmark(d, L, t)
        elif rev and miss:
            nm, cn = DAYS[miss - 1]; banner(d, L, "¡" + nm + "!", t - b["reveal"], y=L.num_c[1] - 5, size=120, col=COL[cn])
        elif last is not None and mode == "names":
            nm, cn = DAYS[last[0] - 1]
            outlined(d, (L.W / 2, L.num_c[1] - 5), nm, font(130 * elastic((t - last[1]) / 0.4) + 1), COL[cn], sw=12)
        elif last is not None and mode == "count":
            outlined(d, (L.W / 2, L.num_c[1] - 5), str(last[0]), font(150 * elastic((t - last[1]) / 0.4) + 1), RAINBOW[last[0] - 1], sw=12)
        elif hdr and bt > 0.3:
            outlined(d, (L.W / 2, L.num_c[1] - 5 + math.sin(t * 5) * 6), hdr, fit_font(hdr, L.W - 160, 96 if not L.v else 72), COL["yellow"], sw=10)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "day":   # un día: ("scene", "day", i, [sprites (o (sprite, color))], esconder) + pop k (actividad k) + qmark + reveal + confetti
        i, objs, hide = b["args"][0], b["args"][1], (b["args"][2] if len(b["args"]) > 2 else False)
        name, cn = DAYS[i - 1]; col = COL[cn]
        rev = b["reveal"] is not None and t >= b["reveal"]
        shown = (not hide) or rev
        if not L.v: calc, csz = (720, 470), 380
        else: calc, csz = (540, 720), 420
        p0 = elastic(bt / 0.55)
        if shown:
            st = 0 if not hide else t - b["reveal"]
            sc = p0 if not hide else (0.85 + 0.15 * elastic(st / 0.5))
            paste_c(im, sprite(f"cal_{i}", csz), calc[0], calc[1] + math.sin(t * 2) * 5, sc, math.sin(t * 1.5) * 3)
            if hide and st < 1.2:
                for j in range(10):
                    a = math.radians(j * 36 + st * 90); r2 = 170 + st * 240
                    d.polygon(star_pts(calc[0] + r2 * math.cos(a), calc[1] + r2 * math.sin(a), 24 * (1.2 - st), 9 * (1.2 - st)), fill=RAINBOW[j])
        else:
            paste_c(im, sprite("cal_0", csz), calc[0], calc[1] + math.sin(t * 2) * 5, p0, math.sin(t * 1.5) * 3)
        pops = {k: tt for k, tt in b["pops"]}
        for k, o in enumerate(objs, 1):
            ok, oc = (o if isinstance(o, (list, tuple)) else (o, None))
            if not L.v:
                x = 1170 if len(objs) == 1 else 1060 + (k - 1) * 230; y = 470 + (k - 1) * 40; sz = 320 if len(objs) == 1 else 250
            else:
                x = 540 + (k - (len(objs) + 1) / 2) * 300; y = 1090; sz = 280
            if hide: tt = bt - 0.3 - k * 0.2
            elif k in pops: tt = t - pops[k]
            else: continue
            if tt < 0: continue
            paste_c(im, sprite(ok, sz, COL[oc] if oc else None), x, y + math.sin(t * 2.6 + k) * 8, elastic(tt / 0.45), math.sin(t * 2 + k) * 6)
        # fila de la semana (bolitas) para ubicar el día
        if not L.v:
            for k in range(7):
                x = 960 + (k - 3) * 70; y = 760; cur = (k + 1 == i) and shown
                rr = 30 + (4 * math.sin(t * 5) if cur else 0) if cur else 18
                c2 = COL[DAYS[k][1]] if (k + 1 <= i and shown) or (not hide and k + 1 <= i) else (225, 225, 235)
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c2, outline=(255, 255, 255), width=5)
                if cur: d.text((x, y + 1), str(i), font=font(rr * 1.2), fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=COL["dark"])
        if q_on(b, t): qmark(d, L, t)
        elif shown:
            st = bt if not hide else t - b["reveal"]
            banner(d, L, ("¡" + name + "!") if hide else name, st, y=L.num_c[1] - 5, size=130, col=col)
        elif bt > 0.3:
            outlined(d, (L.W / 2, L.num_c[1] - 5 + math.sin(t * 5) * 6), "¿QUÉ DÍA ES?", font(96 if not L.v else 72), COL["yellow"], sw=10)
        if b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
    elif kind == "bye":
        banner(d, L, "¡ADIÓS!", bt, size=160, col=COL["orange"])
    if kind in ("card", "size", "bye", "animal", "fruit", "bowl", "word", "letter", "shape", "spattern", "teens", "odd", "paint", "colorw", "mix") and b["confetti"] and t >= b["confetti"]: confetti(d, L, t - b["confetti"])
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
