"""Voces de Tula (ef_dora) y Pipo (em_alex con tono agudo). Genera kids_voz.wav + kids_timeline.json"""
import json, subprocess, numpy as np, soundfile as sf, os
from kokoro_onnx import Kokoro
from script import build
SR = 24000; FPS = 25
k = Kokoro("/home/claude/models/kokoro-v1.0.onnx", "/home/claude/models/voices-v1.0.bin")
PRON = [("Pipo", "Pipo"), ("¡Pío, pío!", "¡Pío, pío!"), ("Ñam, ñam", "Ñam, ñam")]
def voice(who, text):
    if who == "tula":
        s, _ = k.create(text, voice="ef_dora", speed=0.9, lang="es")
        return s.astype(np.float32)
    s, _ = k.create(text, voice="em_alex", speed=0.95, lang="es")
    sf.write("_tmp_in.wav", s, SR)
    r = 1.38
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "_tmp_in.wav", "-af",
                    f"asetrate={int(SR*r)},aresample={SR},atempo={1/r:.5f}", "_tmp_out.wav"], check=True)
    o, _ = sf.read("_tmp_out.wav"); return o.astype(np.float32)
ev = build(); t = 0.3; chunks = [np.zeros(int(0.3 * SR), np.float32)]
for i, e in enumerate(ev):
    e["start"] = round(t, 3)
    if e["text"]:
        s = voice(e["who"], e["text"])
        nz = np.where(np.abs(s) > 0.01)[0]
        if len(nz): s = s[max(0, nz[0] - 200): nz[-1] + 1000]
        s = s / max(1e-6, np.abs(s).max()) * 0.85
        # envolvente para sincronizar la boca (25 fps)
        hop = SR // FPS; env = [float(np.sqrt(np.mean(s[j:j + hop] ** 2))) for j in range(0, len(s), hop)]
        m = max(env) or 1; e["env"] = [round(min(1, v / m * 1.4), 2) for v in env]
        chunks.append(s); t += len(s) / SR
    e["end"] = round(t, 3)
    chunks.append(np.zeros(int(e["pause"] * SR), np.float32)); t += e["pause"]
    print(f"{i:3d} {e['start']:7.2f} {e['who'] or '-':5s} {e['text'] or e['do']}", flush=True)
a = np.concatenate(chunks); sf.write("kids_voz.wav", a, SR)
json.dump({"duration": round(t, 3), "events": ev}, open("kids_timeline.json", "w"), ensure_ascii=False)
print("TOTAL", round(t, 1), "s")
