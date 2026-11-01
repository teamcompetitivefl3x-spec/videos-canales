"""Render: python3 render.py long VOICE [f0 f1 out.mp4]  |  python3 render.py short VOICE IDX"""
import sys, json, math, subprocess
import numpy as np, soundfile as sf
from PIL import Image
import engine as E
from scenes import SCENES, SHORTS, CHAPTERS

FPS = 25
mode, VOICE = sys.argv[1], sys.argv[2]
TL = json.load(open(f"timeline_{VOICE}.json"))
ITEMS = TL["items"]

def build_long():
    W, H = 1920, 1080
    times = {i: (it["start"], it["end"]) for i, it in enumerate(ITEMS)}
    total = TL["duration"]
    scenes = [dict(sc) for sc in SCENES]
    return W, H, times, total, scenes, None, list(range(len(ITEMS)))

def build_short(idx):
    W, H = 1080, 1920
    spec = SHORTS[idx]; sents = spec["sents"]
    times, t = {}, 0.35
    for k, i in enumerate(sents):
        a, b = ITEMS[i]["start"], ITEMS[i]["end"]
        if k: t += 0.32
        times[i] = (t, t + (b - a)); t += b - a
    end_t = t + 0.5
    total = end_t + 3.2
    scenes = [dict(sc) for sc in SCENES if int(sc["at"]) in sents]
    scenes.append(dict(at=None, start=end_t, type="end", text="Historia completa en el *canal*", button="VER VIDEO", btn_at=0.5))
    return W, H, times, total, scenes, spec, sents

def tm(times, at):
    i = int(at); fr = at - i; a, b = times[i]
    return a + fr * (b - a)

def prepare(times, total, scenes):
    for k, sc in enumerate(scenes):
        if sc.get("at") is not None:
            st = tm(times, sc["at"])
            sc["start"] = 0.0 if k == 0 else max(0.0, st - 0.15)
    scenes.sort(key=lambda s: s["start"])
    for k, sc in enumerate(scenes):
        sc["end"] = scenes[k + 1]["start"] if k + 1 < len(scenes) else total
        if sc.get("reveal"):
            sc["_delays"] = [max(0.15, times[r][0] - sc["start"]) if r in times else 0.2 + j * 1.2 for j, r in enumerate(sc["reveal"])]
    return scenes

def sub_events(times, maxc):
    ev = []
    for i, (a, b) in sorted(times.items(), key=lambda x: x[1][0]):
        txt = ITEMS[i]["text"].replace("*", "")
        ch = E.sub_chunks(txt, maxc); tot = sum(len(c) for c in ch); t = a
        for c in ch:
            d = (b - a) * len(c) / tot
            ev.append((t, t + d, c)); t += d
    return ev

def main():
    if mode == "long":
        W, H, times, total, scenes, spec, sents = build_long()
    else:
        W, H, times, total, scenes, spec, sents = build_short(int(sys.argv[3]))
    scenes = prepare(times, total, scenes)
    ctx = E.Ctx(W, H); bg = E.Background(W, H)
    subs = sub_events(times, 64 if W > H else 34)
    nfr = int(math.ceil(total * FPS))
    f0, f1, out = 0, nfr, None
    if mode == "long" and len(sys.argv) > 3 and not sys.argv[3].startswith("--"):
        f0, f1, out = int(sys.argv[3]), min(nfr, int(sys.argv[4])), sys.argv[5]
    if out is None:
        out = "long_video.mp4" if mode == "long" else f"{spec['name']}_video.mp4"
    if "--info" in sys.argv:
        print(nfr, total); return
    sec_of = {i: ITEMS[i]["sec"] for i in sents}
    frames_only = None
    for a in sys.argv:
        if a.startswith("--frames="):
            frames_only = [int(float(x) * FPS) for x in a.split("=")[1].split(",")]
    if frames_only:
        class _N:
            def write(self, b): pass
            def close(self): pass
        class _P:
            stdin = _N()
            def wait(self): pass
        ff = _P(); rng_frames = frames_only
    else:
        rng_frames = range(f0, f1)
    if not frames_only: ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                           "-pix_fmt", "yuv420p", "-r", str(FPS), out], stdin=subprocess.PIPE)
    si = 0; ji = 0
    for fr in rng_frames:
        if frames_only: si = 0; ji = 0
        t = fr / FPS
        while si + 1 < len(scenes) and scenes[si + 1]["start"] <= t: si += 1
        sc = scenes[si]
        im = bg.frame(t)
        L = E.Layer(W, H)
        lt, dur = t - sc["start"], sc["end"] - sc["start"]
        E.draw_scene(ctx, L, sc, lt, dur)
        a = min(1.0, E.ease(lt / 0.22)) * min(1.0, max(0.0, (dur - lt) / 0.2))
        im.alpha_composite(E.apply_alpha(L.im, a))
        # barra superior: capítulo + progreso
        T = E.Layer(W, H); d = T.d; s = ctx.s
        cur = max((i for i in sents if times[i][0] <= t + 0.01), default=sents[0], key=lambda i: times[i][0])
        if mode == "long":
            d.rectangle([0, 0, W * (t / total), 6], fill=E.rgba(E.C["accent"]))
            d.text((60, 46), f"{CHAPTERS[sec_of[cur]]}", font=E.font("b", 28), fill=E.rgba(E.C["muted"], 230), anchor="lm")
            d.text((W - 60, 46), "PULSO IA", font=E.font("b", 24), fill=E.rgba(E.C["muted"], 150), anchor="rm")
        else:
            E.rrect(d, (60, 120, W - 60, 270), 36, E.rgba(E.C["dark"], 200))
            f = E.fit("black", 64, spec["title"], W - 180)
            d.text((W / 2, 195), spec["title"], font=f, fill=E.rgba(E.C["accent"]), anchor="mm")
            d.rectangle([0, 0, W * (t / total), 10], fill=E.rgba(E.C["accent"]))
        while ji + 1 < len(subs) and subs[ji + 1][0] <= t: ji += 1
        if subs and subs[ji][0] <= t < subs[ji][1] + 0.15 and sc["type"] != "chapter":
            E.draw_sub(ctx, T, subs[ji][2])
        im.alpha_composite(T.im)
        if frames_only:
            im.convert("RGB").save(f"prev_{mode}_{fr/FPS:07.2f}.jpg", quality=85); continue
        ff.stdin.write(im.convert("RGB").tobytes())
        if fr % 250 == 0: print(f"{out}: {fr}/{f1}", flush=True)
    ff.stdin.close(); ff.wait()
    if frames_only: return
    # metadatos para el audio de los shorts
    if mode == "short":
        json.dump({"times": {str(k): v for k, v in times.items()}, "total": total,
                   "scene_starts": [s["start"] for s in scenes]}, open(f"{spec['name']}_meta.json", "w"))
    else:
        json.dump({"total": total, "scene_starts": [s["start"] for s in scenes],
                   "chapters": [(s["start"], s["title"]) for s in scenes if s["type"] == "chapter"]}, open("long_meta.json", "w"), ensure_ascii=False)
    print("done", out)

if __name__ == "__main__":
    main()
