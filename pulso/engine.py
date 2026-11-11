"""Motor de motion graphics (PIL + numpy) para video 16:9 y Shorts 9:16."""
import math, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FD = "/usr/share/fonts/opentype/inter/"
FONTS = {"black": "InterDisplay-Black.otf", "xb": "InterDisplay-ExtraBold.otf", "b": "InterDisplay-Bold.otf",
         "sb": "Inter-SemiBold.otf", "m": "Inter-Medium.otf", "r": "Inter-Regular.otf"}
_fc = {}
def font(w, size):
    k = (w, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + FONTS[w], int(size))
    return _fc[k]

C = dict(bg1=(8, 12, 26), bg2=(22, 28, 56), text=(255, 255, 255), muted=(158, 168, 198),
         accent=(255, 199, 56), red=(255, 92, 96), teal=(56, 214, 176), blue=(92, 140, 255),
         card=(26, 33, 64), card2=(40, 49, 88), line=(60, 70, 110), dark=(5, 8, 18))

# Paleta de otro canal sin tocar el código: TEMA='{"accent": [80, 220, 255]}' python3 render.py ...
import os as _os, json as _json
if _os.environ.get("TEMA"):
    C.update({k: tuple(v) for k, v in _json.loads(_os.environ["TEMA"]).items()})

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def rgba(c, a=255): return (c[0], c[1], c[2], int(clamp(a / 255) * 255))

def fmt_num(v, dec=0):
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# ---------- texto ----------
def tokens(text):
    """'*varias palabras*' = color acento (admite tramos de varias palabras)."""
    out, cur = [], None
    for w in text.split():
        m = re.match(r'^([¿¡"«(=]*)(\*?)(.*?)(\*?)([.,:;?!")»…]*)$', w)
        pre, o, core, c, post = m.groups()
        if o: cur = "accent"
        out.append((pre + core + post, cur))
        if c: cur = None
    return out

def wrap_tokens(toks, f, maxw):
    lines, cur, cw = [], [], 0
    sp = f.getlength(" ")
    for w, c in toks:
        wl = f.getlength(w)
        if cur and cw + sp + wl > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, c, wl)); cw += (sp if len(cur) > 1 else 0) + wl
    if cur: lines.append(cur)
    return lines

def text_block_size(lines, f, lh):
    sp = f.getlength(" ")
    w = max(sum(t[2] for t in ln) + sp * (len(ln) - 1) for ln in lines)
    return w, lh * len(lines)

def draw_rich(d, lines, f, x, y, lh, align="center", base=C["text"], alpha=255, reveal=None, total_words=None):
    """reveal: 0..1 progreso de aparición palabra por palabra."""
    sp = f.getlength(" ")
    n = sum(len(l) for l in lines); idx = 0
    for li, ln in enumerate(lines):
        lw = sum(t[2] for t in ln) + sp * (len(ln) - 1)
        cx = x - lw / 2 if align == "center" else x
        for w, col, wl in ln:
            a = alpha
            if reveal is not None:
                p = clamp(reveal * (n + 2) - idx)
                a = alpha * ease(p)
            colr = C[col] if col else base
            if a > 3:
                d.text((cx, y + li * lh), w, font=f, fill=rgba(colr, a))
            cx += wl + sp; idx += 1

def fit(w, size, text, maxw):
    f = font(w, size)
    while f.getlength(text) > maxw and size > 20:
        size *= 0.92; f = font(w, size)
    return f

# ---------- capas ----------
class Layer:
    def __init__(self, W, H):
        self.im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)

def apply_alpha(im, a):
    if a >= 0.999: return im
    r, g, b, al = im.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))

def rrect(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle([int(v) for v in box], radius=int(r), fill=fill, outline=outline, width=width)

def pill(d, cx, y, text, s, color="accent", align="center"):
    f = font("b", 30 * s); tw = f.getlength(text)
    pw, ph = tw + 44 * s, 54 * s
    x0 = cx - pw / 2 if align == "center" else cx
    rrect(d, (x0, y, x0 + pw, y + ph), ph / 2, rgba(C["card2"]))
    d.text((x0 + 22 * s, y + ph / 2), text, font=f, fill=rgba(C[color]), anchor="lm")
    return ph

# ---------- fondo ----------
class Background:
    def __init__(self, W, H, seed=3):
        self.W, self.H = W, H
        PW, PH = W + 240, H + 240
        y = np.linspace(0, 1, PH)[:, None]; x = np.linspace(0, 1, PW)[None, :]
        g = (1 - y) * 0.35 + x * 0.25
        base = np.zeros((PH, PW, 3), np.float32)
        for i in range(3):
            base[..., i] = C["bg1"][i] + (C["bg2"][i] - C["bg1"][i]) * g
        rng = np.random.default_rng(seed)
        blobs = Image.new("RGB", (PW // 4, PH // 4), (0, 0, 0)); bd = ImageDraw.Draw(blobs)
        for col, n in ((C["blue"], 3), ((140, 80, 220), 2), (C["accent"], 1)):
            for _ in range(n):
                cx, cy = rng.uniform(0, PW // 4), rng.uniform(0, PH // 4); r = rng.uniform(40, 110)
                bd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c * 0.22) for c in col))
        blobs = blobs.filter(ImageFilter.GaussianBlur(45)).resize((PW, PH), Image.BILINEAR)
        base += np.asarray(blobs, np.float32)
        # viñeta
        yy, xx = np.mgrid[0:PH, 0:PW]
        v = ((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2
        base *= (1 - 0.35 * np.clip(v, 0, 1.4))[..., None]
        self.base = np.clip(base, 0, 255).astype(np.uint8)
        # grilla
        step = 90
        grid = Image.new("RGBA", (W + step, H + step), (0, 0, 0, 0)); gd = ImageDraw.Draw(grid)
        for gx in range(0, W + step, step): gd.line([(gx, 0), (gx, H + step)], fill=(255, 255, 255, 9))
        for gy in range(0, H + step, step): gd.line([(0, gy), (W + step, gy)], fill=(255, 255, 255, 9))
        self.grid, self.step = grid, step

    def frame(self, t):
        ox = int(120 + 100 * math.sin(t * 0.045)); oy = int(120 + 90 * math.cos(t * 0.037))
        im = Image.fromarray(self.base[oy:oy + self.H, ox:ox + self.W]).convert("RGBA")
        g = int(t * 10) % self.step
        im.alpha_composite(self.grid.crop((g, g, g + self.W, g + self.H)))
        return im

# ---------- iconos ----------
def icon(d, kind, cx, cy, r, col=None, a=255):
    col = rgba(C[col or "accent"], a); white = rgba(C["text"], a); dark = rgba(C["dark"], a)
    if kind == "robot":
        rrect(d, (cx - r, cy - r * 0.75, cx + r, cy + r * 0.85), r * 0.35, col)
        d.line([(cx, cy - r * 0.75), (cx, cy - r * 1.15)], fill=col, width=int(r * 0.09))
        d.ellipse([cx - r * 0.13, cy - r * 1.3, cx + r * 0.13, cy - r * 1.04], fill=col)
        for ex in (-0.4, 0.4):
            d.ellipse([cx + ex * r - r * 0.17, cy - r * 0.2, cx + ex * r + r * 0.17, cy + r * 0.14], fill=dark)
        d.rounded_rectangle([cx - r * 0.35, cy + r * 0.38, cx + r * 0.35, cy + r * 0.5], radius=int(r * 0.06), fill=dark)
    elif kind == "human":
        d.ellipse([cx - r * 0.42, cy - r * 1.0, cx + r * 0.42, cy - r * 0.16], fill=col)
        d.pieslice([cx - r * 0.85, cy - r * 0.05, cx + r * 0.85, cy + r * 1.6], 180, 360, fill=col)
    elif kind == "warning":
        d.polygon([(cx, cy - r), (cx + r * 1.1, cy + r * 0.85), (cx - r * 1.1, cy + r * 0.85)], fill=col)
        d.rounded_rectangle([cx - r * 0.09, cy - r * 0.4, cx + r * 0.09, cy + r * 0.3], radius=int(r * 0.05), fill=dark)
        d.ellipse([cx - r * 0.1, cy + r * 0.45, cx + r * 0.1, cy + r * 0.65], fill=dark)
    elif kind == "check":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.line([(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)], fill=dark, width=int(r * 0.18), joint="curve")
    elif kind == "cross":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        for s_ in (1, -1):
            d.line([(cx - r * 0.4, cy - s_ * r * 0.4), (cx + r * 0.4, cy + s_ * r * 0.4)], fill=dark, width=int(r * 0.18))
    elif kind == "chat":
        rrect(d, (cx - r, cy - r * 0.75, cx + r, cy + r * 0.45), r * 0.3, col)
        d.polygon([(cx - r * 0.5, cy + r * 0.4), (cx - r * 0.75, cy + r * 0.85), (cx - r * 0.1, cy + r * 0.4)], fill=col)
        for ex in (-0.45, 0, 0.45):
            d.ellipse([cx + ex * r - r * 0.11, cy - r * 0.26, cx + ex * r + r * 0.11, cy - r * 0.04], fill=dark)
    elif kind == "money":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.text((cx, cy), "$", font=font("black", r * 1.3), fill=dark, anchor="mm")
    elif kind == "clock":
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        d.ellipse([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], fill=dark)
        d.line([(cx, cy), (cx, cy - r * 0.55)], fill=col, width=int(r * 0.12))
        d.line([(cx, cy), (cx + r * 0.4, cy + r * 0.15)], fill=col, width=int(r * 0.12))
    elif kind == "chart_down":
        pts = [(cx - r, cy - r * 0.6), (cx - r * 0.3, cy - r * 0.1), (cx + r * 0.1, cy - r * 0.35), (cx + r, cy + r * 0.7)]
        d.line(pts, fill=col, width=int(r * 0.16), joint="curve")
        d.polygon([(cx + r * 1.1, cy + r * 0.85), (cx + r * 0.55, cy + r * 0.75), (cx + r * 1.0, cy + r * 0.3)], fill=col)

    elif kind == "drop":
        pts = []
        for k in range(73):
            th = 2 * math.pi * k / 72
            pts.append((cx + r * 0.82 * math.sin(th) * math.sin(th / 2), cy - r * 1.05 * math.cos(th) * 1.0 + r * 0.1))
        d.polygon(pts, fill=col)
        d.ellipse([cx - r * 0.42, cy + r * 0.2, cx - r * 0.2, cy + r * 0.55], fill=rgba(C["text"], a * 0.6))
    elif kind == "vault":
        # cápsula tipo "bóveda": barril ovalado con costillas y tapas
        rrect(d, (cx - r * 1.25, cy - r * 0.62, cx + r * 1.25, cy + r * 0.62), r * 0.6, col)
        for k in range(-3, 4):
            x = cx + k * r * 0.3
            hh = r * 0.62 * math.sqrt(max(0.0, 1 - (k * 0.3 / 1.3) ** 2)) * 0.82
            d.line([(x, cy - hh), (x, cy + hh)], fill=dark, width=max(2, int(r * 0.05)))
        d.line([(cx - r * 1.1, cy), (cx + r * 1.1, cy)], fill=dark, width=max(2, int(r * 0.07)))
        for sx in (-1, 1):
            d.ellipse([cx + sx * r * 1.33 - r * 0.14, cy - r * 0.14, cx + sx * r * 1.33 + r * 0.14, cy + r * 0.14], fill=col)
    elif kind == "bolt":
        d.polygon([(cx + r * 0.25, cy - r * 1.1), (cx - r * 0.65, cy + r * 0.15), (cx - r * 0.02, cy + r * 0.15),
                   (cx - r * 0.3, cy + r * 1.1), (cx + r * 0.65, cy - r * 0.2), (cx + r * 0.02, cy - r * 0.2)], fill=col)
    elif kind == "search":
        # lupa
        d.ellipse([cx - r * 0.9, cy - r * 0.9, cx + r * 0.4, cy + r * 0.4], outline=col, width=max(3, int(r * 0.2)))
        d.line([(cx + r * 0.25, cy + r * 0.25), (cx + r * 0.95, cy + r * 0.95)], fill=col, width=max(4, int(r * 0.3)))
    elif kind == "code":
        # </> dentro de una ventana
        rrect(d, (cx - r * 1.1, cy - r * 0.8, cx + r * 1.1, cy + r * 0.8), r * 0.22, col)
        w_ = max(3, int(r * 0.14))
        d.line([(cx - r * 0.35, cy - r * 0.35), (cx - r * 0.7, cy), (cx - r * 0.35, cy + r * 0.35)], fill=dark, width=w_, joint="curve")
        d.line([(cx + r * 0.35, cy - r * 0.35), (cx + r * 0.7, cy), (cx + r * 0.35, cy + r * 0.35)], fill=dark, width=w_, joint="curve")
        d.line([(cx + r * 0.12, cy - r * 0.45), (cx - r * 0.12, cy + r * 0.45)], fill=dark, width=w_)

# ---------- escenas ----------
class Ctx:
    """Contexto geométrico: horizontal (W>H) o vertical."""
    def __init__(self, W, H):
        self.W, self.H = W, H; self.v = H > W
        self.s = 1.0 if not self.v else 1.05
        self.top = H * (0.10 if not self.v else 0.17)
        self.bot = H * (0.80 if not self.v else 0.66)
        self.cx = W / 2; self.maxw = W * (0.80 if not self.v else 0.86)
    @property
    def mid(self): return (self.top + self.bot) / 2

def entrance(t, delay=0.0, dur=0.55):
    p = ease((t - delay) / dur); return p, (1 - p)

def draw_scene(ctx, L, sc, t, dur):
    """Dibuja la escena sc en la capa L (RGBA) en el tiempo local t."""
    typ = sc["type"]; s = ctx.s; d = L.d; W, H = ctx.W, ctx.H
    fn = globals()["sc_" + typ]
    fn(ctx, L, sc, t, dur)

def group(ctx, L, t, delay, drawfn, dy=40, dur=0.5):
    p, _ = entrance(t, delay, dur)
    if p <= 0.001: return
    if p >= 0.999:
        drawfn(L.d, 0); return
    tmp = Layer(ctx.W, ctx.H); drawfn(tmp.d, int(dy * (1 - p)))
    L.im.alpha_composite(apply_alpha(tmp.im, p))

def sc_headline(ctx, L, sc, t, dur):
    s = ctx.s; size = sc.get("size", 96 if not ctx.v else 88) * s
    f = font("black", size); lh = size * 1.12
    lines = wrap_tokens(tokens(sc["text"]), f, ctx.maxw)
    _, th = text_block_size(lines, f, lh)
    sub = sc.get("sub"); fs = font("m", 42 * s); slines = wrap_tokens(tokens(sub), fs, ctx.maxw * 0.9) if sub else []
    kick = sc.get("kicker")
    total = th + (len(slines) * 56 * s + 30 * s if sub else 0) + (80 * s if kick else 0)
    y = ctx.mid - total / 2
    if sc.get("icon"):
        y += 70 * s
    if sc.get("icon"):
        ir = 70 * s
        group(ctx, L, t, 0, lambda dd, oy: icon(dd, sc["icon"], ctx.cx, y - ir * 1.3 + oy, ir, sc.get("icon_col")), dy=30)
    if kick:
        group(ctx, L, t, 0, lambda dd, oy: pill(dd, ctx.cx, y + oy, kick, s, sc.get("kick_col", "accent")), dy=20)
        y += 80 * s
    rev = clamp(t / max(0.5, min(1.4, dur * 0.35)))
    draw_rich(L.d, lines, f, ctx.cx, y, lh, reveal=rev)
    y += th + 30 * s
    if sub:
        a = 255 * ease((t - 0.6) / 0.5)
        draw_rich(L.d, slines, fs, ctx.cx, y, 56 * s, base=C["muted"], alpha=a)

def sc_number(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d
    size = sc.get("size", 230 if not ctx.v else 200) * s
    p = ease((t - 0.2) / 1.4)
    val = sc["value"] * p
    txt = sc.get("prefix", "") + fmt_num(val, sc.get("dec", 0)) + sc.get("suffix", "")
    fn = fit("black", size, sc.get("prefix", "") + fmt_num(sc["value"], sc.get("dec", 0)) + sc.get("suffix", ""), ctx.maxw)
    lab = sc.get("label", ""); fl = font("b", 52 * s); llines = wrap_tokens(tokens(lab), fl, ctx.maxw)
    kick = sc.get("kicker")
    total = size * 1.05 + 30 * s + len(llines) * 66 * s + (90 * s if kick else 0)
    y = ctx.mid - total / 2
    if kick:
        group(ctx, L, t, 0, lambda dd, oy: pill(dd, ctx.cx, y + oy, kick, s, sc.get("kick_col", "accent")), dy=20); y += 90 * s
    a = 255 * ease(t / 0.35)
    col = C[sc.get("color", "accent")]
    d.text((ctx.cx, y + size * 0.52), txt, font=fn, fill=rgba(col, a), anchor="mm")
    y += size * 1.05 + 30 * s
    draw_rich(d, llines, fl, ctx.cx, y, 66 * s, alpha=255 * ease((t - 0.5) / 0.5))

def sc_bars(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; items = sc["items"]; n = len(items)
    title = sc.get("title")
    y0 = ctx.top + (20 * s)
    if title:
        f = font("xb", 54 * s); tl = wrap_tokens(tokens(title), f, ctx.maxw)
        draw_rich(d, tl, f, ctx.cx, y0, 64 * s, alpha=255 * ease(t / 0.4)); y0 += len(tl) * 64 * s + 40 * s
    base_y = ctx.bot - 70 * s
    area_h = base_y - y0 - 80 * s
    bw = min(220 * s, ctx.maxw / (n * 1.6)); gap = bw * 0.6
    totw = n * bw + (n - 1) * gap; x = ctx.cx - totw / 2
    vmax = max(i[1] for i in items)
    d.line([(ctx.cx - totw / 2 - 40 * s, base_y), (ctx.cx + totw / 2 + 40 * s, base_y)], fill=rgba(C["line"], 255 * ease(t / 0.3)), width=int(3 * s))
    for i, it in enumerate(items):
        lab, v, col = it[0], it[1], it[2]; disp = it[3] if len(it) > 3 else fmt_num(v)
        p = ease((t - 0.3 - i * 0.35) / 0.9)
        h = max(2, area_h * (v / vmax) * p)
        bx = x + i * (bw + gap)
        if p > 0:
            rrect(d, (bx, base_y - h, bx + bw, base_y), 14 * s, rgba(C[col]))
            d.text((bx + bw / 2, base_y - h - 18 * s), disp, font=font("black", 50 * s), fill=rgba(C["text"], 255 * p), anchor="md")
        fl = font("sb", 34 * s)
        for li, ln in enumerate(wrap_tokens(tokens(lab), fl, bw + gap * 0.9)):
            txt = " ".join(w[0] for w in ln)
            d.text((bx + bw / 2, base_y + 20 * s + li * 42 * s), txt, font=fl, fill=rgba(C["muted"], 255 * ease((t - 0.2) / 0.4)), anchor="ma")

def sc_quote(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d
    f = font("xb", sc.get("size", 64 if not ctx.v else 62) * s); lh = f.size * 1.22
    lines = wrap_tokens(tokens(sc["text"]), f, ctx.maxw * 0.92)
    _, th = text_block_size(lines, f, lh)
    total = 150 * s + th + 90 * s
    y = ctx.mid - total / 2
    group(ctx, L, t, 0, lambda dd, oy: dd.text((ctx.cx, y + 120 * s + oy), "“", font=font("black", 260 * s), fill=rgba(C["accent"]), anchor="ms"), dy=30)
    y += 150 * s
    draw_rich(d, lines, f, ctx.cx, y, lh, reveal=clamp(t / max(0.8, dur * 0.45)))
    y += th + 40 * s
    a = 255 * ease((t - 0.8) / 0.5)
    fa = font("m", 34 * s)
    for li, ln in enumerate(wrap_tokens([(w, None) for w in ("— " + sc["author"]).split()], fa, ctx.maxw)):
        d.text((ctx.cx, y + li * 44 * s), " ".join(w[0] for w in ln), font=fa, fill=rgba(C["muted"], a), anchor="ma")

def sc_list(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; items = sc["items"]; n = len(items)
    title = sc.get("title"); y = ctx.top + 10 * s
    fi = font("b", sc.get("size", 50 if not ctx.v else 46) * s); rowh = fi.size * 1.25
    rows = [wrap_tokens(tokens(it), fi, ctx.maxw - 130 * s) for it in items]
    total = (80 * s if title else 0) + sum(len(r) * rowh + 34 * s for r in rows)
    y = max(ctx.top, ctx.mid - total / 2)
    if title:
        group(ctx, L, t, 0, lambda dd, oy: pill(dd, ctx.cx, y + oy, title, s), dy=20); y += 90 * s
    stagger = sc.get("stagger", min(0.9, max(0.35, (dur * 0.55) / max(1, n))))
    x0 = ctx.cx - ctx.maxw / 2 + (40 * s if not ctx.v else 0)
    hl = sc.get("highlight")
    for i, r in enumerate(rows):
        yy = y
        def dr(dd, oy, i=i, r=r, yy=yy):
            on = (hl is None) or (hl == i)
            col = C["accent"] if on else C["line"]
            dd.ellipse([x0, yy + oy + 4 * s, x0 + 70 * s, yy + oy + 74 * s], fill=rgba(col))
            dd.text((x0 + 35 * s, yy + oy + 39 * s), str(i + 1), font=font("black", 40 * s), fill=rgba(C["dark"]), anchor="mm")
            draw_rich(dd, r, fi, x0 + 100 * s, yy + oy + 8 * s, rowh, align="left", base=C["text"] if on else C["muted"])
        group(ctx, L, t, (sc['_delays'][i] if sc.get('_delays') else 0.2 + i * stagger), dr, dy=0)
        y += len(r) * rowh + 34 * s

def sc_chat(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; msgs = sc["msgs"]
    pw = (640 if not ctx.v else 820) * s; ph = (ctx.bot - ctx.top) * 0.98
    px = ctx.cx - pw / 2 if not sc.get("left") else ctx.W * 0.1; py = ctx.mid - ph / 2
    group(ctx, L, t, 0, lambda dd, oy: (rrect(dd, (px, py + oy, px + pw, py + ph + oy), 48 * s, rgba(C["card"]), outline=rgba(C["line"]), width=int(3 * s)),
                                         dd.text((px + pw / 2, py + 50 * s + oy), sc.get("title", "Asistente virtual"), font=font("b", 32 * s), fill=rgba(C["muted"]), anchor="mm")), dy=40)
    if t < 0.4: return
    y = py + 110 * s; fm = font("m", 34 * s)
    stagger = sc.get("stagger", min(1.6, max(0.8, (dur * 0.7) / len(msgs))))
    dl = sc.get("_delays")
    for i, (side, txt) in enumerate(msgs):
        tt = t - (dl[i] if dl else 0.5 + i * stagger)
        if tt < 0: break
        lines = wrap_tokens(tokens(txt), fm, pw * 0.62)
        bw = text_block_size(lines, fm, 44 * s)[0] + 48 * s; bh = len(lines) * 44 * s + 34 * s
        if side == "bot" and tt < 0.45:   # escribiendo...
            bx = px + 30 * s
            rrect(d, (bx, y, bx + 120 * s, y + 64 * s), 30 * s, rgba(C["card2"]))
            for k in range(3):
                ph_ = (math.sin(tt * 14 - k) + 1) / 2
                d.ellipse([bx + 26 * s + k * 26 * s, y + 24 * s, bx + 42 * s + k * 26 * s, y + 40 * s], fill=rgba(C["muted"], 120 + 135 * ph_))
            break
        a = ease(tt / 0.3)
        if side in ("bot", "human"):
            bx = px + 30 * s; colb = C["card2"] if side == "bot" else C["teal"]
        else:
            bx = px + pw - 30 * s - bw; colb = C["blue"]
        rrect(d, (bx, y, bx + bw, y + bh), 26 * s, rgba(colb, 255 * a))
        draw_rich(d, lines, fm, bx + 24 * s, y + 16 * s, 44 * s, align="left", alpha=255 * a,
                  base=C["dark"] if side == "human" else C["text"])
        y += bh + 22 * s

def sc_people(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; n = sc.get("n", 700)
    cols = sc.get("cols", 35 if not ctx.v else 20); rows = math.ceil(n / cols)
    label = sc.get("label"); fl = font("xb", 58 * s)
    ll = wrap_tokens(tokens(label), fl, ctx.maxw) if label else []
    avail_h = (ctx.bot - ctx.top) - (len(ll) * 70 * s + 40 * s)
    cell = min(ctx.maxw / cols, avail_h / rows)
    gw, gh = cols * cell, rows * cell
    x0 = ctx.cx - gw / 2; y0 = ctx.top + (avail_h - gh) / 2
    mode = sc.get("mode", "fill"); col = C[sc.get("color", "accent")]
    fill_t = sc.get("fill_time", 1.6)
    for i in range(n):
        r_, c_ = divmod(i, cols)
        p = ease((t * n / fill_t - i) / (n * 0.08))
        if p <= 0: continue
        cx = x0 + c_ * cell + cell / 2; cy = y0 + r_ * cell + cell / 2; rr = cell * 0.36 * (0.6 + 0.4 * p)
        if mode == "ghost" and t > sc.get("ghost_at", 1.8):
            q = ease((t - sc.get("ghost_at", 1.8) - (i % cols) * 0.01) / 0.6)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=rgba(col, 255 * p), width=max(1, int(cell * 0.08)),
                      fill=rgba(col, 255 * p * (1 - q)))
        else:
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=rgba(col, 255 * p))
    if ll:
        draw_rich(d, ll, fl, ctx.cx, y0 + gh + 40 * s, 70 * s, alpha=255 * ease((t - 0.8) / 0.5))

def sc_timeline(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; pts = sc["points"]; act = sc.get("active", len(pts) - 1); n = len(pts)
    title = sc.get("title")
    if not ctx.v:
        y = ctx.mid + 20 * s; x0, x1 = ctx.W * 0.12, ctx.W * 0.88
        p = ease(t / 1.0)
        d.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=rgba(C["line"]), width=int(6 * s))
        for i, (yr, lab) in enumerate(pts):
            x = x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0.5)
            q = ease((t - 0.2 - i * 0.25) / 0.4)
            if q <= 0: continue
            on = i == act; col = C["accent"] if on else C["muted"]; r = (26 if on else 16) * s
            d.ellipse([x - r, y - r, x + r, y + r], fill=rgba(col, 255 * q))
            d.text((x, y - 50 * s), yr, font=font("black", (58 if on else 44) * s), fill=rgba(col, 255 * q), anchor="ms")
            for li, ln in enumerate(wrap_tokens(tokens(lab), font("sb", 32 * s), (x1 - x0) / n * 0.95)):
                d.text((x, y + 50 * s + li * 40 * s), " ".join(w[0] for w in ln), font=font("sb", 32 * s), fill=rgba(C["text"] if on else C["muted"], 255 * q), anchor="ma")
    else:
        x = ctx.W * 0.2; y0, y1 = ctx.top + 40 * s, ctx.bot - 40 * s
        p = ease(t / 1.0)
        d.line([(x, y0), (x, y0 + (y1 - y0) * p)], fill=rgba(C["line"]), width=int(6 * s))
        for i, (yr, lab) in enumerate(pts):
            y = y0 + (y1 - y0) * (i / (n - 1) if n > 1 else 0.5)
            q = ease((t - 0.2 - i * 0.25) / 0.4)
            if q <= 0: continue
            on = i == act; col = C["accent"] if on else C["muted"]; r = (24 if on else 15) * s
            d.ellipse([x - r, y - r, x + r, y + r], fill=rgba(col, 255 * q))
            d.text((x + 50 * s, y - 8 * s), yr, font=font("black", (56 if on else 44) * s), fill=rgba(col, 255 * q), anchor="ls")
            d.text((x + 50 * s, y + 8 * s), lab, font=font("sb", 34 * s), fill=rgba(C["text"] if on else C["muted"], 255 * q), anchor="la")
    if title:
        f = font("xb", 54 * s)
        draw_rich(d, wrap_tokens(tokens(title), f, ctx.maxw), f, ctx.cx, ctx.top + 10 * s, 64 * s, alpha=255 * ease(t / 0.4))

def sc_stats(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; cards = sc["cards"]; n = len(cards)
    cols = 2 if not ctx.v else 1; rows = math.ceil(n / cols)
    gap = 30 * s
    cw = (ctx.maxw - gap * (cols - 1)) / cols
    title = sc.get("title")
    ch = min(250 * s, ((ctx.bot - ctx.top - (90 * s if title else 0)) - gap * (rows - 1)) / rows)
    y0 = ctx.mid - ((90 * s if title else 0) + rows * ch + gap * (rows - 1)) / 2
    if title:
        group(ctx, L, t, 0, lambda dd, oy: pill(dd, ctx.cx, y0 + oy, title, s), dy=20); y0 += 90 * s
    stagger = sc.get("stagger", min(1.5, max(0.5, dur * 0.6 / n)))
    for i, (val, lab, col) in enumerate(cards):
        r_, c_ = divmod(i, cols)
        x = ctx.cx - ctx.maxw / 2 + c_ * (cw + gap); y = y0 + r_ * (ch + gap)
        def dr(dd, oy, x=x, y=y, val=val, lab=lab, col=col):
            rrect(dd, (x, y + oy, x + cw, y + ch + oy), 30 * s, rgba(C["card"]), outline=rgba(C[col]), width=int(3 * s))
            dd.text((x + 40 * s, y + oy + ch * 0.42), val, font=fit("black", min(96 * s, ch * 0.42), val, cw - 80 * s), fill=rgba(C[col]), anchor="lm")
            fl = font("sb", 34 * s)
            for li, ln in enumerate(wrap_tokens(tokens(lab), fl, cw - 80 * s)[:2]):
                dd.text((x + 40 * s, y + oy + ch * 0.66 + li * 42 * s), " ".join(w[0] for w in ln), font=fl, fill=rgba(C["muted"]), anchor="la")
        group(ctx, L, t, (sc['_delays'][i] if sc.get('_delays') else 0.2 + i * stagger), dr, dy=30)

def sc_compare(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d; a, b = sc["left"], sc["right"]
    title = sc.get("title"); y = ctx.top + 10 * s
    if title:
        f = font("xb", 54 * s); tl = wrap_tokens(tokens(title), f, ctx.maxw)
        draw_rich(d, tl, f, ctx.cx, y, 64 * s, alpha=255 * ease(t / 0.4)); y += len(tl) * 64 * s + 40 * s
    if not ctx.v:
        cw = ctx.maxw * 0.4; ch = ctx.bot - y - 30 * s
        boxes = [(ctx.cx - ctx.maxw / 2, y), (ctx.cx + ctx.maxw / 2 - cw, y)]
    else:
        cw = ctx.maxw; ch = (ctx.bot - y - 120 * s) / 2
        boxes = [(ctx.cx - cw / 2, y), (ctx.cx - cw / 2, y + ch + 120 * s)]
    for i, (spec, (bx, by)) in enumerate(zip((a, b), boxes)):
        lab, val, col = spec
        def dr(dd, oy, bx=bx, by=by, lab=lab, val=val, col=col):
            rrect(dd, (bx, by + oy, bx + cw, by + ch + oy), 34 * s, rgba(C["card"]), outline=rgba(C[col]), width=int(4 * s))
            dd.text((bx + cw / 2, by + oy + ch * 0.45), val, font=fit("black", min(120 * s, ch * 0.4), val, cw - 70 * s), fill=rgba(C[col]), anchor="mm")
            fl = font("sb", 38 * s)
            for li, ln in enumerate(wrap_tokens(tokens(lab), fl, cw - 60 * s)[:2]):
                dd.text((bx + cw / 2, by + oy + ch * 0.68 + li * 46 * s), " ".join(w[0] for w in ln), font=fl, fill=rgba(C["muted"]), anchor="ma")
        group(ctx, L, t, 0.2 + i * sc.get("stagger", 0.9), dr, dy=30)
    p = ease((t - 0.2 - sc.get("stagger", 0.9) + 0.2) / 0.4)
    if p > 0:
        if not ctx.v:
            ay = y + ch / 2; ax = ctx.cx
            d.polygon([(ax - 40 * s, ay - 40 * s), (ax + 40 * s, ay), (ax - 40 * s, ay + 40 * s)], fill=rgba(C["accent"], 255 * p))
        else:
            ax = ctx.cx; ay = y + ch + 60 * s
            d.polygon([(ax - 40 * s, ay - 30 * s), (ax + 40 * s, ay - 30 * s), (ax, ay + 30 * s)], fill=rgba(C["accent"], 255 * p))

def sc_chapter(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d
    p = ease(t / 0.6)
    d.text((ctx.cx, ctx.mid - 30 * s), sc["num"], font=font("black", 260 * s), fill=rgba(C["accent"], 70 * p), anchor="mb")
    f = font("black", 92 * s)
    lines = wrap_tokens(tokens(sc["title"]), f, ctx.maxw)
    draw_rich(d, lines, f, ctx.cx, ctx.mid - 10 * s, 104 * s, reveal=clamp(t / 0.9))
    bw = ctx.maxw * 0.25 * p
    d.rectangle([ctx.cx - bw / 2, ctx.mid + len(lines) * 104 * s + 10 * s, ctx.cx + bw / 2, ctx.mid + len(lines) * 104 * s + 18 * s], fill=rgba(C["accent"]))

def sc_end(ctx, L, sc, t, dur):
    s = ctx.s; d = L.d
    group(ctx, L, t, 0, lambda dd, oy: icon(dd, "chat", ctx.cx, ctx.mid - 170 * s + oy, 80 * s, "accent"), dy=30)
    f = font("black", 76 * s)
    lines = wrap_tokens(tokens(sc["text"]), f, ctx.maxw)
    draw_rich(d, lines, f, ctx.cx, ctx.mid - 40 * s, 88 * s, reveal=clamp(t / 1.0))
    yb = ctx.mid - 40 * s + len(lines) * 88 * s + 50 * s
    def btn(dd, oy):
        fb = font("black", 46 * s); lab = sc.get("button", "SUSCRÍBETE"); bw = fb.getlength(lab) + 90 * s
        rrect(dd, (ctx.cx - bw / 2, yb + oy, ctx.cx + bw / 2, yb + 96 * s + oy), 48 * s, rgba(C["red"]))
        dd.text((ctx.cx, yb + 48 * s + oy), lab, font=fb, fill=rgba(C["text"]), anchor="mm")
    group(ctx, L, t, sc.get("btn_at", 1.2), btn, dy=30)

# ---------- subtítulos ----------
def sub_chunks(text, maxc):
    words = text.split(); chunks, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > maxc:
            chunks.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: chunks.append(cur)
    # evitar trozos mínimos al final
    if len(chunks) > 1 and len(chunks[-1]) < maxc * 0.25:
        last = chunks.pop(); chunks[-1] += " " + last
    return chunks

def draw_sub(ctx, L, text):
    s = ctx.s; d = L.d
    f = font("sb", (40 if not ctx.v else 52) * s); lh = f.size * 1.28
    lines = wrap_tokens([(w, None) for w in text.split()], f, ctx.W * (0.78 if not ctx.v else 0.84))
    w, h = text_block_size(lines, f, lh)
    y = ctx.H * (0.865 if not ctx.v else 0.715)
    rrect(d, (ctx.cx - w / 2 - 26 * s, y - 14 * s, ctx.cx + w / 2 + 26 * s, y + h + 10 * s), 18 * s, (0, 0, 0, 165))
    draw_rich(d, lines, f, ctx.cx, y, lh)
