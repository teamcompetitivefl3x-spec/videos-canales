"""Genera la narración frase por frase y guarda tiempos exactos (timeline.json + narracion.wav)."""
import re, json, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

GUION = "/home/claude/piloto/guion.md"
VOICE = sys.argv[1] if len(sys.argv) > 1 else "em_alex"
SPEED = 1.0
SR = 24000
GAP_SENT = 0.28   # pausa entre frases
GAP_PARA = 0.60   # pausa entre párrafos
GAP_SECT = 1.10   # pausa entre secciones

# Pronunciación para el TTS (el texto en pantalla no cambia)
PRON = [
    (r"\bOpenAI\b", "Oupen Ei Ai"), (r"\bChatGPT\b", "Chat yi pi ti"),
    (r"\bIA\b", "i a"), (r"\bWhatsApp\b", "Guatsap"), (r"\bUber\b", "Úber"),
    (r"Siemiatkowski", "Shemiatkovski"), (r"Gergely Orosz", "Guérguei Orosh"),
    (r"\bBloomberg\b", "Blúmberg"), (r"\bCEO\b", "director general"),
    (r"«|»|\"", ""),
]

def tts_text(s):
    for a, b in PRON:
        s = re.sub(a, b, s)
    return s

def parse():
    txt = open(GUION, encoding="utf-8").read().split("---", 1)[1]
    sections = re.split(r"^## ", txt, flags=re.M)[1:]
    out = []
    for si, sec in enumerate(sections):
        lines = sec.splitlines()
        title = lines[0]
        paras = [p.strip() for p in "\n".join(lines[1:]).split("\n\n") if p.strip()]
        for pi, p in enumerate(paras):
            sents = re.split(r"(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚÑ¿¡\"«0-9])", p)
            for s in sents:
                if s.strip():
                    out.append({"sec": si, "sec_title": title, "para": pi, "text": s.strip()})
    return out

def main():
    k = Kokoro("/home/claude/models/kokoro-v1.0.onnx", "/home/claude/models/voices-v1.0.bin")
    items = parse()
    audio = []
    t = 0.4
    audio.append(np.zeros(int(0.4 * SR), dtype=np.float32))
    prev = None
    for i, it in enumerate(items):
        if prev is not None:
            gap = GAP_SECT if it["sec"] != prev["sec"] else (GAP_PARA if it["para"] != prev["para"] else GAP_SENT)
            audio.append(np.zeros(int(gap * SR), dtype=np.float32)); t += gap
        s, sr = k.create(tts_text(it["text"]), voice=VOICE, speed=SPEED, lang="es")
        s = s.astype(np.float32)
        # recorte de silencios en los bordes
        nz = np.where(np.abs(s) > 0.01)[0]
        if len(nz):
            s = s[max(0, nz[0] - 240): nz[-1] + 1200]
        it["start"] = round(t, 3); t += len(s) / SR; it["end"] = round(t, 3)
        audio.append(s)
        prev = it
        print(f"{i:3d} {it['start']:7.2f}-{it['end']:7.2f} {it['text'][:60]}", flush=True)
    audio.append(np.zeros(int(1.5 * SR), dtype=np.float32)); t += 1.5
    a = np.concatenate(audio)
    a = a / max(1e-6, np.abs(a).max()) * 0.89
    sf.write(f"narracion_{VOICE}.wav", a, SR)
    json.dump({"voice": VOICE, "duration": round(t, 3), "items": items},
              open(f"timeline_{VOICE}.json", "w"), ensure_ascii=False, indent=1)
    print("TOTAL", t)

if __name__ == "__main__":
    main()
