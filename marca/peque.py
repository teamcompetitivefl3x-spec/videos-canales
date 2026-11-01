import sys, math, random
sys.path.insert(0, "/home/claude/kids"); sys.argv = ["x", "long"]
import os; os.chdir("/home/claude/kids")
import kids_render as K
from PIL import Image, ImageDraw, ImageFilter
OUT = "/home/claude/piloto/"
NIGHT1, NIGHT2 = (60, 40, 140), (120, 80, 200)
def sky(W, H, seed=3):
    im = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H; d.line([(0, y), (W, y)], fill=tuple(int(NIGHT1[i] + (NIGHT2[i] - NIGHT1[i]) * k) for i in range(3)) + (255,))
    r = random.Random(seed)
    for _ in range(int(W * H / 9000)):
        x, y, s = r.uniform(0, W), r.uniform(0, H), r.uniform(2, 6)
        d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 255, int(r.uniform(120, 255))))
    for _ in range(int(W * H / 120000)):
        x, y, s = r.uniform(0, W), r.uniform(0, H), r.uniform(14, 26)
        d.polygon(K.star_pts(x, y, s, s * 0.45), fill=K.COL["yellow"] + (255,))
    return im
def planet(size, t=0.0):
    S = 3; W = size * S; im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = W / 2; r = W * 0.30
    # anillo trasero
    for k, col in enumerate(K.RAINBOW[:6]):
        rr = r * (1.55 - k * 0.07)
        d.arc([c - rr, c + r * 0.5 - rr * 0.32, c + rr, c + r * 0.5 + rr * 0.32], 180, 360, fill=col, width=int(W * 0.022))
    d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 170, 60), outline=(230, 120, 30), width=int(W * 0.012))
    
    for (x, y, rr) in ((-0.45, -0.45, 0.13), (0.5, -0.25, 0.09), (0.25, 0.3, 0.08)):
        d.ellipse([c + r * x - r * rr, c + r * y - r * rr, c + r * x + r * rr, c + r * y + r * rr], fill=(240, 130, 50))
    # carita
    for ex in (-0.32, 0.32):
        K.eye(d, c + r * ex, c - r * 0.3, r * 0.16, r * 0.19, 0.0, False)
    d.ellipse([c - r * 0.68, c - r * 0.12, c - r * 0.42, c + r * 0.05], fill=(255, 120, 140))
    d.ellipse([c + r * 0.42, c - r * 0.12, c + r * 0.68, c + r * 0.05], fill=(255, 120, 140))
    d.arc([c - r * 0.25, c - r * 0.2, c + r * 0.25, c + r * 0.2], 20, 160, fill=K.COL["dark"], width=int(W * 0.014))
    # anillo delantero
    for k, col in enumerate(K.RAINBOW[:6]):
        rr = r * (1.55 - k * 0.07)
        d.arc([c - rr, c + r * 0.5 - rr * 0.32, c + rr, c + r * 0.5 + rr * 0.32], 0, 180, fill=col, width=int(W * 0.022))
    return im.resize((size, size), Image.LANCZOS)
# foto de perfil
S = 800; im = sky(S, S, 5); im.alpha_composite(planet(820), (-10, -10))
im.convert("RGB").save(OUT + "pequeplaneta_foto_perfil_800.png")
# banner
W, H = 2560, 1440; cy = H / 2
b = sky(W, H, 7)
K.paste_c(b, planet(620), 330, cy - 20)
d = ImageDraw.Draw(b)
txt = "PequePlaneta"; f = K.font(185); ws = [f.getlength(c) for c in txt]; tot = sum(ws) + 4 * (len(txt) - 1); x = W / 2 - tot / 2
for k, c in enumerate(txt):
    K.outlined(d, (x + ws[k] / 2, cy - 55 + (k % 2) * 10), c, f, K.RAINBOW[k % 10], sw=16); x += ws[k] + 4
K.outlined(d, (W / 2, cy + 105), "Cuentos, juegos y aprendizaje para los más peques", K.font(54), (255, 255, 255), sw=9)
t = K.draw_tula(1.0, 0.0); t = t.resize((int(t.width * 0.75), int(t.height * 0.75))); b.alpha_composite(t, (2040, int(cy + 40)))
p = K.draw_pipo(0.7, 0.0); p = p.resize((int(p.width * 0.7), int(p.height * 0.7))); b.alpha_composite(p, (2120, int(cy - 330)))
K.paste_c(b, K.sprite("cohete", 300), 2380, 260, rot=-25)
for kind, xx, yy, s in (("globo", 1000, 1180, 160), ("estrella", 1600, 1200, 150), ("corazon", 1300, 230, 130)):
    K.paste_c(b, K.sprite(kind, s, color=(K.RAINBOW[5] if kind == "corazon" else None)), xx, yy)
b.convert("RGB").save(OUT + "pequeplaneta_banner_2560x1440.png")
print("ok")
