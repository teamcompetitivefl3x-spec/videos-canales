import sys, math
sys.path.insert(0, "/home/claude/kids"); sys.argv = ["x", "long"]
import os; os.chdir("/home/claude/kids")
import kids_render as K
from PIL import Image, ImageDraw, ImageFilter
OUT = "/home/claude/piloto/"

# ===== TULA Y PIPO =====
# Foto de perfil 800x800 (se ve recortada en círculo)
S = 800; im = Image.new("RGBA", (S, S), (255, 214, 70, 255)); d = ImageDraw.Draw(im)
for i in range(16):
    a0 = math.radians(i * 22.5); a1 = a0 + math.radians(11)
    d.polygon([(S/2, S/2), (S/2 + 900*math.cos(a0), S/2 + 900*math.sin(a0)), (S/2 + 900*math.cos(a1), S/2 + 900*math.sin(a1))], fill=(255, 232, 120, 255))
t = K.draw_tula(0.4, 0.0); t = t.resize((int(t.width*1.05), int(t.height*1.05)))
im.alpha_composite(t, (-40, S - t.height + 10))
p = K.draw_pipo(0.2, 0.0); p = p.resize((int(p.width*0.95), int(p.height*0.95)))
im.alpha_composite(p, (S - p.width + 20, 60))
im.convert("RGB").save(OUT + "tula_y_pipo_foto_perfil_800.png")

# Banner 2560x1440 (zona segura central 1546x423)
W, H = 2560, 1440
sc = K.Scenery(W, H); b = sc.frame(5.0); d = ImageDraw.Draw(b)
cy = H / 2
txt = "Tula y Pipo"; f = K.font(190); ws = [f.getlength(c) for c in txt]; tot = sum(ws) + 6 * (len(txt) - 1); x = W / 2 - tot / 2
for k, c in enumerate(txt):
    if c != " ": K.outlined(d, (x + ws[k] / 2, cy - 55 + (k % 2) * 10), c, f, K.RAINBOW[k % 10], sw=16)
    x += ws[k] + 6
K.outlined(d, (W / 2, cy + 105), "¡Aprende jugando! Números, colores y más", K.font(56), (255, 255, 255), sw=9)
t = K.draw_tula(1.0, 0.0); t = t.resize((int(t.width*0.9), int(t.height*0.9))); b.alpha_composite(t, (-60, int(cy - 120)))
p = K.draw_pipo(0.7, 0.0); p = p.resize((int(p.width*0.85), int(p.height*0.85))); b.alpha_composite(p, (2090, int(cy - 330)))
for k, (kind, xx, yy, s) in enumerate((("globo", 330, 300, 220), ("estrella", 2300, 330, 190), ("manzana", 560, 1180, 170), ("pelota", 2000, 1150, 170), ("corazon", 1280, 250, 150))):
    K.paste_c(b, K.sprite(kind, s, color=(K.RAINBOW[4] if kind == "corazon" else None)), xx, yy)
b.convert("RGB").save(OUT + "tula_y_pipo_banner_2560x1440.png")

# ===== CASO REAL =====
sys.path.insert(0, "/home/claude/build")
import engine as E
NAVY1, NAVY2 = (8, 12, 26), (26, 32, 64)
def navy(Wd, Hd):
    bg = E.Background(Wd, Hd, seed=5).frame(10.0); return bg
# foto de perfil
im = navy(S, S); d = ImageDraw.Draw(im)
d.ellipse([90, 90, S - 90, S - 90], outline=E.rgba(E.C["accent"]), width=18)
E_f = E.font("black", 300)
d.text((S / 2, S / 2 - 40), "CR", font=E_f, fill=E.rgba(E.C["accent"]), anchor="mm")
pts = [(250, 650), (340, 615), (410, 638), (550, 560)]
d.line(pts, fill=E.rgba(E.C["teal"]), width=16, joint="curve")
d.polygon([(578, 543), (522, 548), (558, 592)], fill=E.rgba(E.C["teal"]))
im.convert("RGB").save(OUT + "caso_real_foto_perfil_800.png")
# banner
b = navy(W, H); d = ImageDraw.Draw(b)
d.text((W / 2, cy - 95), "CASO REAL", font=E.font("black", 230), fill=E.rgba(E.C["text"]), anchor="mm")
d.rectangle([W / 2 - 420, cy + 22, W / 2 + 420, cy + 32], fill=E.rgba(E.C["accent"]))
d.text((W / 2, cy + 90), "Negocios e IA, explicados con datos reales", font=E.font("b", 64), fill=E.rgba(E.C["accent"]), anchor="mm")
d.text((W / 2, cy + 160), "Un caso nuevo cada semana", font=E.font("m", 44), fill=E.rgba(E.C["muted"]), anchor="mm")
def card(x, y, val, lab, col):
    E.rrect(d, (x, y, x + 380, y + 190), 28, E.rgba(E.C["card"]), outline=E.rgba(E.C[col]), width=4)
    d.text((x + 34, y + 80), val, font=E.fit("black", 76, val, 320), fill=E.rgba(E.C[col]), anchor="lm")
    d.text((x + 34, y + 145), lab, font=E.font("sb", 30), fill=E.rgba(E.C["muted"]), anchor="lm")
card(150, 470, "+104 %", "ingresos", "teal"); card(150, 700, "−49 %", "plantilla", "accent")
card(W - 530, 470, "700", "«equivalentes»", "red"); card(W - 530, 700, "US$ 1,2 M", "por empleado", "blue")
b.convert("RGB").save(OUT + "caso_real_banner_2560x1440.png")
print("ok")
