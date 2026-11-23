import sys; sys.argv=["x"]
import engine as E
from PIL import Image, ImageDraw, ImageFilter
W,H=1280,720
bg=E.Background(W,H).frame(3.0).convert("RGB")
glow=Image.new("RGBA",(W,H),(0,0,0,0)); g=ImageDraw.Draw(glow)
g.ellipse([40,100,700,660],fill=(255,199,56,80)); glow=glow.filter(ImageFilter.GaussianBlur(80))
bg.paste(glow,(0,0),glow); d=ImageDraw.Draw(bg,"RGBA")
d.text((375,360),"+49%",font=E.fit("black",330,"+49%",660),fill=E.C["accent"],anchor="mm",stroke_width=6,stroke_fill=E.C["dark"])
d.text((990,330),"TE DA LA",font=E.font("black",92),fill=E.C["text"],anchor="mm")
d.text((990,450),"RAZÓN",font=E.font("black",132),fill=E.C["red"],anchor="mm")
E.icon(d,"robot",990,170,62,"accent")
E.rrect(d,(40,620,300,690),20,E.rgba(E.C["dark"],220))
d.text((170,655),"PULSO IA",font=E.font("b",36),fill=E.C["accent"],anchor="mm")
bg.save("thumb.jpg",quality=90); print(bg.size)
