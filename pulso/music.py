"""Música original de fondo (pad + bajo + arpegio suave) y efectos 'whoosh'. Uso: python3 music.py SEGUNDOS out.wav"""
import sys, numpy as np, soundfile as sf

SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
rng = np.random.default_rng(seed)
N = int(dur * SR); t = np.arange(N) / SR
BPM = 92; beat = 60 / BPM; bar = beat * 4

def midi(n): return 440 * 2 ** ((n - 69) / 12)
# Am - F - C - G  (2 compases por acorde)
prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
bass = [45, 41, 48, 43]
chord_len = bar * 2

def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)

pad = np.zeros(N, np.float32)
bas = np.zeros(N, np.float32)
arp = np.zeros(N, np.float32)
nchords = int(np.ceil(dur / chord_len)) + 1
for k in range(nchords):
    c0 = k * chord_len; i0 = int(c0 * SR); i1 = min(N, int((c0 + chord_len + 1.2) * SR))
    if i0 >= N: break
    tt = t[i0:i1] - c0
    env = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (chord_len + 1.2 - tt) / 1.2))
    ch = prog[k % 4]
    for n in ch:
        for det in (-0.12, 0.12):
            f = midi(n + det)
            pad[i0:i1] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env * 0.05
    fb = midi(bass[k % 4] - 12)
    benv = np.minimum(1, tt / 0.05) * np.exp(-tt / 3.0)
    bas[i0:i1] += np.sin(2 * np.pi * fb * tt) * benv * 0.22
    # arpegio en corcheas
    notes = ch + [ch[1] + 12, ch[2] + 12]
    for j in range(int(chord_len / (beat / 2))):
        n0 = c0 + j * beat / 2; a0 = int(n0 * SR); a1 = min(N, a0 + int(1.2 * SR))
        if a0 >= N: break
        ta = t[a0:a1] - n0
        f = midi(notes[(j * 3 + k) % len(notes)] + 12)
        vel = 0.05 * (1.0 if j % 4 == 0 else 0.7)
        arp[a0:a1] += np.sin(2 * np.pi * f * ta) * np.exp(-ta / 0.35) * np.minimum(1, ta / 0.004) * vel
# pulso suave (hi-hat filtrado)
hat = np.zeros(N, np.float32)
for j in range(int(dur / (beat / 2))):
    a0 = int(j * beat / 2 * SR); a1 = min(N, a0 + int(0.06 * SR))
    if a0 >= N: break
    ta = np.arange(a1 - a0) / SR
    hat[a0:a1] += rng.normal(0, 1, a1 - a0) * np.exp(-ta / 0.012) * (0.018 if j % 2 else 0.01)
hat = hat - lowpass(hat, 6000)
mix = lowpass(pad, 2200) + lowpass(bas, 400) + lowpass(arp, 3500) + hat
# entrada/salida
fade = int(3 * SR)
mix[:fade] *= np.linspace(0, 1, fade); mix[-fade:] *= np.linspace(1, 0, fade)
# eco estéreo simple
L = mix.copy(); R = mix.copy()
dl = int(beat * 0.75 * SR)
R[dl:] += 0.25 * mix[:-dl]; L[dl * 2:] += 0.15 * mix[:-dl * 2]
st = np.stack([L, R], 1)
st = st / np.abs(st).max() * 0.8
sf.write(out, st.astype(np.float32), SR)

# whoosh
if len(sys.argv) > 4:
    w = int(0.55 * SR); tw = np.arange(w) / SR
    noise = rng.normal(0, 1, w)
    from scipy.signal import butter, sosfilt
    env = np.sin(np.pi * np.minimum(1, tw / 0.55)) ** 2
    lo = sosfilt(butter(2, [300, 3000], btype="band", fs=SR, output="sos"), noise) * env
    lo = lo / np.abs(lo).max() * 0.5
    sf.write(sys.argv[4], np.stack([lo, lo * 0.9], 1).astype(np.float32), SR)
print("ok", out)
