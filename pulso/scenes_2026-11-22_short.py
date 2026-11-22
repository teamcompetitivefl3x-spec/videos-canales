# Pulso IA · Short: Signal bloquea capturas por la IA del teléfono (20 nov. 2026). "at" = índice de frase.
CHAPTERS = ["SHORT"]

SCENES = [
 dict(at=0, type="headline", icon="cross", icon_col="red", kicker="SIGNAL", text="Bloqueó las *capturas de pantalla*", size=100),
 dict(at=1, type="headline", text="¿El *motivo*?", size=150),
 dict(at=2, type="headline", icon="robot", icon_col="red", text="La *IA* de tu propio teléfono", size=100),
 dict(at=3, type="headline", kicker="20 DE NOVIEMBRE · 2026", text="Capturas limitadas en *Android* y *iPhone*", size=90),
 dict(at=4, type="chat", title="Asistente con IA · recreación", msgs=[("user", "¿Qué hay en mi pantalla?"), ("bot", "Veo tu chat. Te resumo los mensajes…")], stagger=1.6),
 dict(at=5, type="headline", icon="warning", icon_col="red", text="Incluidos tus chats *cifrados*", size=100),
 dict(at=6, type="quote", text="Una *amenaza existencial* para Signal.", author="Meredith Whittaker, presidenta de Signal (traducción)", size=72),
 dict(at=7, type="compare", title="No es la primera vez", left=("2025", "Windows", "blue"), right=("2026", "Android e iPhone", "accent"), stagger=1.8),
 dict(at=8, type="headline", icon="check", icon_col="teal", text="Se puede *desactivar*…", sub="…pero Signal advierte que pierdes su garantía de privacidad", size=96),
 dict(at=9, type="headline", icon="warning", icon_col="red", text="Y admite que *no alcanza*", sub="la IA podría llegar a tus datos por otros caminos", size=96),
 dict(at=10, type="stats", title="LO QUE PIDE SIGNAL", cards=[("Apple", "iPhone y Mac", "blue"), ("Google", "Android", "teal"), ("Microsoft", "Windows", "accent")], stagger=0.7),
 dict(at=11, type="headline", text="Más en *Pulso IA*", size=120),
]

SHORTS = [
 dict(name="short_signal", title="Signal vs. la IA del teléfono", sents=list(range(12)),
      end_text="Suscríbete a *Pulso IA*", end_button="SUSCRÍBETE"),
]
