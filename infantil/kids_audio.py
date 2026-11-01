"""Música infantil original + efectos + mezcla final. Uso: python3 kids_audio.py"""
import json, subprocess, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt, resample_poly
SR = 48000
TL = json.load(open("kids_timeline.json")); EV = TL["events"]; TOTAL = TL["duration"]
N = int((TOTAL + 0.5) * SR); t = np.arange(N) / SR
rng = np.random.default_rng(5)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def lp(x, fc): a = np.exp(-2 * np.pi * fc / SR); return lfilter([1 - a], [1, -a], x)

# ---------- música: C - G - Am - F a 112 BPM ----------
BPM = 112; beat = 60 / BPM; bar = 4 * beat
prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
bass = [36, 43, 45, 41]
mel = [72, 74, 76, 79, 76, 74, 72, 67, 69, 72, 71, 67, 65, 67, 69, 72]  # motivo pegadizo
music = np.zeros(N)
def add(x0, sig):
    i0 = int(x0 * SR)
    if i0 >= N: return
    sig = sig[: N - i0]; music[i0: i0 + len(sig)] += sig
def pluck(f, dur=0.5, amp=0.1, dec=0.18):
    tt = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(8 * np.pi * f * tt)) * np.exp(-tt / dec) * np.minimum(1, tt / 0.003) * amp
nbars = int(TOTAL / bar) + 2
for b in range(nbars):
    b0 = b * bar; ch = prog[b % 4]
    for q in range(4):
        add(b0 + q * beat, pluck(midi(bass[b % 4] + (12 if q % 2 else 0)), 0.45, 0.20, 0.22))
    for e in range(8):  # acordes en corcheas (marimba)
        if e % 2 == 1:
            for n in ch: add(b0 + e * beat / 2, pluck(midi(n + 12), 0.3, 0.035, 0.09))
    if b % 8 >= 4:  # melodía cada 4 compases
        for k in range(4):
            add(b0 + k * beat, pluck(midi(mel[(b * 4 + k) % 16]), 0.6, 0.075, 0.25))
    for q in (1, 3):  # palmas
        n_ = int(0.09 * SR); tt = np.arange(n_) / SR
        add(b0 + q * beat, sosfilt(butter(2, [900, 4000], "band", fs=SR, output="sos"), rng.normal(0, 1, n_)) * np.exp(-tt / 0.025) * 0.10)
    for e in range(8):  # maraca
        n_ = int(0.05 * SR); tt = np.arange(n_) / SR
        add(b0 + e * beat / 2, sosfilt(butter(2, 5000, "high", fs=SR, output="sos"), rng.normal(0, 1, n_)) * np.exp(-tt / 0.012) * (0.035 if e % 2 else 0.02))
fade = int(2 * SR); music[:fade] *= np.linspace(0, 1, fade); music[-fade:] *= np.linspace(1, 0, fade)
music = music / np.abs(music).max() * 0.8

# ---------- efectos ----------
sfx = np.zeros(N)
def at(x0, sig, g=1.0):
    i0 = int(x0 * SR)
    if 0 <= i0 < N: s = sig[: N - i0] * g; sfx[i0: i0 + len(s)] += s
def pop():
    n_ = int(0.12 * SR); tt = np.arange(n_) / SR; f = 500 + 900 * tt / 0.12
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.04) * 0.5
def ding(f0=1318.5):
    n_ = int(0.9 * SR); tt = np.arange(n_) / SR
    return (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2.01 * tt)) * np.exp(-tt / 0.3) * 0.35
def tada():
    out = np.zeros(int(1.2 * SR))
    for k, n in enumerate((72, 76, 79, 84)):
        s = pluck(midi(n), 0.8, 0.4, 0.3); i = int(k * 0.09 * SR); out[i:i + len(s)] += s[: len(out) - i]
    return out
def whoosh():
    n_ = int(0.5 * SR); tt = np.arange(n_) / SR
    x = sosfilt(butter(2, [400, 3000], "band", fs=SR, output="sos"), rng.normal(0, 1, n_)) * np.sin(np.pi * tt / 0.5) ** 2
    return x / np.abs(x).max() * 0.25
def rumble():
    n_ = int(2.8 * SR); tt = np.arange(n_) / SR
    x = lp(rng.normal(0, 1, n_), 300) * np.minimum(1, tt / 0.2) * np.exp(-np.maximum(0, tt - 1.2) / 0.8)
    return x / np.abs(x).max() * 0.6
P, D, T, W, R = pop(), ding(), tada(), whoosh(), rumble()
for e in EV:
    for a in e["do"]:
        k = a[0]; s0 = e["start"]
        if k == "scene": at(s0 - 0.15, W)
        elif k in ("pop", "rpop", "cd"): at(s0, P)
        elif k in ("numeral", "fill", "sc", "reveal"): at(s0, D)
        elif k in ("confetti",): at(s0, T)
        elif k == "launch": at(s0, R)
        elif k in ("popall", "sa", "sb"): at(s0, P, 0.8)
    if any(a[0] == "scene" and a[1] in ("title", "end", "hello") for a in e["do"]): at(e["start"] + 0.3, T, 0.8)

sf.write("kids_music.wav", np.stack([music, music], 1).astype(np.float32), SR)
sf.write("kids_sfx.wav", np.stack([sfx, sfx], 1).astype(np.float32), SR)
fc = ("[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v1][v2];"
      "[1:a]volume=0.34[m];[m][v1]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=600[md];"
      "[v2][md][2:a]amix=inputs=3:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "kids_voz.wav", "-i", "kids_music.wav", "-i", "kids_sfx.wav",
                "-filter_complex", fc, "-map", "[a]", "-t", f"{TOTAL:.3f}", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "kids_mix.m4a"], check=True)
print("ok", TOTAL)
