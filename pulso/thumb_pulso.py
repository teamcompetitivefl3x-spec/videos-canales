import sys; sys.argv=["x"]
import engine as E
from PIL import Image, ImageDraw, ImageFilter
W,H=1280,720
bg=E.Background(W,H).frame(3.0).convert("RGB")
glow=Image.new("RGBA",(W,H),(0,0,0,0)); g=ImageDraw.Draw(glow)
g.ellipse([20,90,720,670],fill=(255,92,96,90)); glow=glow.filter(ImageFilter.GaussianBlur(85))
bg.paste(glow,(0,0),glow); d=ImageDraw.Draw(bg,"RGBA")
d.text((370,330),"29M",font=E.fit("black",360,"29M",680),fill=E.C["red"],anchor="mm",stroke_width=7,stroke_fill=E.C["dark"])
d.text((1000,290),"CANCIONES IA",font=E.fit("black",96,"CANCIONES IA",520),fill=E.C["text"],anchor="mm")
E.rrect(d,(760,360,1240,480),24,E.rgba(E.C["accent"]))
d.text((1000,420),"BORRADAS",font=E.fit("black",104,"BORRADAS",440),fill=E.C["dark"],anchor="mm")
E.icon(d,"cross",1000,165,60,"red")
E.rrect(d,(40,620,300,690),20,E.rgba(E.C["dark"],220))
d.text((170,655),"PULSO IA",font=E.font("b",36),fill=E.C["accent"],anchor="mm")
bg.save("thumb.jpg",quality=90); print(bg.size)
