# Episodio infantil: "¡Aprendemos las vocales con Tula y Pipo!" (largo, 2026-11-11)
# Cada evento: who (tula/pipo/None), text, pause (silencio después, en s), do (acciones visuales), chap (capítulo opcional)
OBJS = {
    1: ("sol", "sol", "soles", "amarillo", "amarillos"),
    2: ("pez", "pez", "peces", "naranja", "naranjas"),
    3: ("globo", "globo", "globos", "rojo", "rojos"),
    4: ("manzana", "manzana", "manzanas", "verde", "verdes"),
    5: ("estrella", "estrella", "estrellas", "morada", "moradas"),
    6: ("flor", "flor", "flores", "rosada", "rosadas"),
    7: ("burbuja", "burbuja", "burbujas", "celeste", "celestes"),
    8: ("pelota", "pelota", "pelotas", "azul", "azules"),
    9: ("nube", "nube", "nubes", "blanca", "blancas"),
    10: ("corazon", "corazón", "corazones", "de colores", "de colores"),
}
WORDS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez"]
TITLE = ("¡APRENDEMOS", "LAS VOCALES!")
THUMB = {"lines": ("¡LAS", "VOCALES!"), "objs": ["L_A", "L_E", "L_I", "L_O", "L_U"]}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, ¿qué vamos a aprender hoy?"),
    E("tula", "¡Hoy vamos a conocer las vocales! Son cinco letras muy especiales.", do=[("scene", "card", "¡LAS VOCALES!", "orange", ["L_A", "L_E", "L_I", "L_O", "L_U"])]),
    E("pipo", "¡Cinco letras! A, E, I, O, U.", pause=0.6),
    E("tula", "Mira, escucha y repite en voz alta. ¿Listo? ¡Vamos!", pause=0.8),
]

# (vocal, quién la presenta, pista de la boca, [(objeto, PALABRA, "artículo palabra", dato, quién pregunta)], conteo (n, objeto, plural) | None)
VOW = [
    ("A", "tula", "Para decir A, abre la boca bien grande, así.",
     [("abeja", "ABEJA", "la abeja", "¡Bzzz, bzzz! La abeja vuela de flor en flor.", "pipo"),
      ("arbol", "ÁRBOL", "el árbol", "El árbol es alto y tiene muchas hojas verdes.", "tula")],
     (3, "abeja", "abejas")),
    ("E", "pipo", "Para decir E, estira la boquita, como una sonrisa.",
     [("elefante", "ELEFANTE", "el elefante", "El elefante es muy grande y tiene una trompa larga.", "tula"),
      ("estrella", "ESTRELLA", "la estrella", "La estrella brilla en el cielo de noche.", "pipo")],
     (4, "estrella", "estrellas")),
    ("I", "tula", "Para decir I, sonríe mucho, mucho, y muestra los dientes.",
     [("iglu", "IGLÚ", "el iglú", "El iglú es una casita hecha de nieve, donde hace mucho frío.", "pipo"),
      ("isla", "ISLA", "la isla", "La isla es un pedacito de tierra con agua alrededor.", "tula")],
     None),
    ("O", "pipo", "Para decir O, pon la boca redonda, como una pelotita.",
     [("oso", "OSO", "el oso", "El oso es grandote, peludito, y le encanta la miel.", "tula"),
      ("oveja", "OVEJA", "la oveja", "La oveja tiene lana muy suave y dice ¡beee!", "pipo")],
     (5, "oveja", "ovejas")),
    ("U", "tula", "Para decir U, pon la boca como para dar un besito.",
     [("uvas", "UVAS", "las uvas", "Las uvas son pequeñas, redondas y muy dulces.", "pipo"),
      ("uno", "UNO", "el uno", "¡Uno! Como el número uno. Levanta un dedito.", "tula")],
     None),
]
ORD = {"A": "primera", "E": "segunda", "I": "tercera", "O": "cuarta", "U": "quinta"}

def other(w): return "tula" if w == "pipo" else "pipo"

def vowel_segment(v):
    ch, who, mouth, words, cnt = v; o = other(who)
    ev = [E(None, None, pause=0.8, do=[("scene", "letter", ch)], chap=f"La letra {ch}"),
          E(who, f"La {ORD[ch]} vocal es… ¡la {ch}!", pause=0.6),
          E(o, f"Esta es la {ch} grande.", pause=0.4),
          E(who, f"Y esta es la {ch} pequeñita.", pause=0.6, do=[("pop", 2)]),
          E(o, mouth, pause=0.5),
          E(who, f"Ahora tú. Dilo fuerte: ¡{ch}!", pause=2.0),
          E(o, f"¡Otra vez! ¡{ch}, {ch}, {ch}!", pause=2.2)]
    for k, (ok, WD, art, fact, asker) in enumerate(words):
        word = art.split(" ", 1)[1]; ans = other(asker)
        ev += [E(None, None, pause=0.6, do=[("scene", "word", ok, WD, ch)]),
               E(asker, "¿Qué es esto?" if k == 0 else "¿Y esto qué es?", pause=3.0, do=[("qmark", 1)]),
               E(ans, f"¡Es {art}!", pause=0.7, do=[("qmark", 0), ("reveal", 1)]),
               E(asker, f"{word.capitalize()} empieza con {ch}. ¡{ch}, {word}!", pause=0.5),
               E(ans, fact, pause=0.6),
               E(asker, f"Repite conmigo: ¡{word}!", pause=2.0)]
    if cnt:
        n, ok, pl = cnt; c = who
        ev.append(E(None, None, pause=0.8, do=[("scene", "count", n, ok)]))
        ev.append(E(c, f"¡Contemos {pl}! ¡Cuenta conmigo!", pause=0.5))
        for i in range(1, n + 1):
            ev.append(E(c, WORDS[i].capitalize() + ".", pause=0.6, do=[("pop", i)]))
        ev.append(E(o, f"¡{WORDS[n].capitalize()} {pl}!", pause=0.8, do=[("numeral", n)]))
    return ev

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

START = [E(None, None, pause=1.0, do=[("scene", "card", "¿CON QUÉ VOCAL EMPIEZA?", "yellow")], chap="Juego: ¿con qué vocal empieza?"),
         E("tula", "¡Juguemos! Te muestro un dibujo y tú me dices con qué vocal empieza.", pause=0.6),
         E("pipo", "¡Escucha bien la primera letra! ¡Pío!", pause=0.6)]
for ok, WD, art, ch, who in (("oso", "OSO", "oso", "O", "pipo"), ("abeja", "ABEJA", "abeja", "A", "tula"),
                             ("elefante", "ELEFANTE", "elefante", "E", "pipo"), ("uvas", "UVAS", "uvas", "U", "tula"),
                             ("iglu", "IGLÚ", "iglú", "I", "pipo")):
    START += [E(None, None, pause=0.8, do=[("scene", "vstart", ok, WD, ch)]),
              E(who, f"¿Con qué vocal empieza {art}?", pause=3.4, do=[("qmark", 1)]),
              E(other(who), f"¡Con la {ch}! {ch}, {art}.", pause=1.0, do=[("qmark", 0), ("reveal", 1)])]
START.append(E("tula", "¡Muy bien! ¡Eres un campeón de las vocales!", pause=0.6, do=[("confetti", 1)]))

FIND = [E(None, None, pause=1.0, do=[("scene", "card", "¡ENCUENTRA LA VOCAL!", "pink")], chap="Juego: encuentra la vocal"),
        E("pipo", "¡Ahora vamos a buscar vocales! Señálala con tu dedito.", pause=0.6)]
for seq, idx, ch, who in ((["E", "O", "A"], 2, "A", "pipo"), (["U", "I", "E"], 1, "I", "tula"),
                          (["O", "A", "U"], 0, "O", "pipo"), (["A", "E", "U"], 2, "U", "tula"),
                          (["I", "E", "O"], 1, "E", "pipo")):
    FIND += [E(None, None, pause=0.6, do=[("scene", "lfind", seq, idx, ch)]),
             E(who, f"¿Dónde está la {ch}?", pause=3.4, do=[("qmark", 1)]),
             E(other(who), f"¡Aquí está! ¡La {ch}!", pause=1.0, do=[("qmark", 0), ("reveal", 1)])]

PL = {"oso": "osos", "elefante": "elefantes", "abeja": "abejas", "arbol": "árboles"}
MASC = {"oso", "elefante", "arbol"}
QUIZ = [E(None, None, pause=1.2, do=[("scene", "quiz_intro")], chap="Juego: ¿cuántos hay?"),
        E("tula", "¡Otro juego! Mira bien y dime cuántos hay.", pause=0.8)]
for n, ok, who in ((2, "oso", "pipo"), (4, "abeja", "tula"), (3, "elefante", "pipo"), (6, "arbol", "tula")):
    pl = PL[ok]
    QUIZ += [E(None, None, pause=0.8, do=[("scene", "quiz", n, ok)]),
             E(who, f"¿Cuántos {pl} hay?" if ok in MASC else f"¿Cuántas {pl} hay?", pause=3.6, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), f"¡{WORDS[n].capitalize()}! ¡Hay {WORDS[n]} {pl}!", pause=0.9, do=[("qmark", 0), ("numeral", n)])]

MISS = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ VOCAL FALTA?", "purple")], chap="Juego: ¿qué vocal falta?"),
        E("pipo", "¡Oh, no! ¡Una vocal se escondió!"),
        E("tula", "Digamos las vocales en orden y descubramos cuál falta.", pause=0.6)]
for miss, who in ((2, "tula"), (4, "pipo"), (1, "tula")):
    seq = ["A", "E", "I", "O", "U"]; ch = seq[miss]
    said = ", ".join(seq[:miss] + ["…"] + seq[miss + 1:]) if miss < 4 else ", ".join(seq[:4]) + "…"
    MISS += [E(None, None, pause=0.6, do=[("scene", "lpattern", seq, miss)]),
             E(who, f"{said} ¿Qué vocal falta?", pause=3.6, do=[("qmark", 1)]),
             E(other(who), f"¡La {ch}! A, E, I, O, U.", pause=1.0, do=[("qmark", 0), ("fill", 1)])]

REV_IT = [("A", "abeja", "ABEJA"), ("E", "elefante", "ELEFANTE"), ("I", "iglu", "IGLÚ"), ("O", "oso", "OSO"), ("U", "uvas", "UVAS")]
REVIEW = [E(None, None, pause=1.0, do=[("scene", "lreview", REV_IT)], chap="Repaso de las vocales"),
          E("tula", "¡Repasemos todas las vocales! Dilas conmigo.", pause=0.6)]
for i, (ch, ok, wd) in enumerate(REV_IT, 1):
    REVIEW.append(E("tula" if i % 2 else "pipo", f"¡{ch}, de {wd.lower()}!", pause=1.0, do=[("rpop", i)]))
REVIEW += [E("pipo", "¡Ahora más rápido! A, E, I, O, U.", pause=1.6),
           E("tula", "¡Bravo! ¡Te sabes las cinco vocales!", pause=2.5, do=[("confetti", 1)])]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "¿Cuál es tu vocal favorita? ¡La mía es la O, de oso!", pause=2.5),
    E("tula", "Hoy, busca en tu casa cosas que empiecen con A, E, I, O, U. Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    for v in VOW[:3]:
        ev += vowel_segment(v)
    ev += dance("pipo", "¡Ya conocemos tres vocales! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    for v in VOW[3:]:
        ev += vowel_segment(v)
    ev += START + QUIZ + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + FIND + MISS + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
    for e in ev:
        if e["text"]: print(e["who"], "|", e["text"])
