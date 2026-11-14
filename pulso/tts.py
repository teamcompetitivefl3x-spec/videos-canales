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
    (r"\bNVIDIA\b", "Envidia"), (r"\bJensen Huang\b", "Yénsen Juang"), (r"\bHuang\b", "Juang"), (r"\bColette Kress\b", "Colét Kres"),
    (r"\bHarvey Jones\b", "Járvei Yóuns"), (r"\bTSMC\b", "te ese eme ce"), (r"\bFable 5\.2\b", "Féibol cinco punto dos"),
    (r"\bMythos 5\.2\b", "Mítos cinco punto dos"), (r"\bOpus 5\.5\b", "Óupus cinco punto cinco"), (r"\bGemini 4 Carbon\b", "Yémini cuatro Cárbon"),
    (r"\bGemini 4 Argon\b", "Yémini cuatro Árgon"), (r"\bAl Jazeera\b", "Al Yasira"), (r"\bTechCrunch\b", "Tec Cranch"),
    (r"\bWall Street\b(?! Journal)", "Guol Strit"), (r"\btokens\b", "tóquens"), (r"\btoken\b", "tóquen"), (r"\bCisco\b", "Sísco"),
    (r"\bMicrosoft\b", "Máicrosoft"), (r"\bApple\b", "Ápol"),
    (r"Builder\.ai", "Bílder Ei Ai"), (r"Engineer\.ai", "Inyiníer Ei Ai"), (r"Sachin Dev Duggal", "Sáchin Dev Dúgal"), (r"\bDuggal\b", "Dúgal"),
    (r"\bWall Street Journal\b", "Guol Strit Yérnal"), (r"\bQatar\b", "Catar"), (r"\bFast Company\b", "Fast Cómpani"), (r"\bEY\b", "i guai"),
    (r"\bManpreet Ratia\b", "Mánprit Rátia"), (r"\bRatia\b", "Rátia"), (r"\bFinancial Times\b", "Fainánshal Taims"), (r"\bViola Credit\b", "Viola Crédit"),
    (r"\bLinkedIn\b", "Linkedín"), (r"\bred social X\b", "red social equis"), (r"\bapps\b", "aps"), (r"\bapp\b", "ap"),
    (r"\bstartups\b", "estártaps"), (r"\bstartup\b", "estártap"), (r"\bmarketing\b", "márketing"), (r"\bGPT\b", "yi pi ti"),
    (r"\bVietnam\b", "Vietnám"), (r"\bbot\b", "bot"),
    (r"\bOpenAI\b", "Oupen Ei Ai"), (r"\bChatGPT\b", "Chat yi pi ti"),
    (r"\bIA\b", "i a"), (r"\bWhatsApp\b", "Guatsap"), (r"\bUber\b", "Úber"),
    (r"Siemiatkowski", "Shemiatkovski"), (r"Gergely Orosz", "Guérguei Orosh"),
    (r"\bBloomberg\b", "Blúmberg"), (r"\bCEO\b", "director general"),
    (r"\bWashington Post\b", "Guáshinton Post"), (r"\bRiverside\b", "Ríversaid"),
    (r"\bEpoch AI\b", "Épok Ei Ai"), (r"\bAltman\b", "Áltman"), (r"\bGemini\b", "Yémini"),
    (r"\bMIT Technology Review\b", "Em Ai Ti Teknólogi Riviú"), (r"\bGPT-4\b", "yi pi ti cuatro"),
    (r"\bShaolei Ren\b", "Shaolei Ren"), (r"\bstreaming\b", "estríming"), (r"\bGoogle\b", "Gúgol"),
    (r"\bHugging Face\b", "Jáguin Feis"), (r"\bExploitGym\b", "Éksploit Yim"), (r"\bGPT-5\.6 Sol\b", "yi pi ti cinco punto seis Sol"),
    (r"\bBlack Hat\b", "Blak Jat"), (r"\bWired\b", "Guáired"), (r"\bReuters\b", "Róiters"), (r"\bEric Wallace\b", "Érik Guólas"),
    (r"\bWallace\b", "Guólas"), (r"\bMichael Dalton\b", "Máikol Dálton"), (r"\bDalton\b", "Dálton"), (r"\bClem Delangue\b", "Clem Delang"),
    (r"\bGLM 5\.2\b", "ye ele eme cinco punto dos"), (r"\bMETR\b", "Míter"), (r"\bRedwood Research\b", "Réduud Ríserch"),
    (r"\bsoftware\b", "sóftuer"), (r"\bhackear\b", "jaquear"), (r"\bhackers\b", "jákers"), (r"\bhackeo\b", "jaqueo"),
    (r"\bLas Vegas\b", "Las Végas"), (r"\bUnited Airlines\b", "Iunáited Érlains"), (r"\bUnited\b", "Iunáited"),
    (r"\b1986\b", "mil novecientos ochenta y seis"), (r"15\.000 millones", "quince mil millones"), (r"\b44\b", "cuarenta y cuatro"),
    (r"\b96\b", "noventa y seis"), (r"\b78\b", "setenta y ocho"), (r"\b3D\b", "tres dé"), (r"\bClaude\b", "Clod"), (r"\bAnthropic\b", "Antrópic"),
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
