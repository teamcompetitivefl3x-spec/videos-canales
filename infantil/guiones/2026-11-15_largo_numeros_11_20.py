# Episodio infantil: "¡Contamos del 11 al 20 con Tula y Pipo!" (largo, 2026-11-15)
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
WORDS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
         "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte"]
TITLE = ("¡CONTAMOS", "DEL 11 AL 20!")
THUMB = {"lines": ("¡DEL 11", "AL 20!"), "objs": ["N_11", "N_15", "N_20"], "x": (700, 1360), "y": 640, "size": 250}

def E(who=None, text=None, pause=0.35, do=None, chap=None):
    e = dict(who=who, text=text, pause=pause, do=do or [])
    if chap: e["chap"] = chap
    return e

def other(w): return "tula" if w == "pipo" else "pipo"
def cap(s): return s[0].upper() + s[1:]

# objeto: (singular, plural, femenino)
NOUN = {"estrella": ("estrella", "estrellas", True), "globo": ("globo", "globos", False), "pez": ("pez", "peces", False),
        "manzana": ("manzana", "manzanas", True), "flor": ("flor", "flores", True), "pelota": ("pelota", "pelotas", True),
        "fresa": ("fresa", "fresas", True), "sol": ("sol", "soles", False), "corazon": ("corazón", "corazones", False),
        "pato": ("patito", "patitos", False), "naranja": ("naranja", "naranjas", True), "pera": ("pera", "peras", True)}

INTRO = [
    E(None, None, pause=4.5, do=[("scene", "title")], chap="Hola, Tula y Pipo"),
    E("tula", "¡Hola, amiguitos! Soy Tula, la tortuga.", do=[("scene", "hello")]),
    E("pipo", "¡Y yo soy Pipo, el pajarito! ¡Pío, pío!"),
    E("pipo", "Tula, yo ya sé contar hasta diez. ¿Hay números más grandes?"),
    E("tula", "¡Claro que sí! Hoy vamos a contar del once al veinte.", pause=0.6,
      do=[("scene", "card", "¡DEL 11 AL 20!", "orange", ["N_11", "N_15", "N_20"])]),
    E("pipo", "¡Del once al veinte! ¡Qué emoción!", pause=0.6),
    E("tula", "Primero, calentemos. Contemos hasta diez con los deditos.", pause=0.5,
      do=[("scene", "review20", 10)], chap="Calentamos: del 1 al 10"),
]
for i in range(1, 11):
    INTRO.append(E("pipo" if i % 2 else "tula", cap(WORDS[i]) + ".", pause=0.45, do=[("rpop", i)]))
INTRO += [E("tula", "¡Diez! ¡Las dos manos llenas! ¡Muy bien!", pause=0.6, do=[("confetti", 1)]),
          E("pipo", "¿Y qué viene después del diez? ¡Vamos a descubrirlo!", pause=0.8)]

# (número, objeto, quién presenta)
TEEN = [(11, "estrella", "tula"), (12, "globo", "pipo"), (13, "pez", "tula"), (14, "manzana", "pipo"), (15, "flor", "tula"),
        (16, "pelota", "pipo"), (17, "fresa", "tula"), (18, "sol", "pipo"), (19, "corazon", "tula"), (20, "pato", "pipo")]

def teen_segment(n, ok, who, chap=None):
    s, pl, fem = NOUN[ok]; o = other(who); k = n - 10
    un = "una" if fem else "un"; cuantos = "Cuántas" if fem else "Cuántos"
    if n == 11:
        first = E(who, f"Aquí hay diez {pl}. ¡La cajita está llena!", pause=0.6)
    else:
        first = E(who, f"Aquí hay {WORDS[n - 1]} {pl}. Diez en la cajita llena… y {WORDS[k - 1]} al lado.", pause=0.6)
    ev = [E(None, None, pause=0.7, do=[("scene", "teens", n, ok, n - 1)], chap=chap), first,
          E(o, f"¡Y llega {un} {s} más!", pause=0.6, do=[("pop", n)]),
          E(who, f"¿{cuantos} {pl} hay ahora?", pause=3.0, do=[("qmark", 1)]),
          E(o, f"¡{cap(WORDS[n])}! ¡Hay {WORDS[n]} {pl}!", pause=0.7, do=[("qmark", 0), ("numeral", n)])]
    if n == 20:
        ev.append(E(who, "Veinte es diez y diez. ¡Dos cajitas llenas!", pause=0.6, do=[("reveal", 1), ("confetti", 1)]))
    else:
        ev.append(E(who, f"{cap(WORDS[n])} es diez y {WORDS[k]}.", pause=0.6, do=[("reveal", 1)]))
    ev.append(E(o, f"Repite conmigo: ¡{WORDS[n]}!", pause=2.0))
    if n in (11, 15, 20):
        ev.append(E(who, f"¡Otra vez, más fuerte! ¡{cap(WORDS[n])}!", pause=2.0))
    return ev

def dance(intro_who, intro, chap):
    return [E(None, None, pause=0.6, do=[("scene", "dance")], chap=chap), E(intro_who, intro, pause=15.0, do=[("dancing", 1)])]

QUIZ = [E(None, None, pause=1.0, do=[("scene", "card", "¿CUÁNTOS HAY?", "cyan")], chap="Juego: ¿cuántos hay?"),
        E("tula", "¡A jugar! Mira bien y dime cuántos hay.", pause=0.5),
        E("pipo", "Un truco: la cajita llena tiene diez. ¡Después cuenta los que sobran!", pause=0.8)]
for n, ok, who in ((13, "pato", "pipo"), (16, "fresa", "tula"), (12, "naranja", "pipo"), (18, "pez", "tula"), (15, "pera", "pipo")):
    s, pl, fem = NOUN[ok]; k = n - 10
    QUIZ += [E(None, None, pause=0.6, do=[("scene", "teens", n, ok, 0)]),
             E(who, f"¿{'Cuántas' if fem else 'Cuántos'} {pl} hay?", pause=3.8, do=[("qmark", 1), ("popall", 1)]),
             E(other(who), f"Diez… y {WORDS[k]} más. ¡{cap(WORDS[n])} {pl}!", pause=0.9, do=[("qmark", 0), ("numeral", n), ("reveal", 1)])]
QUIZ.append(E("tula", "¡Excelente! ¡Cuentas como un campeón!", pause=0.6))

NUMQ = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ NÚMERO ES?", "green")], chap="Juego: ¿qué número es?"),
        E("pipo", "¡Ahora te muestro un número y tú me dices cuál es!", pause=0.6)]
for n, who, ok in ((14, "pipo", "manzana"), (17, "tula", "estrella"), (12, "pipo", "globo"), (19, "tula", "corazon"), (16, "pipo", "pelota")):
    NUMQ += [E(None, None, pause=0.6, do=[("scene", "numq", n, ok)]),
             E(who, "¿Qué número es este?", pause=3.4, do=[("qmark", 1)]),
             E(other(who), f"¡Es el {WORDS[n]}! Un uno… y un {WORDS[n - 10]}.", pause=1.0, do=[("qmark", 0), ("reveal", 1)])]
NUMQ.append(E("pipo", "¡Bravo! ¡Ya reconoces los números grandes!", pause=0.6))

MISS = [E(None, None, pause=1.0, do=[("scene", "card", "¿QUÉ NÚMERO FALTA?", "purple")], chap="Juego: ¿qué número falta?"),
        E("pipo", "¡Oh, no! ¡Un número se escondió!"),
        E("tula", "Contemos en orden y descubramos cuál falta.", pause=0.6)]
for seq, miss, who in (([11, 12, 13, 14, 15], 2, "tula"), ([15, 16, 17, 18, 19], 3, "pipo"), ([16, 17, 18, 19, 20], 1, "tula"), ([12, 13, 14, 15, 16], 4, "pipo")):
    said = ", ".join(cap(WORDS[v]) if i == 0 else WORDS[v] for i, v in enumerate(seq[:miss]))
    rest = ", ".join(WORDS[v] for v in seq[miss + 1:])
    q = f"{said}… y luego {rest}. ¿Qué número falta?" if rest else f"{said}… y después, ¿qué viene?"
    MISS += [E(None, None, pause=0.6, do=[("scene", "missing", seq, miss)]),
             E(who, q, pause=3.6, do=[("qmark", 1)]),
             E(other(who), f"¡El {WORDS[seq[miss]]}! " + ", ".join(cap(WORDS[v]) if i == 0 else WORDS[v] for i, v in enumerate(seq)) + ".",
               pause=1.0, do=[("qmark", 0), ("fill", 1)])]

REVIEW = [E(None, None, pause=1.0, do=[("scene", "review20", 20)], chap="Contamos del 1 al 20"),
          E("tula", "¡Ahora el gran final! Contemos del uno al veinte, todos juntos. ¡Puedes saltar con cada número!", pause=0.8)]
for i in range(1, 21):
    REVIEW.append(E("tula" if i % 2 else "pipo", cap(WORDS[i]) + ".", pause=0.5, do=[("rpop", i)]))
REVIEW += [E("pipo", "¡Veinte! ¡Lo logramos!", pause=0.6, do=[("confetti", 1)]),
           E("tula", "¡Bravo! ¡Ya sabes contar hasta veinte!", pause=2.5)]

OUTRO = [
    E(None, None, pause=0.6, do=[("scene", "bye")], chap="Despedida"),
    E("tula", "¡Lo hiciste muy, muy bien, amiguito!"),
    E("pipo", "¿Cuál es tu número favorito? ¡El mío es el doce, como los globos!", pause=2.5),
    E("tula", "Hoy, cuenta tus juguetes en casa. ¿Llegas hasta veinte? Nos vemos en el próximo video. ¡Adiós!"),
    E("pipo", "¡Chau, chau! ¡Pío, pío!", pause=1.0),
    E(None, None, pause=8.0, do=[("scene", "end")]),
]

def build():
    ev = list(INTRO)
    for i, (n, ok, who) in enumerate(TEEN[:5]):
        ev += teen_segment(n, ok, who, "Del 11 al 15" if i == 0 else None)
    ev += dance("pipo", "¡Ya llegamos al quince! ¡Hagamos una pausa para bailar!", "Pausa para bailar")
    for i, (n, ok, who) in enumerate(TEEN[5:]):
        ev += teen_segment(n, ok, who, "Del 16 al 20" if i == 0 else None)
    ev += QUIZ + NUMQ + dance("tula", "¡Muy bien! ¡A bailar otra vez!", "¡A bailar otra vez!") + MISS + REVIEW + OUTRO
    return ev

if __name__ == "__main__":
    ev = build(); words = sum(len(e["text"].split()) for e in ev if e["text"])
    print(len(ev), "eventos,", words, "palabras,", round(sum(e["pause"] for e in ev), 1), "s de pausas")
    for e in ev:
        if e["text"]: print(e["who"], "|", e["text"])
