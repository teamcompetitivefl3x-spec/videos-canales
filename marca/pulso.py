import sys, math
sys.path.insert(0, "/home/claude/build"); sys.argv = ["x", "long", "em_alex"]
import engine as E
from PIL import Image, ImageDraw, ImageFilter
OUT = "/home/claude/piloto/"
CY, MG = (0, 220, 255), (255, 60, 200)
def grad_line(Wd, Hd, pts, width, glow=True):
    lay = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    n = len(pts) - 1
    for i in range(n):
        k = i / max(1, n - 1); col = tuple(int(CY[j] + (MG[j] - CY[j]) * k) for j in range(3))
        d.line([pts[i], pts[i + 1]], fill=col + (255,), width=width)
    if glow:
        g = lay.filter(ImageFilter.GaussianBlur(width * 1.6)); out = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
        out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(lay); return out
    return lay
def pulse(x0, x1, y, amp, segs):
    pts = []; w = (x1 - x0)
    pattern = [0, 0, 0.05, -0.1, 0.9, -1.0, 0.35, 0, 0, 0]
    for s in range(segs):
        for k, v in enumerate(pattern):
            pts.append((x0 + w * (s + k / len(pattern)) / segs, y - v * amp))
    pts.append((x1, y)); return pts
# --- foto de perfil ---
S = 800; im = E.Background(S, S, seed=8).frame(3.0)
im.alpha_composite(grad_line(S, S, pulse(60, 740, 560, 120, 1), 16))
d = ImageDraw.Draw(im)
f = E.font("black", 330)
d.text((S / 2 + 6, 330 + 6), "IA", font=f, fill=(0, 0, 0, 120), anchor="mm")
d.text((S / 2, 330), "IA", font=f, fill=(255, 255, 255, 255), anchor="mm")
im.convert("RGB").save(OUT + "pulso_ia_foto_perfil_800.png")
# --- banner ---
W, H = 2560, 1440; cy = H / 2
b = E.Background(W, H, seed=8).frame(7.0)
b.alpha_composite(grad_line(W, H, pulse(0, W, cy + 175, 60, 6), 9))
d = ImageDraw.Draw(b)
f = E.font("black", 240); w1, w2, gap = f.getlength("PULSO"), f.getlength("IA"), 50
x0 = W / 2 - (w1 + gap + w2) / 2
d.text((x0, cy - 80), "PULSO", font=f, fill=(255, 255, 255, 255), anchor="lm")
d.text((x0 + w1 + gap, cy - 80), "IA", font=f, fill=CY + (255,), anchor="lm")
d.text((W / 2, cy + 70), "Noticias e historias increíbles de la IA", font=E.font("b", 58), fill=(255, 255, 255, 240), anchor="mm")
tags = ["NOTICIAS", "HERRAMIENTAS", "HISTORIAS", "CURIOSIDADES"]; ft = E.font("b", 34)
widths = [ft.getlength(t) + 70 for t in tags]; tot = sum(widths) + 30 * (len(tags) - 1); x = W / 2 - tot / 2
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
for t_, w_ in zip(tags, widths):
    E.rrect(ld, (x, cy + 265, x + w_, cy + 325), 30, (20, 24, 50, 230), outline=MG + (230,), width=3)
    ld.text((x + w_ / 2, cy + 295), t_, font=ft, fill=(255, 255, 255, 255), anchor="mm"); x += w_ + 30
b.alpha_composite(lay)
b.convert("RGB").save(OUT + "pulso_ia_banner_2560x1440.png")
print("ok")
