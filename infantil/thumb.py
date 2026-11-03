import sys; sys.argv = ["x", "long"]
import kids_render as K
from PIL import Image, ImageDraw
W, H = 1920, 1080
sc = K.Scenery(W, H); im = sc.frame(3.0); d = ImageDraw.Draw(im)
# fondo con rayos suaves
ray = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(ray)
import math
for i in range(16):
    a0 = math.radians(i * 22.5); a1 = a0 + math.radians(11)
    rd.polygon([(W / 2, 430), (W / 2 + 2000 * math.cos(a0), 430 + 2000 * math.sin(a0)), (W / 2 + 2000 * math.cos(a1), 430 + 2000 * math.sin(a1))], fill=(255, 255, 255, 38))
im.alpha_composite(ray); d = ImageDraw.Draw(im)
# título
import script as SC
TH = getattr(SC, "THUMB", None)
LINES = TH["lines"] if TH else ("¡CONTAMOS", "DEL 1 AL 10!")
for row, (txt, y, size, off) in enumerate(((LINES[0], 150, 200, 0), (LINES[1], 355, 200 if len(LINES[1]) <= 12 else 170, 4))):
    f = K.font(size); ws = [f.getlength(c) for c in txt]; tot = sum(ws) + 10 * (len(txt) - 1); x = W / 2 - tot / 2
    for k, c in enumerate(txt):
        K.outlined(d, (x + ws[k] / 2, y + (k % 2) * 14), c, f, K.RAINBOW[(k + off) % 10], sw=18); x += ws[k] + 10
# objetos
if TH and TH.get("objs"):
    objs = TH["objs"]; n = len(objs); xs = [580 + (720 * k / max(1, n - 1)) for k in range(n)]
    for k, kind in enumerate(objs):
        K.paste_c(im, K.sprite(kind, 300 if n <= 3 else 250, face=kind in K.SHAPES), xs[k], 585 + (k % 2) * -35, 1.0, (k - n // 2) * 6)
else:
    for k, (kind, x, y, s) in enumerate((("globo", 560, 640, 300), ("estrella", 960, 650, 260), ("manzana", 1360, 650, 280))):
        K.paste_c(im, K.sprite(kind, s), x, y)
    for k, n in enumerate((1, 2, 3)):
        K.badge(d, [660, 1060, 1470][k], [520, 530, 530][k], str(n), r=46)
t1 = K.draw_tula(0.5, 0.6); t1 = t1.resize((int(t1.width * 1.15), int(t1.height * 1.15)))
im.alpha_composite(t1, (-60, H - t1.height + 40))
p1 = K.draw_pipo(0.2, 0.7); p1 = p1.resize((int(p1.width * 1.1), int(p1.height * 1.1)))
im.alpha_composite(p1, (W - p1.width + 30, H - p1.height - 60))
im.convert("RGB").resize((1280, 720), Image.LANCZOS).save("/home/claude/piloto/kids_miniatura_1280x720.jpg", quality=92)
