import sys; sys.argv=["x"]
import engine as E
from PIL import Image, ImageDraw, ImageFilter
W,H=1280,720
bg=E.Background(W,H).frame(3.0).convert("RGB")
d=ImageDraw.Draw(bg,"RGBA")
# halo rojo detrás del número
glow=Image.new("RGBA",(W,H),(0,0,0,0)); g=ImageDraw.Draw(glow)
g.ellipse([60,90,720,650],fill=(255,92,96,90)); glow=glow.filter(ImageFilter.GaussianBlur(80))
bg.paste(glow,(0,0),glow); d=ImageDraw.Draw(bg,"RGBA")
f=E.font("black",400)
d.text((390,350),"+80",font=f,fill=E.C["accent"],anchor="mm",stroke_width=6,stroke_fill=E.C["dark"])
f2=E.font("black",112)
d.text((1000,330),"FUERA DE",font=E.font("black",84),fill=E.C["text"],anchor="mm")
d.text((1000,445),"CONTROL",font=E.font("black",100),fill=E.C["red"],anchor="mm")
# robot con señal de alerta
E.icon(d,"robot",1000,195,56,"red")
E.rrect(d,(40,620,300,690),20,E.rgba(E.C["dark"],220))
d.text((170,655),"PULSO IA",font=E.font("b",36),fill=E.C["accent"],anchor="mm")
bg.save("thumb.jpg",quality=90); print(bg.size)
