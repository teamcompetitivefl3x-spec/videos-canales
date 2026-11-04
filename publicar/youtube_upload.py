"""Publica en YouTube los pedidos de cola/*.json con la API oficial (gratis). Corre en GitHub Actions.

Cada pedido (cola/AAAA-MM-DD_canal_tipo.json):
{
  "canal": "pulso" | "peque" | "curiosidades",      # clave de publicar/canales.json
  "titulo": "...", "descripcion": "...", "tags": ["..."],
  "categoria": "28",                                  # 28 Ciencia y tecnología, 27 Educación, 24 Entretenimiento
  "video": "https://raw.githubusercontent.com/.../archivo.mp4",
  "miniatura": "https://raw.githubusercontent.com/.../thumb.jpg",   # opcional
  "privacidad": "public", "notificar": true, "idioma": "es"
}
Resultado: publicados/<mismo nombre>.json con video_id, url, channel_id y channel_title (o "error").
Secretos: YT_CLIENT_ID, YT_CLIENT_SECRET y un refresh token por canal (ver canales.json).
"""
import glob, json, os, sys, time, datetime
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANALES = json.load(open(os.path.join(ROOT, "publicar", "canales.json"), encoding="utf-8"))
API = "https://www.googleapis.com/youtube/v3"
UP = "https://www.googleapis.com/upload/youtube/v3"


def token(refresh):
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": refresh, "grant_type": "refresh_token"}, timeout=60)
    r.raise_for_status()
    return r.json()["access_token"]


def descargar(url, dest):
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for ch in r.iter_content(1 << 20):
                f.write(ch)
    return os.path.getsize(dest)


def publicar(p, cfg):
    refresh = os.environ.get(cfg["secret"], "")
    if not refresh:
        raise RuntimeError(f"falta el secreto {cfg['secret']} en GitHub")
    h = {"Authorization": f"Bearer {token(refresh)}"}
    # 1) verificar que la cuenta autorizada es el canal correcto ANTES de subir
    me = requests.get(f"{API}/channels", params={"part": "snippet", "mine": "true"}, headers=h, timeout=60)
    me.raise_for_status()
    items = me.json().get("items", [])
    if not items:
        raise RuntimeError("el token no tiene ningún canal de YouTube")
    ch_id, ch_title = items[0]["id"], items[0]["snippet"]["title"]
    if cfg.get("channel_id") and ch_id != cfg["channel_id"]:
        raise RuntimeError(f"canal equivocado: el token es de '{ch_title}' ({ch_id}), se esperaba {cfg['channel_id']}")
    # 2) bajar el video
    vid = "/tmp/video.mp4"
    size = descargar(p["video"], vid)
    if size < 100_000:
        raise RuntimeError(f"el video pesa {size} bytes: ¿URL equivocada?")
    # 3) subida reanudable
    meta = {
        "snippet": {"title": p["titulo"][:100], "description": p["descripcion"][:5000], "tags": p.get("tags", []),
                    "categoryId": str(p.get("categoria", "28")), "defaultLanguage": p.get("idioma", "es"),
                    "defaultAudioLanguage": p.get("idioma", "es")},
        "status": {"privacyStatus": p.get("privacidad", "public"),
                   "selfDeclaredMadeForKids": bool(p.get("made_for_kids", cfg.get("made_for_kids", False))),
                   "embeddable": True, "publicStatsViewable": True, "license": "youtube"},
    }
    ini = requests.post(f"{UP}/videos", params={"uploadType": "resumable", "part": "snippet,status",
                                                 "notifySubscribers": str(p.get("notificar", True)).lower()},
                        headers={**h, "Content-Type": "application/json; charset=UTF-8",
                                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
                        data=json.dumps(meta), timeout=60)
    ini.raise_for_status()
    loc = ini.headers["Location"]
    for intento in range(5):
        with open(vid, "rb") as f:
            r = requests.put(loc, data=f, headers={**h, "Content-Type": "video/mp4", "Content-Length": str(size)}, timeout=3600)
        if r.status_code in (200, 201):
            break
        if r.status_code in (500, 502, 503, 504):
            time.sleep(10 * (intento + 1)); continue
        raise RuntimeError(f"subida falló: {r.status_code} {r.text[:500]}")
    else:
        raise RuntimeError("subida falló tras 5 intentos")
    v = r.json()
    out = {"video_id": v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}",
           "channel_id": v["snippet"]["channelId"], "channel_title": v["snippet"].get("channelTitle", ch_title),
           "privacidad": v["status"]["privacyStatus"], "titulo": v["snippet"]["title"]}
    # 4) miniatura (si el canal está verificado por teléfono)
    if p.get("miniatura"):
        try:
            img = requests.get(p["miniatura"], timeout=120); img.raise_for_status()
            t = requests.post(f"{UP}/thumbnails/set", params={"videoId": v["id"]},
                              headers={**h, "Content-Type": "image/jpeg"}, data=img.content, timeout=120)
            out["miniatura"] = "ok" if t.ok else f"error {t.status_code}: {t.text[:300]}"
        except Exception as e:  # la miniatura no debe tumbar una subida ya hecha
            out["miniatura"] = f"error: {e}"
    return out


def main():
    pedidos = sorted(glob.glob(os.path.join(ROOT, "cola", "*.json")))
    if not pedidos:
        print("cola vacía"); return 0
    fallos = 0
    for ruta in pedidos:
        nombre = os.path.basename(ruta)
        p = json.load(open(ruta, encoding="utf-8"))
        cfg = CANALES.get(p.get("canal"))
        res = {"pedido": nombre, "canal": p.get("canal"),
               "fecha": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        try:
            if not cfg:
                raise RuntimeError(f"canal desconocido: {p.get('canal')}")
            res.update(publicar(p, cfg))
            print(f"OK {nombre}: {res['url']} en '{res['channel_title']}'")
        except Exception as e:
            fallos += 1
            res["error"] = str(e)
            print(f"ERROR {nombre}: {e}", file=sys.stderr)
        json.dump(res, open(os.path.join(ROOT, "publicados", nombre), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        os.remove(ruta)  # el pedido sale de la cola pase lo que pase: nunca se sube dos veces solo
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
