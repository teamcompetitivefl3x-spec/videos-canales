"""Arma pistas de narración/SFX por pieza y mezcla final. Uso: python3 audio.py long|short IDX"""
import sys, json, subprocess, numpy as np, soundfile as sf
ARGS = sys.argv[1:] + [""] * 2
mode = ARGS[0]
sys.argv = ["render.py", mode, "em_alex"]
import render as R  # reutiliza timeline y escenas (no renderiza al importar)

SR = 48000
nar, nsr = sf.read("narracion_em_alex.wav")
from scipy.signal import resample_poly
nar = resample_poly(nar, SR, nsr)
items = R.ITEMS
wh, wsr = sf.read("whoosh.wav")
wh = resample_poly(wh, SR, wsr) if wsr != SR else wh

if mode == "long":
    W, H, times, total, scenes, spec, sents = R.build_long()
    name = "long"
    track = nar.copy()
    N = int(total * SR) + SR
    v = np.zeros(N); v[:len(track)] = track[:N]
else:
    idx = int(ARGS[1])
    W, H, times, total, scenes, spec, sents = R.build_short(idx)
    name = spec["name"]
    N = int(total * SR) + SR
    v = np.zeros(N)
    for i in sents:
        a, b = items[i]["start"], items[i]["end"]
        seg = nar[int(a * SR): int(b * SR)]
        st = int(times[i][0] * SR)
        v[st: st + len(seg)] = seg[: N - st]
scenes = R.prepare(times, total, scenes)
sfx = np.zeros((N, 2))
for sc in scenes[1:]:
    st = int(max(0, sc["start"] - 0.2) * SR)
    seg = wh[: N - st] * (0.16 if sc["type"] != "chapter" else 0.3)
    sfx[st: st + len(seg)] += seg
v = v[: int(total * SR)]; sfx = sfx[: int(total * SR)]
sf.write(f"{name}_voz.wav", v.astype(np.float32), SR)
sf.write(f"{name}_sfx.wav", sfx.astype(np.float32), SR)
seed = {"long": 7}.get(name, 11 + len(name))
subprocess.run(["python3", "music.py", str(total + 1), f"{name}_music.wav", str(seed)], check=True)
fc = ("[0:a]aformat=channel_layouts=stereo,asplit=2[v1][v2];"
      "[1:a]volume=0.30[m];[m][v1]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=500:makeup=1[md];"
      "[2:a]aformat=channel_layouts=stereo[s];"
      "[v2][md][s]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{name}_voz.wav", "-i", f"{name}_music.wav", "-i", f"{name}_sfx.wav",
                "-filter_complex", fc, "-map", "[a]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", f"{name}_mix.m4a"], check=True)
print("ok", name, total)
